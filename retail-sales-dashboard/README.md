# Retail Sales and Profitability Dashboard

This project analyzes Sample Superstore sales data to understand revenue, profit, discount impact, product performance, and regional profitability.

## Tools Used

- Python and Pandas for data cleaning
- MySQL for SQL analysis
- Power BI for dashboard building

## Dataset

- Source file: `data/raw/superstore.csv`
- Cleaned file: `data/processed/superstore_clean.csv`
- Rows: 9,994

## Work Completed

- Cleaned raw sales data using Python.
- Standardized column names.
- Converted order and ship dates into date fields.
- Created `year`, `month`, `year_month`, `shipping_days`, `profit_margin`, and `discount_band`.
- Wrote SQL queries for sales, profit, category, region, discount, product and monthly trend analysis.
- Built a Power BI dashboard with KPI cards, category and region visuals, yearly trend, discount impact, sub-category profit and product-level table.

## Key Results

- Total Sales: `$2.30M`
- Total Profit: `$286.40K`
- Profit Margin: `12.47%`
- Total Orders: `5,009`
- Strongest category: `Technology`
- Weak area identified: `Tables` sub-category and high-discount orders

## Power BI Report

https://app.powerbi.com/view?r=eyJrIjoiOWQyOTFkYTItOTM5Mi00N2E1LTliMjItNDA4YzUyNzg1ZWEzIiwidCI6IjgxM2E3NTMyLWI4YmEtNDNhZi1iMWYyLWRiMWFlMGY2NzA1YiJ9&pageName=55fa1cf11714d49bec3b

## Important Files

- `src/clean_superstore.py`
- `sql/analysis_queries.sql`
- `dashboard/powerbi_measures.dax`
- `dashboard/Retail_Sales_Dashboard.pbix`
- `outputs/query_results_csv/`

## Run Python Cleaning

```bash
pip install -r requirements.txt
python src/clean_superstore.py
```
