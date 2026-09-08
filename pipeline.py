import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup

# =========================
# DATABASE
# =========================

def init_database():
    conn = sqlite3.connect("bookworld_reference.db")
    return conn

# =========================
# EXTRACT
# =========================

def extract(conn):

    data = {}

    # CSV
    data["sales"] = pd.read_csv("sales_raw.csv")


    #SQLite
    data["channels"] = pd.read_sql_query(
        """
        SELECT
            channel_code,
            channel_name,
            acquisition_cost_gbp,
            channel_group,
            is_active
        FROM channels
        """,
        conn
    )

    data["countries"] = pd.read_sql_query(
        """
        SELECT
            country_code,
            country_name,
            currency_code,
            vat_rate,
            region,
            is_active
        FROM countries
        """,
        conn
    )


    data["category_rules"] = pd.read_sql_query(
        """
        SELECT
            category_name,
            margin_rate,
            strategic_flag,
            default_channel_code,
            is_active
        FROM category_rules
        """,
        conn
    )
    

    # Web scraping
    url = "https://books.toscrape.com/"
    try:
        response = requests.get(url, timeout=15)

        books_list = []

        if response.status_code == 200:

            soup = BeautifulSoup(response.text, "html.parser")

            books = soup.select("article.product_pod")
        

            base_url = "https://books.toscrape.com/"

            for book in books:

                title = book.select_one("h3 a")["title"]
                price = book.select_one(".price_color").get_text(strip=True)
                link = book.select_one("h3 a")["href"]

                detail_url = base_url + link

                detail_response = requests.get(detail_url, timeout=15)
       
                if detail_response.status_code == 200:

                    detail_soup = BeautifulSoup(
                        detail_response.text,
                        "html.parser"
                    )

                    breadcrumb = detail_soup.select("ul.breadcrumb li")
                    category = breadcrumb[2].get_text(strip=True)

                else:

                    print("Erreur page détail :", detail_response.status_code)
                    category = None

                books_list.append({
                    "book_name": title,
                    "price_gbp": price,
                    "category_name": category
                })


        else:

            print("Erreur scraping :", response.status_code)

    except requests.RequestException as e:
        print("Erreur scraping :", e)

    data["books"] = books_list




    # Frankfurter API

    url = "https://api.frankfurter.dev/v2/rate/GBP/EUR"

    try:
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            exchange_data = response.json()
            data["exchange_rate"] = exchange_data["rate"]
        else:
            print("Erreur Frankfurter :", response.status_code)
            data["exchange_rate"] = None
    
    except requests.RequestException as e:
        print("Erreur Frankfurter :", e)
        data["exchange_rate"] = None


    return data

# =========================
# TRANSFORM
# =========================

