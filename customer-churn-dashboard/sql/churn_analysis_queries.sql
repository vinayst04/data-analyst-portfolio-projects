-- Query 1: 01 Overall Kpis
SELECT
    COUNT(*) AS total_customers,
    SUM(churn_flag) AS churned_customers,
    COUNT(*) - SUM(churn_flag) AS retained_customers,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_percent,
    ROUND(AVG(monthly_charges), 2) AS average_monthly_charges,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk,
    ROUND(SUM(annual_revenue_at_risk), 2) AS annual_revenue_at_risk
FROM telco_churn;


-- Query 2: 02 Churn By Contract
SELECT
    contract,
    COUNT(*) AS total_customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_percent,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk
FROM telco_churn
GROUP BY contract
ORDER BY churn_rate_percent DESC;


-- Query 3: Churn by tenure group
-- MIN(tenure) keeps the groups in natural order: 0-6, 7-12, 13-24, 25-48, 49+.
SELECT
    tenure_group,
    COUNT(*) AS total_customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_percent,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk
FROM telco_churn
GROUP BY tenure_group
ORDER BY MIN(tenure);


-- Query 4: 04 Churn By Payment Method
SELECT
    payment_method,
    COUNT(*) AS total_customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_percent,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk
FROM telco_churn
GROUP BY payment_method
ORDER BY churn_rate_percent DESC;


-- Query 5: 05 Churn By Charge Group
SELECT
    charge_group,
    COUNT(*) AS total_customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_percent,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk
FROM telco_churn
GROUP BY charge_group
ORDER BY churn_rate_percent DESC;


-- Query 6: 06 Revenue At Risk By Contract
SELECT
    contract,
    SUM(churn_flag) AS churned_customers,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk,
    ROUND(SUM(annual_revenue_at_risk), 2) AS annual_revenue_at_risk
FROM telco_churn
GROUP BY contract
ORDER BY monthly_revenue_at_risk DESC;


-- Query 7: 07 Churn By Internet Service
SELECT
    internet_service,
    COUNT(*) AS total_customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_percent
FROM telco_churn
GROUP BY internet_service
ORDER BY churn_rate_percent DESC;


-- Query 8: 08 Churn By Tech Support
SELECT
    tech_support,
    COUNT(*) AS total_customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_percent
FROM telco_churn
GROUP BY tech_support
ORDER BY churn_rate_percent DESC;


-- Query 9: 09 Churn By Senior Status
SELECT
    is_senior,
    COUNT(*) AS total_customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_percent
FROM telco_churn
GROUP BY is_senior
ORDER BY churn_rate_percent DESC;


-- Query 10: 10 High Risk Segments
SELECT
    contract,
    tenure_group,
    charge_group,
    COUNT(*) AS total_customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_percent,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk
FROM telco_churn
GROUP BY contract, tenure_group, charge_group
HAVING COUNT(*) >= 20
ORDER BY churn_rate_percent DESC, monthly_revenue_at_risk DESC
LIMIT 15;
