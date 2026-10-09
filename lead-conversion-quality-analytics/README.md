# Lead Conversion & Quality Analytics

An end-to-end portfolio project that evaluates lead conversion performance, tests whether the decline is statistically meaningful, identifies reliable segment differences, and translates the findings into testable business actions.

**Tools:** Python, SQL, MySQL Workbench, Excel, Power Query, Power BI, and Microsoft Fabric

## View the project

- [Portfolio case study](https://vinay-st-portfolio.vercel.app/lead-conversion-quality-analytics)
- [Published Power BI report](https://app.powerbi.com/view?r=eyJrIjoiNjg4N2E0OTItZDk0Ni00ZDIxLWJmZDMtZGZmNTFiNWFhODU5IiwidCI6IjgxM2E3NTMyLWI4YmEtNDNhZi1iMWYyLWRiMWFlMGY2NzA1YiJ9&pageName=pageExecutive)
- [Supporting Excel analysis](excel/Lead_Conversion_Quality_Analytics.xlsx)

## Resume-ready project summary

**Lead Conversion and Quality Analytics Dashboard**

- Analyzed 3,021 anonymized leads across a six-month period using Python, SQL, Excel, and Power BI; established an 8.11% baseline close rate against a 9.60% target.
- Applied logistic regression, chi-square and two-proportion tests, Wilson confidence intervals, and FDR correction to confirm a statistically significant decline and isolate reliable segment differences.
- Identified Holding Tank - Debt as the strongest reliable ad group at 14.50% and Student Debt as the weakest at 1.11%, while clearly separating association from causation.
- Built scenario models showing that 46 additional closes are required to reach the target, and translated the analysis into staged testing and CRM data-quality recommendations.

## Business questions

1. Is lead quality improving or declining over time, and is the trend statistically significant?
2. Which observable lead characteristics are associated with higher or lower close rates?
3. Can the portfolio move from an 8.11% close rate to at least 9.6%, and which opportunities should be tested?

## Executive findings

- The data contains 3,021 leads from April through September 2009. There were 245 closes, producing an 8.11% all-lead close rate.
- Close odds declined by about 10.1% per 30 days. The logistic trend odds ratio was 0.899 (95% CI 0.829–0.974, p = 0.0093), providing statistically significant evidence of decline.
- Holding Tank - Debt was the strongest reliable ad group at 14.50% (49/338), while Student Debt was the weakest at 1.11% (4/360). These are observational associations, not proof that the ad group caused the outcome.
- Reaching the 9.6% target requires at least 291 closes—46 more than observed. The scenario analysis shows testable routes to that target; it is planning evidence, not a forecast or guarantee.
- Unknown outcomes represent 70.84% of all leads. Better CRM outcome tracking is therefore the first operational recommendation.

## Recommended review path

1. Open the portfolio case study for the business story and recommendations.
2. Explore the published Power BI report.
3. Open the Excel workbook for supporting calculations and reconciliations.
4. Review the PBIP source, Python pipeline, or SQL implementation for technical depth.

## Project structure

```text
excel/         supporting Excel analysis workbook
powerbi/       source-controlled PBIP report and semantic model
mysql/         MySQL Workbench schema, embedded data, analysis, and validation
sql/           portable reporting queries
src/           core Python analysis scripts
data/          privacy-safe Power BI input and analytical exports
website/       source code for the interactive portfolio dashboard
```

## Technical approach

- Python: privacy-safe preparation, analytical exports, Wilson confidence intervals, hypothesis tests, logistic regression, scenario analysis, and validation.
- Excel and Power Query: transparent cleaning steps, KPI reconciliation, and reviewer-friendly supporting analysis.
- SQL and MySQL Workbench: constrained analytical schema, repeatable data load, business queries, and validation checks.
- Power BI: executive overview, trend evidence, lead-quality drivers, and quantified opportunity scenarios.
- Statistical methods: logistic time-trend regression, monthly chi-square test, first-versus-last-month two-proportion test, Wilson intervals, and Benjamini-Hochberg false-discovery control.

## Reproduce locally

Install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

The original source file is intentionally excluded. The included `data/sanitized/clean_leads.csv` is de-identified and allows the PBIP model to load locally. To rebuild it from source, place the original workbook at `data/source/Analyst_case_study_dataset_1.xls`, then run:

```powershell
python .\src\run_analysis.py
# Refresh LeadQualityCleaning in excel\Lead_Conversion_Quality_Analytics.xlsx.
python .\src\advanced_analysis.py
```

Before opening the PBIP project on another computer, replace the placeholder `C:\path\to\lead-conversion-quality-analytics` in the semantic-model table definitions with the absolute path to your local clone.

For MySQL Workbench, open `mysql/lead_conversion_quality_analytics_workbench.sql`. It is the self-contained script containing the schema, de-identified analytical rows, business queries, and validation checks.

## Data handling and interpretation

- Direct identifiers and detailed URL fields were removed before downstream analysis.
- The original source is excluded. The included row-level analytical file is de-identified and contains no direct contact fields.
- Unknown outcomes remain in the denominator, so the primary close rate is `Closed / all leads`.
- Segment findings are associations. Opportunity estimates from different dimensions overlap and should not be added together.
- Scenario outputs are test designs that should be validated on a controlled share of future traffic before broader rollout.