def transform(data):

    if data["exchange_rate"] is None:
        raise ValueError(
            "Taux de change indisponible : transformation impossible."
        )


    #==== NETTOYAGE =====

    # 1. Conversion de la date
    data["sales"]["order_date"] = pd.to_datetime(
        data["sales"]["order_date"]
    )


    # 2. Conversion du catalogue en DataFrame
    books_df = pd.DataFrame(data["books"])


    # 3. Nettoyage du prix GBP

    books_df["price_gbp"] = (
        books_df["price_gbp"]
        .str.replace("Â£", "", regex=False)
        .astype(float)
    )


    # 4. Conversion GBP → EUR
    books_df["price_eur"] = (
        books_df["price_gbp"] * data["exchange_rate"]
    ).round(2)
   

    
    #==== ENRICHISSEMENT =====

    # 1. Sales + Books
    sales_books_df = data["sales"].merge(
        books_df,
        on="book_name",
        how="left"
    )


    # 7. Sales + Channels
    sales_channels_df = sales_books_df.merge(
        data["channels"],
        on="channel_code",
        how="left"
    )

    # Conversion du coût d'acquisition GBP → EUR
    sales_channels_df["acquisition_cost_eur"] = (
        sales_channels_df["acquisition_cost_gbp"]
        * data["exchange_rate"]
    ).round(2)

    # Préparation table channels_sql

    channels_sql = data["channels"].copy()

    channels_sql["acquisition_cost_eur"] = (
        channels_sql["acquisition_cost_gbp"]
        * data["exchange_rate"]
    ).round(2)

    
    # 8. Sales + Countries
    sales_countries_df = sales_channels_df.merge(
        data["countries"],
        on="country_code",
        how="left"
    )

    sales_countries_df = sales_countries_df.rename(
        columns={
            "is_active_x": "is_active_channel",
            "is_active_y": "is_active_country"
        }
    )



    # Country missing from reference : Enrichissement de NL
    nl_mask = sales_countries_df["country_code"] == "NL"

    sales_countries_df.loc[nl_mask, "country_name"] = "Netherlands"
    sales_countries_df.loc[nl_mask, "currency_code"] = "EUR"
    sales_countries_df.loc[nl_mask, "vat_rate"] = 21.0
    sales_countries_df.loc[nl_mask, "region"] = "Europe"

    # Préparation table countries_sql
    countries_sql = data["countries"].copy()

    nl_data = pd.DataFrame([{
        "country_code": "NL",
        "country_name": "Netherlands",
        "currency_code": "EUR",
        "vat_rate": 21.0,
        "region": "Europe",
        "is_active": None
    }])

    countries_sql = pd.concat(
        [countries_sql, nl_data],
        ignore_index=True
    )


    # 9. Sales + Category rules
    sales_final_df = sales_countries_df.merge(
        data["category_rules"],
        on="category_name",
        how="left",
    )

    sales_final_df = sales_final_df.rename(
        columns={
            "is_active": "is_active_category"
        }
    )
    

    #==== ANALYSE =====

    # Creation colonnes revenue
    sales_final_df["revenue_gbp"] = (
        sales_final_df["price_gbp"]
        * sales_final_df["quantity"]
        * (1 - sales_final_df["discount_rate"])
    ).round(2)

    sales_final_df["revenue_eur"] = (
        sales_final_df["price_eur"]
        * sales_final_df["quantity"]
        * (1 - sales_final_df["discount_rate"])
    ).round(2)

    #==== Agregations =====

    # 1. Sales x country
    sales_by_country = (
        sales_final_df
        .groupby(
            ["country_code", "country_name"],
            as_index=False
        )
        .agg(
            total_orders=("order_id", "nunique"),
            total_quantity=("quantity", "sum"),
            total_revenue_gbp=("revenue_gbp", "sum"),
            total_revenue_eur=("revenue_eur", "sum"),
            total_acquisition_cost_gbp=("acquisition_cost_gbp", "sum"),
            total_acquisition_cost_eur=("acquisition_cost_eur", "sum"),
            mean_discount_rate=("discount_rate", "mean")
        )
    )

    sales_by_country["mean_discount_rate"] = (
        sales_by_country["mean_discount_rate"].round(4)
    )


    # 2. Sales x country x month
    sales_final_df["order_month"] = (
        sales_final_df["order_date"]
        .dt.to_period("M")
        .astype(str)
    )

    sales_by_country_month = (
        sales_final_df
        .groupby(
            ["order_month", "country_code", "country_name"],
            as_index=False
        )
        .agg(
            total_orders=("order_id", "nunique"),
            total_quantity=("quantity", "sum"),
            total_revenue_gbp=("revenue_gbp", "sum"),
            total_revenue_eur=("revenue_eur", "sum")
        )
    )


    # 3. Sales x category

    sales_by_country_category = (
        sales_final_df
        .groupby(
            [
                "country_code",
                "country_name",
                "category_name"
            ],
            as_index=False
        )
        .agg(
            total_orders=("order_id", "nunique"),
            total_quantity=("quantity", "sum"),
            total_revenue_gbp=("revenue_gbp", "sum"),
            total_revenue_eur=("revenue_eur", "sum"),
            mean_discount_rate=("discount_rate", "mean")
        )
    )

    # 4. Sales x channel

    sales_by_country_channel = (
        sales_final_df
        .groupby(
            [
                "country_code",
                "country_name",
                "channel_code",
                "channel_name",
                "channel_group"
            ],
            as_index=False
        )
        .agg(
            total_orders=("order_id", "nunique"),
            total_quantity=("quantity", "sum"),
            total_revenue_gbp=("revenue_gbp", "sum"),
            total_revenue_eur=("revenue_eur", "sum"),
            total_acquisition_cost_gbp=("acquisition_cost_gbp", "sum"),
            total_acquisition_cost_eur=("acquisition_cost_eur", "sum"),
            mean_discount_rate=("discount_rate", "mean")
        )
    )
    
   

    # 5. Pays x channel group

    sales_by_country_channel_group = (
        sales_final_df
        .groupby(
            [
                "country_code",
                "country_name",
                "channel_group"
            ],
            as_index=False
        )
        .agg(
            total_orders=("order_id", "nunique"),
            total_quantity=("quantity", "sum"),
            total_revenue_gbp=("revenue_gbp", "sum"),
            total_revenue_eur=("revenue_eur", "sum"),
            total_acquisition_cost_gbp=("acquisition_cost_gbp", "sum"),
            total_acquisition_cost_eur=("acquisition_cost_eur", "sum"),
            mean_discount_rate=("discount_rate", "mean")
        )
    )


    # 6. Panier moyen

    sales_by_country["average_order_value_eur"] = (
        sales_by_country["total_revenue_eur"]
        / sales_by_country["total_orders"]
    ).round(2)


    # 7. Revenue par livre vendu
    sales_by_country["revenue_per_book_eur"] = (
        sales_by_country["total_revenue_eur"]
        / sales_by_country["total_quantity"]
    ).round(2)

    # 8. Cout d'acquisition moyen par commande
    sales_by_country["acquisition_cost_per_order_eur"] = (
        sales_by_country["total_acquisition_cost_eur"]
        / sales_by_country["total_orders"]
    ).round(2)

    sales_by_country["acquisition_cost_ratio"] = (
        sales_by_country["total_acquisition_cost_eur"]
        / sales_by_country["total_revenue_eur"]
    ).round(4)



    # 9. Total SALES
    total_sales = {
        "total_quantity": sales_final_df["quantity"].sum(),
        "total_transactions": sales_final_df["order_id"].nunique(),
        "total_revenue_eur": sales_final_df["revenue_eur"].sum()
    }

    total_sales["average_order_value_eur"] = (
        total_sales["total_revenue_eur"]
        / total_sales["total_transactions"]
    ).round(2)

    total_sales["average_quantity_per_transaction"] = (
        total_sales["total_quantity"]
        / total_sales["total_transactions"]
    ).round(2)


    #==== RGPD =====
    # Suppression des données personnelles non nécessaires
    sales_final_df = sales_final_df.drop(
        columns=["customer_first_name", "customer_last_name"]
    )


    #==== Preparation table sales_sql =====

    data["sales_sql"] = sales_final_df[[
        "order_id",
        "order_date",
        "book_id",
        "book_name",
        "category_name",
        "country_code",
        "channel_code",
        "quantity",
        "discount_rate",
        "price_gbp",
        "price_eur",
        "revenue_gbp",
        "revenue_eur",
        "acquisition_cost_gbp",
        "acquisition_cost_eur"
    ]]

    # 11. On conserve le résultat dans data["sales"]
    data["sales"] = sales_final_df
    data["countries_sql"] = countries_sql
    data["channels_sql"] = channels_sql
    data["sales_by_country"] = sales_by_country
    data["sales_by_country_month"] = sales_by_country_month
    data["sales_by_country_channel"] = sales_by_country_channel
    data["sales_by_country_category"] = sales_by_country_category
    data["total_sales"] = total_sales
    data["sales_by_country_channel_group"] = sales_by_country_channel_group



    return data

