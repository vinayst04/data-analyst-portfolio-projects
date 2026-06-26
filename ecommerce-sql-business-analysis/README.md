# E-commerce SQL Business Analysis

This project uses the Olist Brazilian e-commerce dataset to perform SQL-based business analysis across orders, customers, sellers, products, payments, delivery and reviews.

## Tools Used

- MySQL for business analysis
- SQL for joins, aggregations, CTEs, ranking and trend analysis
- Python for checking CSV files and row counts

## Dataset Tables

- `olist_customers_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `product_category_name_translation.csv`

## Work Completed

- Checked all raw CSV files using Python.
- Loaded the Olist CSV files into MySQL tables.
- Wrote 15 SQL queries covering business KPIs, monthly revenue, product categories, customer states, seller ranking, seller revenue share, repeat customers, payment methods, delivery performance, reviews and high-value orders.

## Key Results

- Total Orders: `99,441`
- Delivered Orders: `96,478`
- Unique Customers: `96,096`
- Active Sellers: `3,095`
- Product Revenue: `$13.59M`
- Freight Value: `$2.25M`
- Late Delivery Rate: `6.77%`
- Highest revenue category: `health_beauty`
- Highest revenue customer state: `SP`

## Important Files

- `src/check_olist_csv_files.py`
- `sql/business_analysis_queries.sql`
- `outputs/query_results_csv/`
- `data/raw/`

## Run CSV Check

```bash
pip install -r requirements.txt
python src/check_olist_csv_files.py
```

## SQL Analysis

Import the CSV files into MySQL with the table names shown in the SQL file, then run:

```text
sql/business_analysis_queries.sql
```
