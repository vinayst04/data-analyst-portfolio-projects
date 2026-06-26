# Global Economic Indicators API Dashboard

This project extracts World Bank API data for selected countries and indicators, prepares analysis-ready CSV files, validates the data using SQL and builds a Power BI dashboard for country comparison.

## Tools Used

- Python, Requests and Pandas for API extraction and data preparation
- MySQL for SQL analysis
- Power BI for dashboard building

## Data Scope

- Countries: India, United States, China, Germany, United Kingdom, Japan, Brazil and South Africa
- Indicators: GDP, GDP Growth, Inflation, Unemployment, Population, Internet Users and Life Expectancy
- Years: 2014 to 2024

## Work Completed

- Extracted data from the World Bank API.
- Converted JSON responses into DataFrames.
- Created clean, latest, wide-format, country metadata and indicator metadata CSV files.
- Imported processed CSV files into MySQL for validation and analysis.
- Wrote SQL queries for data coverage, GDP ranking, inflation, unemployment, GDP growth, internet usage, population, latest country snapshot and highest GDP growth years.
- Built a two-page Power BI report for global overview and country comparison.

## Key Results

- Countries: `8`
- Indicators: `7`
- Clean rows: `616`
- Data Availability: `100%`
- Latest United States GDP: about `$28.75T`

## Power BI Report

https://app.powerbi.com/view?r=eyJrIjoiNmQxOTg1NDctM2M2Ni00NGU1LWJkMjEtOWM3ZGMxZDlmNTI4IiwidCI6IjgxM2E3NTMyLWI4YmEtNDNhZi1iMWYyLWRiMWFlMGY2NzA1YiJ9

## Important Files

- `src/fetch_world_bank_indicators.py`
- `sql/world_bank_analysis_queries.sql`
- `dashboard/powerbi_measures.dax`
- `dashboard/Global_Economic_Indicators_Dashboard.pbix`
- `data/processed/`
- `outputs/query_results_csv/`

## Run Python Extraction

```bash
pip install -r requirements.txt
python src/fetch_world_bank_indicators.py
```
