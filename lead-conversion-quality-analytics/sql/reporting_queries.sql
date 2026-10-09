-- Portable reporting queries over the sanitized clean_leads table.
-- Run a query when you need the result; no views are created.

-- Portfolio KPI query.
SELECT
  COUNT(*) AS total_leads,
  SUM(IsClosed) AS closed_leads,
  1.0 * SUM(IsClosed) / COUNT(*) AS close_rate,
  SUM(IsGoodProgression) AS good_progression,
  SUM(IsBadQuality) AS bad_quality,
  SUM(IsUnknown) AS unknown
FROM clean_leads;

-- Reliable segment query.
SELECT *
FROM segment_performance
WHERE MeetsReliableN = 1;

-- Opportunity summary by dimension.
SELECT
  Dimension AS dimension_name,
  MAX(BenchmarkSegment) AS benchmark_segment,
  MAX(BenchmarkObservedRate) AS benchmark_observed_rate,
  MAX(BenchmarkWilsonLow) AS benchmark_wilson_low,
  SUM(PotentialIncrementalCloses) AS potential_incremental_closes
FROM opportunity_inputs
GROUP BY Dimension;
