-- MySQL 8.0 schema for the Lead Conversion & Quality Analytics portfolio project.
-- Designed for execution in MySQL Workbench.

CREATE DATABASE IF NOT EXISTS lead_quality_analytics
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE lead_quality_analytics;

CREATE TABLE IF NOT EXISTS clean_leads (
  LeadKey VARCHAR(32) NOT NULL,
  LeadCreated DATE NOT NULL,
  LeadDate DATE NOT NULL,
  WeekStart DATE NOT NULL,
  MonthStart DATE NOT NULL,
  DaysSinceStart INT UNSIGNED NOT NULL,
  CallStatus VARCHAR(100) NOT NULL,
  OutcomeBucket VARCHAR(40) NOT NULL,
  IsClosed TINYINT UNSIGNED NOT NULL,
  IsGoodProgression TINYINT UNSIGNED NOT NULL,
  IsBadQuality TINYINT UNSIGNED NOT NULL,
  IsUnknown TINYINT UNSIGNED NOT NULL,
  IsPositiveSignal TINYINT UNSIGNED NOT NULL,
  WidgetNameNormalized VARCHAR(255) NOT NULL,
  WidgetFormPages VARCHAR(20) NOT NULL,
  WidgetDesign VARCHAR(100) NOT NULL,
  PublisherZoneName VARCHAR(100) NOT NULL,
  PublisherCampaignName VARCHAR(100) NOT NULL,
  AddressScore DECIMAL(8,4) NULL,
  AddressScoreBand VARCHAR(40) NOT NULL,
  AddressScoreMissing TINYINT UNSIGNED NOT NULL,
  PhoneScore DECIMAL(8,4) NULL,
  PhoneScoreBand VARCHAR(40) NOT NULL,
  PhoneScoreMissing TINYINT UNSIGNED NOT NULL,
  AdvertiserCampaignName VARCHAR(150) NOT NULL,
  State VARCHAR(20) NOT NULL,
  DebtLevel VARCHAR(50) NOT NULL,
  Partner VARCHAR(100) NOT NULL,
  ReferralDomain VARCHAR(255) NOT NULL,
  MarketingCampaign VARCHAR(255) NOT NULL,
  AdGroup VARCHAR(255) NOT NULL,
  Keyword VARCHAR(512) NOT NULL,
  PRIMARY KEY (LeadKey),
  INDEX idx_clean_leads_date (LeadDate),
  INDEX idx_clean_leads_month (MonthStart),
  INDEX idx_clean_leads_outcome (OutcomeBucket),
  CONSTRAINT chk_clean_leads_outcome
    CHECK (IsClosed + IsGoodProgression + IsBadQuality + IsUnknown = 1),
  CONSTRAINT chk_clean_leads_flags
    CHECK (
      IsClosed IN (0,1) AND IsGoodProgression IN (0,1)
      AND IsBadQuality IN (0,1) AND IsUnknown IN (0,1)
      AND IsPositiveSignal IN (0,1)
      AND AddressScoreMissing IN (0,1) AND PhoneScoreMissing IN (0,1)
    )
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS weekly_trends (
  WeekStart DATE NOT NULL PRIMARY KEY,
  Leads INT UNSIGNED NOT NULL,
  Closed INT UNSIGNED NOT NULL,
  GoodProgression INT UNSIGNED NOT NULL,
  BadQuality INT UNSIGNED NOT NULL,
  UnknownLeads INT UNSIGNED NOT NULL,
  PositiveSignals INT UNSIGNED NOT NULL,
  CloseRate DOUBLE NOT NULL,
  PositiveSignalRate DOUBLE NOT NULL,
  CloseRateWilsonLow DOUBLE NOT NULL,
  CloseRateWilsonHigh DOUBLE NOT NULL,
  TargetRate DOUBLE NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS monthly_trends (
  MonthStart DATE NOT NULL PRIMARY KEY,
  Leads INT UNSIGNED NOT NULL,
  Closed INT UNSIGNED NOT NULL,
  GoodProgression INT UNSIGNED NOT NULL,
  BadQuality INT UNSIGNED NOT NULL,
  UnknownLeads INT UNSIGNED NOT NULL,
  PositiveSignals INT UNSIGNED NOT NULL,
  CloseRate DOUBLE NOT NULL,
  PositiveSignalRate DOUBLE NOT NULL,
  CloseRateWilsonLow DOUBLE NOT NULL,
  CloseRateWilsonHigh DOUBLE NOT NULL,
  TargetRate DOUBLE NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS trend_tests (
  TestName VARCHAR(255) NOT NULL PRIMARY KEY,
  Estimate DOUBLE NULL,
  Lower95 DOUBLE NULL,
  Upper95 DOUBLE NULL,
  PValue DOUBLE NULL,
  Interpretation TEXT NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS segment_performance (
  DimensionName VARCHAR(100) NOT NULL,
  Segment VARCHAR(512) NOT NULL,
  Leads INT UNSIGNED NOT NULL,
  Closed INT UNSIGNED NOT NULL,
  CloseRate DOUBLE NOT NULL,
  WilsonLow DOUBLE NOT NULL,
  WilsonHigh DOUBLE NOT NULL,
  LiftVsOverall DOUBLE NOT NULL,
  PValueVsRest DOUBLE NULL,
  MeetsDescriptiveN TINYINT UNSIGNED NOT NULL,
  MeetsReliableN TINYINT UNSIGNED NOT NULL,
  QValueWithinDimension DOUBLE NULL,
  StatisticallyDistinctFDR05 TINYINT UNSIGNED NOT NULL,
  PRIMARY KEY (DimensionName, Segment),
  INDEX idx_segment_reliable (DimensionName, MeetsReliableN),
  CONSTRAINT chk_segment_flags CHECK (
    MeetsDescriptiveN IN (0,1)
    AND MeetsReliableN IN (0,1)
    AND StatisticallyDistinctFDR05 IN (0,1)
  )
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS opportunity_inputs (
  DimensionName VARCHAR(100) NOT NULL,
  Segment VARCHAR(512) NOT NULL,
  Leads INT UNSIGNED NOT NULL,
  Closed INT UNSIGNED NOT NULL,
  CloseRate DOUBLE NOT NULL,
  WilsonLow DOUBLE NOT NULL,
  WilsonHigh DOUBLE NOT NULL,
  BenchmarkSegment VARCHAR(512) NOT NULL,
  BenchmarkObservedRate DOUBLE NOT NULL,
  BenchmarkWilsonLow DOUBLE NOT NULL,
  PlanningRate DOUBLE NOT NULL,
  PotentialIncrementalCloses DOUBLE NOT NULL,
  ScenarioNote TEXT NOT NULL,
  PRIMARY KEY (DimensionName, Segment)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS target_scenarios (
  Scenario VARCHAR(255) NOT NULL PRIMARY KEY,
  LeadsAffected INT UNSIGNED NOT NULL,
  AssumedDestinationRate DOUBLE NOT NULL,
  ExpectedIncrementalCloses DOUBLE NOT NULL,
  ExpectedTotalCloses DOUBLE NOT NULL,
  ExpectedCloseRate DOUBLE NOT NULL,
  MeetsTarget TINYINT UNSIGNED NOT NULL,
  CommercialRevenueAtStatedOffer DOUBLE NOT NULL,
  Assumption TEXT NOT NULL,
  CONSTRAINT chk_target_scenario_flag CHECK (MeetsTarget IN (0,1))
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS model_coefficients (
  Term VARCHAR(512) NOT NULL PRIMARY KEY,
  Coefficient DOUBLE NULL,
  OddsRatio DOUBLE NULL,
  OddsRatioLow95 DOUBLE NULL,
  OddsRatioHigh95 DOUBLE NULL,
  PValue DOUBLE NULL,
  QValue DOUBLE NULL,
  ModelRole VARCHAR(100) NOT NULL,
  BootstrapSignConsistency DOUBLE NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS model_metrics (
  Metric VARCHAR(255) NOT NULL PRIMARY KEY,
  MetricValue DOUBLE NULL,
  Notes TEXT NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS analysis_summary (
  Metric VARCHAR(255) NOT NULL PRIMARY KEY,
  MetricValue DOUBLE NULL,
  Definition TEXT NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS qa_checks (
  CheckName VARCHAR(255) NOT NULL PRIMARY KEY,
  Actual DOUBLE NULL,
  Expected DOUBLE NULL,
  Passed TINYINT UNSIGNED NOT NULL,
  Notes TEXT NOT NULL,
  CONSTRAINT chk_qa_passed CHECK (Passed IN (0,1))
) ENGINE=InnoDB;
