from flask import Flask, jsonify, request, abort
import sqlite3

app = Flask(__name__)

DATABASE = "bookworld_final.db"
API_KEY = "bookworld0897"



# DATABASE


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn



# AUTHENTICATION


@app.before_request
def check_key():

    if request.args.get("api-key") != API_KEY:
        abort(401)



# HEALTH


@app.route("/health", methods=["GET"])
def health():


    try:
        conn = get_db_connection()

        conn.execute("""
            SELECT 1
        """)

        conn.close()

        return jsonify({
            "status": "ok",
            "database": "connected"
        }), 200

    except sqlite3.Error:
        return jsonify({
            "status": "error",
            "database": "unavailable"
        }), 500

# SALES BY COUNTRY


@app.route("/sales-by-country", methods=["GET"])
def sales_by_country():

    try:
        conn = get_db_connection()

        rows = conn.execute("""
            SELECT *
            FROM sales_by_country
        """).fetchall()

        conn.close()

        return jsonify([dict(row) for row in rows]), 200

    except sqlite3.Error:
        return jsonify({
            "error": "Database error"
        }), 500

# SALES BY COUNTRY AND MONTH


@app.route("/sales-by-country-month", methods=["GET"])
def sales_by_country_month():

    try:
        conn = get_db_connection()

        rows = conn.execute("""
            SELECT *
            FROM sales_by_country_month
        """).fetchall()

        conn.close()

        return jsonify([dict(row) for row in rows]), 200

    except sqlite3.Error:
        return jsonify({
            "error": "Database error"
        }), 500


# SALES BY COUNTRY AND CHANNEL


@app.route("/sales-by-country-channel", methods=["GET"])
def sales_by_country_channel():

    try:
        conn = get_db_connection()

        rows = conn.execute("""
            SELECT *
            FROM sales_by_country_channel
        """).fetchall()

        conn.close()

        return jsonify([dict(row) for row in rows]), 200

    except sqlite3.Error:
        return jsonify({
            "error": "Database error"
        }), 500


# SALES BY COUNTRY AND CATEGORY


@app.route("/sales-by-country-category", methods=["GET"])
def sales_by_country_category():

    try:
        conn = get_db_connection()

        rows = conn.execute("""
            SELECT *
            FROM sales_by_country_category
        """).fetchall()

        conn.close()

        return jsonify([dict(row) for row in rows]), 200

    except sqlite3.Error:
        return jsonify({
            "error": "Database error"
        }), 500


# SALES BY COUNTRY AND CHANNEL GROUP


@app.route("/sales-by-country-channel-group", methods=["GET"])
def sales_by_country_channel_group():

    try:
        conn = get_db_connection()

        rows = conn.execute("""
            SELECT *
            FROM sales_by_country_channel_group
        """).fetchall()

        conn.close()

        return jsonify([dict(row) for row in rows]), 200

    except sqlite3.Error:
        return jsonify({
            "error": "Database error"
        }), 500

# RUN API


if __name__ == "__main__":
    app.run(debug=True)