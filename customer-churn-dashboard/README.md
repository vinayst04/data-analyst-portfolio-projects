# Customer Churn Analytics and Retention Dashboard

This project analyzes Telco customer churn to identify churn patterns by contract type, tenure, payment method, service usage, senior status and revenue at risk.

## Tools Used

- Python and Pandas for data cleaning
- MySQL for SQL analysis
- Power BI for dashboard building

## Dataset

- Source file: `data/raw/telco_churn.csv`
- Cleaned file: `data/processed/telco_churn_clean.csv`
- Rows: 7,043

## Work Completed

- Cleaned Telco customer data using Python.
- Converted `total_charges` from text to numeric.
- Created `churn_flag`, `is_senior`, `tenure_group`, `charge_group`, `monthly_revenue_at_risk`, and `annual_revenue_at_risk`.
- Wrote SQL queries for churn by contract, tenure, payment method, charge group, internet service, tech support, senior status and high-risk segments.
- Built a two-page Power BI dashboard for churn overview and revenue-risk analysis.

## Key Results

- Total Customers: `7,043`
- Churned Customers: `1,869`
- Churn Rate: `26.54%`
- Monthly Revenue at Risk: `$139.13K`
- Annual Revenue at Risk: `$1.67M`
- Highest-risk groups: month-to-month customers, early-tenure customers and electronic check users

## Power BI Report

https://app.powerbi.com/view?r=eyJrIjoiMTk5Y2U2NTctMGNhNy00ODI3LTlhZDctMjhkNmNkYWMzODZhIiwidCI6IjgxM2E3NTMyLWI4YmEtNDNhZi1iMWYyLWRiMWFlMGY2NzA1YiJ9

## Important Files

- `src/clean_telco_churn.py`
- `sql/churn_analysis_queries.sql`
- `dashboard/powerbi_measures.dax`
- `dashboard/Customer_Churn_Retention_Dashboard.pbix`
- `outputs/query_results_csv/`

## Run Python Cleaning

```bash
pip install -r requirements.txt
python src/clean_telco_churn.py
```
