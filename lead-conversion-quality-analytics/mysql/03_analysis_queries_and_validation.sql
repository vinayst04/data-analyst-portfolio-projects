USE lead_quality_analytics;

-- This file contains normal, runnable SELECT queries. No database views are created.
-- Each numbered query returns the same result set that the previous view returned.
-- These drops remove the legacy view objects when this script is re-run in an existing schema.
DROP VIEW IF EXISTS vw_opportunity_ranking;
DROP VIEW IF EXISTS vw_segment_business_performance;
DROP VIEW IF EXISTS vw_weekly_performance;
DROP VIEW IF EXISTS vw_monthly_performance;
DROP VIEW IF EXISTS vw_opportunity_by_dimension;
DROP VIEW IF EXISTS vw_reliable_segments;
DROP VIEW IF EXISTS vw_lead_quality_overview;

-- Query 1: portfolio KPI summary.
SELECT
  COUNT(*) AS total_leads,
  SUM(IsClosed) AS closed_leads,
  SUM(IsClosed) / COUNT(*) AS close_rate,
  SUM(IsGoodProgression) AS good_progression,
  SUM(IsBadQuality) AS bad_quality,
  SUM(IsUnknown) AS unknown_leads
FROM clean_leads;

-- Query 2: segments with a reliable sample size.
SELECT *
FROM segment_performance
WHERE MeetsReliableN = 1;

-- Query 3: opportunity summary by business dimension.
SELECT
  DimensionName,
  MAX(BenchmarkSegment) AS benchmark_segment,
  MAX(BenchmarkObservedRate) AS benchmark_observed_rate,
  MAX(BenchmarkWilsonLow) AS benchmark_wilson_low,
  SUM(PotentialIncrementalCloses) AS potential_incremental_closes
FROM opportunity_inputs
GROUP BY DimensionName;

-- Query 4: monthly lead performance, calculated directly from Clean Leads.
SELECT
  MonthStart,
  COUNT(*) AS leads,
  SUM(IsClosed) AS closed_leads,
  SUM(IsGoodProgression) AS good_progression_leads,
  SUM(IsBadQuality) AS bad_quality_leads,
  SUM(IsUnknown) AS unknown_leads,
  SUM(IsPositiveSignal) AS positive_signal_leads,
  SUM(IsClosed) / NULLIF(COUNT(*), 0) AS close_rate,
  SUM(IsPositiveSignal) / NULLIF(COUNT(*), 0) AS positive_signal_rate,
  0.096 AS target_close_rate,
  (0.096 - SUM(IsClosed) / NULLIF(COUNT(*), 0)) * 100 AS target_gap_percentage_points
FROM clean_leads
GROUP BY MonthStart
ORDER BY MonthStart;

-- Query 5: weekly lead performance, calculated directly from Clean Leads.
SELECT
  WeekStart,
  COUNT(*) AS leads,
  SUM(IsClosed) AS closed_leads,
  SUM(IsGoodProgression) AS good_progression_leads,
  SUM(IsBadQuality) AS bad_quality_leads,
  SUM(IsUnknown) AS unknown_leads,
  SUM(IsPositiveSignal) AS positive_signal_leads,
  SUM(IsClosed) / NULLIF(COUNT(*), 0) AS close_rate,
  SUM(IsPositiveSignal) / NULLIF(COUNT(*), 0) AS positive_signal_rate,
  0.096 AS target_close_rate,
  (0.096 - SUM(IsClosed) / NULLIF(COUNT(*), 0)) * 100 AS target_gap_percentage_points
FROM clean_leads
GROUP BY WeekStart
ORDER BY WeekStart;

