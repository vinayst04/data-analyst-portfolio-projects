# MySQL Workbench implementation

This folder contains the native MySQL 8.0 implementation of the analytical layer. It is generated from the Power Query-cleaned analytical CSV outputs and runs in MySQL Workbench.

## Generated objects

- Database: `lead_quality_analytics`
- Eleven InnoDB tables with primary keys, indexes and validation constraints
- Seven standalone analytical queries in `03_analysis_queries_and_validation.sql`
- Reconciliation and privacy-control queries

The query pack does **not** create database views. Run a numbered `SELECT` query whenever you need that output:

1. Portfolio KPI summary
2. Reliable segments
3. Opportunity summary by dimension
4. Monthly performance
5. Weekly performance
6. Business segment comparison
7. Opportunity ranking

## Run in MySQL Workbench

1. Open `lead_conversion_quality_analytics_workbench.sql` in MySQL Workbench.
2. Select a connected MySQL 8.0 session and execute the complete script.
3. Run any of the seven clearly labelled analytical queries. The final checks should return 3,021 leads, 245 closes, a 0.0810989738 close rate, six months, 27 weeks, seven segment dimensions, zero invalid outcomes, zero IP literals and zero failed checks.

No password or connection information is stored in the project.
