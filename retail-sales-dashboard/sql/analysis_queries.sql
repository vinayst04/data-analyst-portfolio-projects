-- Retail Sales Dashboard: Business Analysis SQL Queries
-- Dataset: Sample Superstore
-- Table name: superstore

-- Query 1: 01 Overall Kpis
SELECT
  ROUND(SUM(sales), 2) AS total_sales,
  ROUND(SUM(profit), 2) AS total_profit,
  ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS profit_margin_percent,
  COUNT(DISTINCT order_id) AS total_orders,
  COUNT(DISTINCT customer_id) AS total_customers,
  SUM(quantity) AS total_quantity,
  ROUND(AVG(discount) * 100, 2) AS average_discount_percent
FROM superstore;

-- Query 2: 02 Sales Profit By Category
SELECT
  category,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS profit_margin_percent
FROM superstore
GROUP BY category
ORDER BY sales DESC;

-- Query 3: 03 Sales Profit By Sub Category
SELECT
  sub_category,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS profit_margin_percent
FROM superstore
GROUP BY sub_category
ORDER BY profit ASC;

-- Query 4: 04 Region Performance
SELECT
  region,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS profit_margin_percent
FROM superstore
GROUP BY region
ORDER BY profit DESC;

-- Query 5: 05 Segment Performance
SELECT
  segment,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS profit_margin_percent
FROM superstore
GROUP BY segment
ORDER BY profit DESC;

-- Query 6: Discount band impact
-- Shows whether higher discount bands are helping or hurting profit.
SELECT
  discount_band,
  COUNT(*) AS total_rows,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS profit_margin_percent
FROM superstore
GROUP BY discount_band
ORDER BY profit_margin_percent DESC;

-- Query 7: 07 Top 10 Products By Sales
SELECT
  product_name,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(profit), 2) AS profit
FROM superstore
GROUP BY product_name
ORDER BY sales DESC
LIMIT 10;

-- Query 8: 08 Bottom 10 Products By Profit
SELECT
  product_name,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(profit), 2) AS profit
FROM superstore
GROUP BY product_name
ORDER BY profit ASC
LIMIT 10;

-- Query 9: 09 Monthly Sales Trend
SELECT
  year_month,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(profit), 2) AS profit
FROM superstore
GROUP BY year_month
ORDER BY year_month;

-- Query 10: State profit leakage
-- Keeps only states with sales above 10000 so tiny states do not dominate the list.
SELECT
  state,
  region,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS profit_margin_percent
FROM superstore
GROUP BY state, region
HAVING SUM(sales) > 10000
ORDER BY profit ASC
LIMIT 15;