-- Query 6: one comparable segment table across seven business dimensions.
WITH segment_counts AS (
  SELECT 'Ad group' AS dimension_name, AdGroup AS segment, COUNT(*) AS leads,
         SUM(IsClosed) AS closed_leads, SUM(IsGoodProgression) AS good_progression_leads,
         SUM(IsBadQuality) AS bad_quality_leads, SUM(IsUnknown) AS unknown_leads
  FROM clean_leads GROUP BY AdGroup
  UNION ALL
  SELECT 'Partner', Partner, COUNT(*), SUM(IsClosed), SUM(IsGoodProgression),
         SUM(IsBadQuality), SUM(IsUnknown)
  FROM clean_leads GROUP BY Partner
  UNION ALL
  SELECT 'Debt level', DebtLevel, COUNT(*), SUM(IsClosed), SUM(IsGoodProgression),
         SUM(IsBadQuality), SUM(IsUnknown)
  FROM clean_leads GROUP BY DebtLevel
  UNION ALL
  SELECT 'State', State, COUNT(*), SUM(IsClosed), SUM(IsGoodProgression),
         SUM(IsBadQuality), SUM(IsUnknown)
  FROM clean_leads GROUP BY State
  UNION ALL
  SELECT 'Widget design', WidgetDesign, COUNT(*), SUM(IsClosed), SUM(IsGoodProgression),
         SUM(IsBadQuality), SUM(IsUnknown)
  FROM clean_leads GROUP BY WidgetDesign
  UNION ALL
  SELECT 'Address score band', AddressScoreBand, COUNT(*), SUM(IsClosed), SUM(IsGoodProgression),
         SUM(IsBadQuality), SUM(IsUnknown)
  FROM clean_leads GROUP BY AddressScoreBand
  UNION ALL
  SELECT 'Phone score band', PhoneScoreBand, COUNT(*), SUM(IsClosed), SUM(IsGoodProgression),
         SUM(IsBadQuality), SUM(IsUnknown)
  FROM clean_leads GROUP BY PhoneScoreBand
), portfolio AS (
  SELECT SUM(IsClosed) / NULLIF(COUNT(*), 0) AS overall_close_rate
  FROM clean_leads
)
SELECT
  segment_counts.dimension_name,
  segment_counts.segment,
  segment_counts.leads,
  segment_counts.closed_leads,
  segment_counts.good_progression_leads,
  segment_counts.bad_quality_leads,
  segment_counts.unknown_leads,
  segment_counts.closed_leads / NULLIF(segment_counts.leads, 0) AS close_rate,
  segment_counts.good_progression_leads / NULLIF(segment_counts.leads, 0) AS good_progression_rate,
  segment_counts.bad_quality_leads / NULLIF(segment_counts.leads, 0) AS bad_quality_rate,
  segment_counts.unknown_leads / NULLIF(segment_counts.leads, 0) AS unknown_rate,
  portfolio.overall_close_rate,
  segment_counts.closed_leads / NULLIF(segment_counts.leads, 0) - portfolio.overall_close_rate AS close_rate_difference,
  (segment_counts.closed_leads / NULLIF(segment_counts.leads, 0)) / NULLIF(portfolio.overall_close_rate, 0) AS close_rate_lift
FROM segment_counts
CROSS JOIN portfolio
ORDER BY dimension_name, close_rate DESC, leads DESC;

-- Query 7: rank the largest below-average opportunities within each dimension.
WITH segment_counts AS (
  SELECT 'Ad group' AS dimension_name, AdGroup AS segment, COUNT(*) AS leads, SUM(IsClosed) AS closed_leads FROM clean_leads GROUP BY AdGroup
  UNION ALL SELECT 'Partner', Partner, COUNT(*), SUM(IsClosed) FROM clean_leads GROUP BY Partner
  UNION ALL SELECT 'Debt level', DebtLevel, COUNT(*), SUM(IsClosed) FROM clean_leads GROUP BY DebtLevel
  UNION ALL SELECT 'State', State, COUNT(*), SUM(IsClosed) FROM clean_leads GROUP BY State
  UNION ALL SELECT 'Widget design', WidgetDesign, COUNT(*), SUM(IsClosed) FROM clean_leads GROUP BY WidgetDesign
  UNION ALL SELECT 'Address score band', AddressScoreBand, COUNT(*), SUM(IsClosed) FROM clean_leads GROUP BY AddressScoreBand
  UNION ALL SELECT 'Phone score band', PhoneScoreBand, COUNT(*), SUM(IsClosed) FROM clean_leads GROUP BY PhoneScoreBand
), portfolio AS (
  SELECT SUM(IsClosed) / NULLIF(COUNT(*), 0) AS overall_close_rate FROM clean_leads
), segment_rates AS (
  SELECT dimension_name, segment, leads, closed_leads,
         closed_leads / NULLIF(leads, 0) AS close_rate,
         overall_close_rate,
         closed_leads / NULLIF(leads, 0) - overall_close_rate AS close_rate_difference,
         (closed_leads / NULLIF(leads, 0)) / NULLIF(overall_close_rate, 0) AS close_rate_lift,
         GREATEST(0, (overall_close_rate - closed_leads / NULLIF(leads, 0)) * leads) AS potential_additional_closes_to_overall
  FROM segment_counts CROSS JOIN portfolio
)
SELECT
  segment_rates.*,
  DENSE_RANK() OVER (PARTITION BY dimension_name ORDER BY close_rate DESC, leads DESC) AS performance_rank,
  DENSE_RANK() OVER (PARTITION BY dimension_name ORDER BY potential_additional_closes_to_overall DESC, leads DESC) AS opportunity_rank
FROM segment_rates
ORDER BY dimension_name, opportunity_rank;

-- Validation queries. Expected controls: 3,021 leads, 245 closes, 46 additional closes, and zero failed checks.
SELECT COUNT(*) AS total_leads, SUM(IsClosed) AS closed_leads, SUM(IsClosed) / COUNT(*) AS close_rate
FROM clean_leads;

SELECT CEILING(COUNT(*) * 0.096) AS target_closes, CEILING(COUNT(*) * 0.096) - SUM(IsClosed) AS incremental_closes_required
FROM clean_leads;

SELECT COUNT(*) AS invalid_outcome_rows
FROM clean_leads
WHERE IsClosed + IsGoodProgression + IsBadQuality + IsUnknown <> 1;

SELECT COUNT(*) AS ip_literal_referral_domains
FROM clean_leads
WHERE INET6_ATON(ReferralDomain) IS NOT NULL;

SELECT COUNT(*) AS failed_qa_checks
FROM qa_checks
WHERE Passed <> 1;
