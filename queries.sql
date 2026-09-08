-- BOOKWORLD - SQL EXTRACTION QUERIES


-- 1. REFERENCE DATA
-- Used to enrich sales data in the pipeline

-- Channels
SELECT
    channel_code,
    channel_name,
    acquisition_cost_gbp,
    channel_group,
    is_active
FROM channels;


-- Countries
SELECT
    country_code,
    country_name,
    currency_code,
    vat_rate,
    region,
    is_active
FROM countries;


-- Category rules
SELECT
    category_name,
    margin_rate,
    strategic_flag,
    default_channel_code,
    is_active
FROM category_rules;



-- 2. QUERY WITH FILTER
-- Used as a data quality check before enrichment


SELECT
    country_code,
    country_name,
    currency_code,
    vat_rate,
    region,
    is_active
FROM countries
WHERE is_active = 1;


-- 2. FINAL VERIFICATIONS
-- Used to verify that final tables have been created
-- and contain data

-- Check that tables exist

SELECT name
FROM sqlite_master
WHERE type = 'table'


-- Check number of rows in each final table

SELECT 'sales' AS table_name, COUNT(*) AS row_count
FROM sales

UNION ALL

SELECT 'countries', COUNT(*)
FROM countries

UNION ALL

SELECT 'channels', COUNT(*)
FROM channels

UNION ALL

SELECT 'category_rules', COUNT(*)
FROM category_rules

UNION ALL

SELECT 'sales_by_country', COUNT(*)
FROM sales_by_country

UNION ALL

SELECT 'sales_by_country_month', COUNT(*)
FROM sales_by_country_month

UNION ALL

SELECT 'sales_by_country_channel', COUNT(*)
FROM sales_by_country_channel

UNION ALL

SELECT 'sales_by_country_category', COUNT(*)
FROM sales_by_country_category

UNION ALL

SELECT 'sales_by_country_channel_group', COUNT(*)
FROM sales_by_country_channel_group;