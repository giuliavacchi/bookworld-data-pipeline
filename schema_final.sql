-- BOOKWORLD - SCHEMA FINAL


-- =========================================================
-- SALES
-- RGPD: customer_first_name and customer_last_name
-- are not retained because they are not necessary
-- for the final analysis.


CREATE TABLE IF NOT EXISTS sales (
    order_id TEXT PRIMARY KEY,
    order_date DATE,
    book_id TEXT,
    book_name TEXT,
    category_name TEXT,
    country_code TEXT,
    channel_code TEXT,
    quantity INTEGER,
    discount_rate REAL,
    price_gbp REAL,
    price_eur REAL,
    revenue_gbp REAL,
    revenue_eur REAL,
    acquisition_cost_gbp REAL,
    acquisition_cost_eur REAL,

    FOREIGN KEY (country_code)
        REFERENCES countries(country_code),

    FOREIGN KEY (channel_code)
        REFERENCES channels(channel_code),

    FOREIGN KEY (category_name)
        REFERENCES category_rules(category_name)
);


-- =========================================================
-- REFERENCE TABLES


CREATE TABLE IF NOT EXISTS countries (
    country_code TEXT PRIMARY KEY,
    country_name TEXT,
    currency_code TEXT,
    vat_rate REAL,
    region TEXT,
    is_active INTEGER
);


CREATE TABLE IF NOT EXISTS channels (
    channel_code TEXT PRIMARY KEY,
    channel_name TEXT,
    acquisition_cost_gbp REAL,
    acquisition_cost_eur REAL,
    channel_group TEXT,
    is_active INTEGER
);


CREATE TABLE IF NOT EXISTS category_rules (
    category_name TEXT PRIMARY KEY,
    margin_rate REAL,
    strategic_flag INTEGER,
    default_channel_code TEXT,
    is_active INTEGER
);


-- =========================================================
-- AGGREGATED TABLES


CREATE TABLE IF NOT EXISTS sales_by_country (
    country_code TEXT,
    country_name TEXT,
    total_orders INTEGER,
    total_quantity INTEGER,
    total_revenue_gbp REAL,
    total_revenue_eur REAL,
    total_acquisition_cost_gbp REAL,
    total_acquisition_cost_eur REAL,
    mean_discount_rate REAL,
    average_order_value_eur REAL,
    revenue_per_book_eur REAL,
    acquisition_cost_per_order_eur REAL,
    acquisition_cost_ratio REAL
);


CREATE TABLE IF NOT EXISTS sales_by_country_month (
    order_month TEXT,
    country_code TEXT,
    country_name TEXT,
    total_orders INTEGER,
    total_quantity INTEGER,
    total_revenue_gbp REAL,
    total_revenue_eur REAL
);


CREATE TABLE IF NOT EXISTS sales_by_country_channel (
    country_code TEXT,
    country_name TEXT,
    channel_code TEXT,
    channel_name TEXT,
    channel_group TEXT,
    total_orders INTEGER,
    total_quantity INTEGER,
    total_revenue_gbp REAL,
    total_revenue_eur REAL,
    total_acquisition_cost_gbp REAL,
    total_acquisition_cost_eur REAL,
    mean_discount_rate REAL
);


CREATE TABLE IF NOT EXISTS sales_by_country_category (
    country_code TEXT,
    country_name TEXT,
    category_name TEXT,
    total_orders INTEGER,
    total_quantity INTEGER,
    total_revenue_gbp REAL,
    total_revenue_eur REAL,
    mean_discount_rate REAL
);


CREATE TABLE IF NOT EXISTS sales_by_country_channel_group (
    country_code TEXT,
    country_name TEXT,
    channel_group TEXT,
    total_orders INTEGER,
    total_quantity INTEGER,
    total_revenue_gbp REAL,
    total_revenue_eur REAL,
    total_acquisition_cost_gbp REAL,
    total_acquisition_cost_eur REAL,
    mean_discount_rate REAL
);