# =========================
# FINAL DATABASE
# =========================

def init_final_database():
    conn = sqlite3.connect("bookworld_final.db")

    with open("schema_final.sql", "r", encoding="utf-8") as file:
        schema = file.read()

    conn.executescript(schema)

    # Vérification de la création des tables
    tables = pd.read_sql_query(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        """,
        conn
    )

    print("Tables créées :", tables["name"].tolist())

    return conn

# =========================
# LOAD
# =========================

def load(data):

   #==== Base finale SQLite =====

    conn = init_final_database()

    # Nettoyage des tables
    conn.executescript("""
        DELETE FROM sales;
        DELETE FROM countries;
        DELETE FROM channels;
        DELETE FROM category_rules;
        DELETE FROM sales_by_country;
        DELETE FROM sales_by_country_month;
        DELETE FROM sales_by_country_channel;
        DELETE FROM sales_by_country_category;
        DELETE FROM sales_by_country_channel_group;
    """)

    # Sales
    data["sales_sql"].to_sql(
        "sales",
        conn,
        if_exists="append",
        index=False
    )

    # Référentiels
    data["countries_sql"].to_sql(
        "countries",
        conn,
        if_exists="append",
        index=False
    )

    data["channels_sql"].to_sql(
        "channels",
        conn,
        if_exists="append",
        index=False
    )

    data["category_rules"].to_sql(
        "category_rules",
        conn,
        if_exists="append",
        index=False
    )

    # Agrégations
    data["sales_by_country"].to_sql(
        "sales_by_country",
        conn,
        if_exists="append",
        index=False
    )

    data["sales_by_country_month"].to_sql(
        "sales_by_country_month",
        conn,
        if_exists="append",
        index=False
    )

    data["sales_by_country_channel"].to_sql(
        "sales_by_country_channel",
        conn,
        if_exists="append",
        index=False
    )

    data["sales_by_country_category"].to_sql(
        "sales_by_country_category",
        conn,
        if_exists="append",
        index=False
    )

    data["sales_by_country_channel_group"].to_sql(
        "sales_by_country_channel_group",
        conn,
        if_exists="append",
        index=False
    )

    # Vérification du chargement des données
    tables = [
        "sales",
        "countries",
        "channels",
        "category_rules",
        "sales_by_country",
        "sales_by_country_month",
        "sales_by_country_channel",
        "sales_by_country_category",
        "sales_by_country_channel_group"
    ]

    for table in tables:
        count = conn.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"{table} : {count} lignes")

    conn.close()

    print("Base finale SQLite créée avec succès.")

   #==== EXPORT CSV ===== 

    data["sales"].to_csv(
        "sales_final_df.csv", index=False
    )

    data["sales_sql"].to_csv(
        "sales_sql_df.csv", index=False
    )


    kpi_global = pd.DataFrame([data["total_sales"]])

    kpi_global.to_csv(
        "kpi_global.csv",
        index=False
    )

    data["sales_by_country"].to_csv(
        "sales_by_country.csv", index=False
    )

    data["sales_by_country_month"].to_csv(
        "sales_by_country_month.csv", index=False
    )
    data["sales_by_country_channel"].to_csv(
        "sales_by_country_channel.csv", index=False
    )

    data["sales_by_country_category"].to_csv(
        "sales_by_country_category.csv", index=False
    )

    data["sales_by_country_channel_group"].to_csv(
        "sales_by_country_channel_group.csv",
        index=False
   )

    print("Fichiers CSV exportés avec succès.")


# =========================
# MAIN
# =========================

def main():
    conn = init_database()
    data = extract(conn)
    conn.close()
    data = transform(data)
    load(data)


if __name__ == "__main__":
    main()