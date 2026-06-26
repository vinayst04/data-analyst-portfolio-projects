-- Global Economic Indicators: Simple SQL Analysis Queries
-- Use these table names after loading the processed CSV files into MySQL:
-- world_bank_indicators_clean
-- world_bank_latest_indicators
-- country_metadata
-- indicator_metadata


-- Query 1: Data coverage summary
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT country_code) AS countries,
    COUNT(DISTINCT indicator_code) AS indicators,
    MIN(year) AS start_year,
    MAX(year) AS end_year
FROM world_bank_indicators_clean;


-- Query 2: Latest GDP by country
SELECT
    country_name,
    latest_year,
    ROUND(value / 1000000000000.0, 2) AS gdp_trillion_usd
FROM world_bank_latest_indicators
WHERE indicator_code = 'NY.GDP.MKTP.CD'
ORDER BY value DESC;


-- Query 3: Latest unemployment by country
SELECT
    country_name,
    latest_year,
    ROUND(value, 2) AS unemployment_percent
FROM world_bank_latest_indicators
WHERE indicator_code = 'SL.UEM.TOTL.ZS'
ORDER BY value DESC;


-- Query 4: Latest internet users by country
SELECT
    country_name,
    latest_year,
    ROUND(value, 2) AS internet_users_percent
FROM world_bank_latest_indicators
WHERE indicator_code = 'IT.NET.USER.ZS'
ORDER BY value DESC;


-- Query 5: GDP growth trend
SELECT
    country_name,
    year,
    ROUND(value, 2) AS gdp_growth_percent
FROM world_bank_indicators_clean
WHERE indicator_code = 'NY.GDP.MKTP.KD.ZG'
ORDER BY country_name, year;


-- Query 6: Average value by indicator
SELECT
    short_name,
    ROUND(AVG(value), 2) AS average_value
FROM world_bank_indicators_clean
WHERE value IS NOT NULL
GROUP BY short_name
ORDER BY short_name;


-- Query 7: Countries by region
SELECT
    region,
    COUNT(*) AS country_count
FROM country_metadata
GROUP BY region
ORDER BY country_count DESC;


-- Query 8: Latest country snapshot
-- This uses the wide table created by Python.
-- Each indicator already has its own column, so the SQL stays simple.
SELECT
    country_name,
    ROUND(`GDP` / 1000000000000.0, 2) AS gdp_trillion_usd,
    ROUND(`GDP Growth`, 2) AS gdp_growth_percent,
    ROUND(`Inflation`, 2) AS inflation_percent,
    ROUND(`Unemployment`, 2) AS unemployment_percent,
    ROUND(`Internet Users`, 2) AS internet_users_percent,
    ROUND(`Life Expectancy`, 2) AS life_expectancy
FROM country_year_indicators_wide
WHERE year = 2024
ORDER BY gdp_trillion_usd DESC;
