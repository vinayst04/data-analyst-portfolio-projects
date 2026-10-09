"""Build the optional advanced analytical layer for the case study.

This module contains the statistical tests, confidence intervals, multiple-testing
adjustments, regression, temporal holdout, and bootstrap checks. The resulting
totals, privacy controls, and analytical outputs were independently reconciled
before publication.

Cleaning is owned by the Excel Power Query named LeadQualityCleaning. This module
reads the refreshed Clean Leads worksheet and performs analysis only.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportions_ztest


PROJECT_DIR = Path(__file__).resolve().parents[1]
SOURCE_FILE = PROJECT_DIR / "data" / "source" / "Analyst_case_study_dataset_1.xls"
WORKBOOK_FILE = PROJECT_DIR / "excel" / "Lead_Conversion_Quality_Analytics.xlsx"
SANITIZED_DIR = PROJECT_DIR / "data" / "sanitized"
EXPORT_DIR = PROJECT_DIR / "data" / "exports"
QA_DIR = PROJECT_DIR / "qa"

TARGET_RATE = 0.096
BASE_CPL = 30.0
OFFERED_CPL = 33.0
MIN_SEGMENT_N = 30
RELIABLE_SEGMENT_N = 75
MODEL_RARE_N = 60
RANDOM_SEED = 20260921

PII_COLUMNS = {
    "FirstName",
    "Email",
    "IP Address",
    "ReferralURL",
    "ReferralURL Parameters",
    "LandingPageURL",
    "Landing Page URL Parameters",
    "SearchQuery",
}

GOOD_STATUSES = {"EP Sent", "EP Received", "EP Confirmed"}
BAD_STATUSES = {
    "Unable to contact - Bad Contact Information",
    "Contacted - Invalid Profile",
    "Contacted - Doesn't Qualify",
}


def is_ip_literal(value: object) -> bool:
    """Return True only when the complete value is an IPv4 or IPv6 address."""
    if value is None or pd.isna(value):
        return False
    try:
        ipaddress.ip_address(str(value).strip())
        return True
    except ValueError:
        return False


def sensitive_value_count(df: pd.DataFrame) -> int:
    """Count direct identifiers that survive in downstream text values."""
    email_pattern = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", flags=re.I)
    query_pattern = re.compile(r"(?:\?|&)[^\s=&?]+=[^\s&]*", flags=re.I)
    count = 0
    for column in df.select_dtypes(include=["object", "string"]).columns:
        for value in df[column].dropna().astype(str):
            stripped = value.strip()
            count += int(is_ip_literal(stripped))
            count += int(bool(email_pattern.fullmatch(stripped)))
            count += int(bool(query_pattern.search(stripped)))
    return count


def wilson_interval(successes: int, total: int, alpha: float = 0.05) -> tuple[float, float]:
    if total <= 0:
        return (np.nan, np.nan)
    z = stats.norm.ppf(1 - alpha / 2)
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt((p * (1 - p) / total) + (z * z / (4 * total * total))) / denominator
    return (max(0.0, center - half), min(1.0, center + half))


def load_power_query_clean_leads() -> pd.DataFrame:
    """Load the refreshed Excel Power Query output used by every downstream tool."""
    clean = pd.read_excel(WORKBOOK_FILE, sheet_name="Clean Leads", header=2)
    clean = clean.dropna(how="all")
    clean = clean.loc[clean["LeadKey"].notna()].copy()

    for column in ["LeadCreated", "LeadDate", "WeekStart", "MonthStart"]:
        clean[column] = pd.to_datetime(clean[column], errors="raise")

    integer_columns = [
        "DaysSinceStart",
        "IsClosed",
        "IsGoodProgression",
        "IsBadQuality",
        "IsUnknown",
        "IsPositiveSignal",
        "AddressScoreMissing",
        "PhoneScoreMissing",
    ]
    for column in integer_columns:
        clean[column] = pd.to_numeric(clean[column], errors="raise").astype(int)

    for column in ["AddressScore", "PhoneScore"]:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")

    if len(clean) != 3021:
        raise ValueError(f"Expected 3,021 Power Query rows, found {len(clean):,}")
    if clean["LeadKey"].nunique() != len(clean):
        raise ValueError("Power Query output contains duplicate LeadKey values")
    if sensitive_value_count(clean):
        raise ValueError("Power Query output contains a sensitive value")
    return clean


def aggregate_trend(df: pd.DataFrame, period_col: str) -> pd.DataFrame:
    trend = (
        df.groupby(period_col, dropna=False)
        .agg(
            Leads=("LeadKey", "size"),
            Closed=("IsClosed", "sum"),
            GoodProgression=("IsGoodProgression", "sum"),
            BadQuality=("IsBadQuality", "sum"),
            Unknown=("IsUnknown", "sum"),
            PositiveSignals=("IsPositiveSignal", "sum"),
        )
        .reset_index()
        .sort_values(period_col)
    )
    trend["CloseRate"] = trend["Closed"] / trend["Leads"]
    trend["PositiveSignalRate"] = trend["PositiveSignals"] / trend["Leads"]
    cis = trend.apply(lambda row: wilson_interval(int(row["Closed"]), int(row["Leads"])), axis=1)
    trend["CloseRateWilsonLow"] = [x[0] for x in cis]
    trend["CloseRateWilsonHigh"] = [x[1] for x in cis]
    trend["TargetRate"] = TARGET_RATE
    return trend


def trend_tests(df: pd.DataFrame, monthly: pd.DataFrame) -> pd.DataFrame:
    model = smf.glm("IsClosed ~ DaysSinceStart", data=df, family=sm.families.Binomial()).fit()
    beta = float(model.params["DaysSinceStart"])
    se = float(model.bse["DaysSinceStart"])
    odds_30 = math.exp(beta * 30)
    odds_30_low = math.exp((beta - 1.96 * se) * 30)
    odds_30_high = math.exp((beta + 1.96 * se) * 30)
    contingency = np.column_stack([monthly["Closed"], monthly["Leads"] - monthly["Closed"]])
    chi2, chi_p, chi_dof, _ = stats.chi2_contingency(contingency)

    first = monthly.iloc[0]
    last = monthly.iloc[-1]
    z_stat, endpoint_p = proportions_ztest(
        [int(first["Closed"]), int(last["Closed"])],
        [int(first["Leads"]), int(last["Leads"])],
    )
    rows = [
        {
            "Test": "Logistic linear time trend",
            "Estimate": odds_30,
            "Lower95": odds_30_low,
            "Upper95": odds_30_high,
            "PValue": float(model.pvalues["DaysSinceStart"]),
            "Interpretation": "Odds ratio per 30 days; association only.",
        },
        {
            "Test": "Monthly rate heterogeneity",
            "Estimate": float(chi2),
            "Lower95": np.nan,
            "Upper95": np.nan,
            "PValue": float(chi_p),
            "Interpretation": f"Chi-square across {int(chi_dof + 1)} months.",
        },
        {
            "Test": "First vs last month",
            "Estimate": float(last["CloseRate"] - first["CloseRate"]),
            "Lower95": np.nan,
            "Upper95": np.nan,
            "PValue": float(endpoint_p),
            "Interpretation": "Unadjusted endpoint difference; sensitive to month mix.",
        },
    ]
    return pd.DataFrame(rows)


def segment_performance(df: pd.DataFrame) -> pd.DataFrame:
    dimensions = {
        "Widget": "WidgetNameNormalized",
        "Widget pages": "WidgetFormPages",
        "Widget design": "WidgetDesign",
        "Publisher zone": "PublisherZoneName",
        "Publisher channel": "PublisherCampaignName",
        "Advertiser campaign": "AdvertiserCampaignName",
        "State": "State",
        "Debt level": "DebtLevel",
        "Partner": "Partner",
        "Referral domain": "ReferralDomain",
        "Marketing campaign": "MarketingCampaign",
        "Ad group": "AdGroup",
        "Keyword": "Keyword",
        "Address score band": "AddressScoreBand",
        "Phone score band": "PhoneScoreBand",
    }
    baseline = df["IsClosed"].mean()
    rows: list[dict[str, object]] = []
    for dimension, column in dimensions.items():
        grouped = df.groupby(column, dropna=False)["IsClosed"].agg(["size", "sum"]).reset_index()
        for _, item in grouped.iterrows():
            n = int(item["size"])
            closed = int(item["sum"])
            other_n = len(df) - n
            other_closed = int(df["IsClosed"].sum()) - closed
            low, high = wilson_interval(closed, n)
            if n > 0 and other_n > 0:
                try:
                    _, p_value = proportions_ztest([closed, other_closed], [n, other_n])
                except (ValueError, ZeroDivisionError):
                    p_value = np.nan
            else:
                p_value = np.nan
            rows.append(
                {
                    "Dimension": dimension,
                    "Segment": str(item[column]),
                    "Leads": n,
                    "Closed": closed,
                    "CloseRate": closed / n if n else np.nan,
                    "WilsonLow": low,
                    "WilsonHigh": high,
                    "LiftVsOverall": (closed / n) / baseline if n and baseline else np.nan,
                    "PValueVsRest": p_value,
                    "MeetsDescriptiveN": int(n >= MIN_SEGMENT_N),
                    "MeetsReliableN": int(n >= RELIABLE_SEGMENT_N),
                }
            )
    result = pd.DataFrame(rows)
    result["QValueWithinDimension"] = np.nan
    for dimension, idx in result.groupby("Dimension").groups.items():
        valid_idx = [i for i in idx if pd.notna(result.loc[i, "PValueVsRest"])]
        if valid_idx:
            result.loc[valid_idx, "QValueWithinDimension"] = multipletests(
                result.loc[valid_idx, "PValueVsRest"], method="fdr_bh"
            )[1]
    result["StatisticallyDistinctFDR05"] = (result["QValueWithinDimension"] < 0.05).astype(int)
    return result.sort_values(["Dimension", "Leads", "CloseRate"], ascending=[True, False, False]).reset_index(drop=True)


def opportunity_inputs(segments: pd.DataFrame) -> pd.DataFrame:
    practical_dimensions = {
        "Widget", "Widget pages", "Widget design", "Publisher zone", "Publisher channel",
        "Advertiser campaign", "Debt level", "Partner", "Marketing campaign", "Ad group",
        "Address score band", "Phone score band",
    }
    usable = segments[
        segments["Dimension"].isin(practical_dimensions) & segments["MeetsReliableN"].eq(1)
    ].copy()
    rows: list[pd.DataFrame] = []
    for dimension, group in usable.groupby("Dimension"):
        benchmark_row = group.sort_values(["WilsonLow", "Leads"], ascending=False).iloc[0]
        benchmark_rate = float(benchmark_row["CloseRate"])
        benchmark_lower = float(benchmark_row["WilsonLow"])
        g = group.copy()
        g["BenchmarkSegment"] = str(benchmark_row["Segment"])
        g["BenchmarkObservedRate"] = benchmark_rate
        g["BenchmarkWilsonLow"] = benchmark_lower
        # Conservative planning rate uses the benchmark's lower confidence bound.
        g["PlanningRate"] = benchmark_lower
        g["PotentialIncrementalCloses"] = np.maximum(0, g["Leads"] * (g["PlanningRate"] - g["CloseRate"]))
        g["ScenarioNote"] = "Dimension-specific planning input; overlapping dimensions are not additive."
        rows.append(g)
    if not rows:
        return pd.DataFrame()
    result = pd.concat(rows, ignore_index=True)
    return result[
        [
            "Dimension", "Segment", "Leads", "Closed", "CloseRate", "WilsonLow", "WilsonHigh",
            "BenchmarkSegment", "BenchmarkObservedRate", "BenchmarkWilsonLow", "PlanningRate",
            "PotentialIncrementalCloses", "ScenarioNote",
        ]
    ].sort_values(["Dimension", "PotentialIncrementalCloses"], ascending=[True, False])


def build_target_scenarios(df: pd.DataFrame, segments: pd.DataFrame) -> pd.DataFrame:
    """Create transparent, non-additive routes to the minimum 9.6% threshold."""
    total = len(df)
    closed = int(df["IsClosed"].sum())
    target_closes = math.ceil(total * TARGET_RATE)
    gap = target_closes - closed
    ad_groups = segments[(segments["Dimension"] == "Ad group") & (segments["MeetsReliableN"] == 1)].copy()
    benchmark = ad_groups.loc[ad_groups["Segment"].eq("Holding Tank - Debt")].iloc[0]
    student = ad_groups.loc[ad_groups["Segment"].eq("Student Debt")].iloc[0]

    observed_delta = float(benchmark["CloseRate"] - student["CloseRate"])
    observed_shift = math.ceil(gap / observed_delta)
    observed_gain = observed_shift * observed_delta

    # Conservative planning uses the benchmark's lower Wilson bound and shifts the
    # lowest-performing eligible sources first. The final source is partially shifted.
    planning_rate = float(benchmark["WilsonLow"])
    sources = ad_groups[
        ~ad_groups["Segment"].eq(benchmark["Segment"]) & (ad_groups["CloseRate"] < planning_rate)
    ].sort_values("CloseRate")
    remaining = float(gap)
    shifted = 0.0
    conservative_gain = 0.0
    source_parts: list[str] = []
    for _, source in sources.iterrows():
        delta = planning_rate - float(source["CloseRate"])
        if delta <= 0 or remaining <= 0:
            continue
        available = float(source["Leads"])
        take = min(available, remaining / delta)
        shifted += take
        gain = take * delta
        conservative_gain += gain
        remaining -= gain
        source_parts.append(f"{source['Segment']} ({math.ceil(take):,} leads)")

    scenarios = pd.DataFrame(
        [
            {
                "Scenario": "Portfolio conversion target",
                "LeadsAffected": total,
                "AssumedDestinationRate": TARGET_RATE,
                "ExpectedIncrementalCloses": gap,
                "ExpectedTotalCloses": target_closes,
                "ExpectedCloseRate": target_closes / total,
                "MeetsTarget": 1,
                "CommercialRevenueAtStatedOffer": total * OFFERED_CPL,
                "Assumption": "Improve conversion across the portfolio; operational mechanism must be tested.",
            },
            {
                "Scenario": "Observed ad-group mix test",
                "LeadsAffected": observed_shift,
                "AssumedDestinationRate": float(benchmark["CloseRate"]),
                "ExpectedIncrementalCloses": observed_gain,
                "ExpectedTotalCloses": closed + observed_gain,
                "ExpectedCloseRate": (closed + observed_gain) / total,
                "MeetsTarget": int((closed + observed_gain) >= target_closes),
                "CommercialRevenueAtStatedOffer": total * OFFERED_CPL,
                "Assumption": f"Shift {observed_shift:,} Student Debt leads to Holding Tank - Debt at observed rates. Association may not persist after reallocation.",
            },
            {
                "Scenario": "Conservative ad-group mix test",
                "LeadsAffected": math.ceil(shifted),
                "AssumedDestinationRate": planning_rate,
                "ExpectedIncrementalCloses": conservative_gain,
                "ExpectedTotalCloses": closed + conservative_gain,
                "ExpectedCloseRate": (closed + conservative_gain) / total,
                "MeetsTarget": int((closed + conservative_gain) >= target_closes - 1e-9),
                "CommercialRevenueAtStatedOffer": total * OFFERED_CPL,
                "Assumption": "Shift " + ", then ".join(source_parts) + " to Holding Tank - Debt using its 95% Wilson lower bound. Validate with a randomized or staged test.",
            },
        ]
    )
    return scenarios


def collapse_rare(series: pd.Series, min_n: int = MODEL_RARE_N) -> pd.Series:
    counts = series.value_counts(dropna=False)
    keep = set(counts[counts >= min_n].index)
    return series.where(series.isin(keep), "Other / rare")


def auc_rank(y_true: pd.Series, predicted: pd.Series) -> float:
    positive = int(y_true.sum())
    negative = len(y_true) - positive
    if positive == 0 or negative == 0:
        return np.nan
    ranks = stats.rankdata(predicted)
    return float((ranks[y_true.to_numpy() == 1].sum() - positive * (positive + 1) / 2) / (positive * negative))


def fit_explanatory_model(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    model_df = df.copy()
    # Exclude structurally redundant fields from the same model: PublisherZone is a
    # one-to-one proxy for PublisherCampaign, AdvertiserCampaign is determined by
    # CreditSolutions creative, and Call-center Partner is determined by channel.
    categorical = ["WidgetFormPages", "WidgetDesign", "PublisherCampaignName", "DebtLevel"]
    for column in categorical:
        model_df[column] = collapse_rare(model_df[column].astype(str))
    model_df["Time30Days"] = model_df["DaysSinceStart"] / 30.0
    model_df["AddressScoreFilled"] = model_df["AddressScore"].fillna(model_df["AddressScore"].median())
    model_df["PhoneScoreFilled"] = model_df["PhoneScore"].fillna(model_df["PhoneScore"].median())

    formula = (
        "IsClosed ~ Time30Days + AddressScoreFilled + AddressScoreMissing + "
        "PhoneScoreFilled + PhoneScoreMissing + C(WidgetFormPages) + C(WidgetDesign) + "
        "C(PublisherCampaignName) + C(DebtLevel)"
    )
    model = smf.glm(formula, data=model_df, family=sm.families.Binomial()).fit(cov_type="HC1")
    conf = model.conf_int()
    coefficients = pd.DataFrame(
        {
            "Term": model.params.index,
            "Coefficient": model.params.values,
            "OddsRatio": np.exp(np.clip(model.params.values, -50, 50)),
            "OddsRatioLow95": np.exp(np.clip(conf[0].values, -50, 50)),
            "OddsRatioHigh95": np.exp(np.clip(conf[1].values, -50, 50)),
            "PValue": model.pvalues.values,
        }
    )
    coefficients["QValue"] = multipletests(coefficients["PValue"].fillna(1), method="fdr_bh")[1]
    coefficients["ModelRole"] = "Explanatory association; coefficients are adjusted for listed covariates."

    predicted = model.predict(model_df)
    split_date = model_df["LeadDate"].quantile(0.80)
    train = model_df[model_df["LeadDate"] <= split_date]
    test = model_df[model_df["LeadDate"] > split_date]
    train_model = smf.glm(formula, data=train, family=sm.families.Binomial()).fit()
    test_pred = train_model.predict(test)

    # Bootstrap sign stability for non-intercept terms.
    rng = np.random.default_rng(RANDOM_SEED)
    terms = list(model.params.index)
    boot_signs = {term: [] for term in terms if term != "Intercept"}
    successful_bootstraps = 0
    for _ in range(100):
        sample_idx = rng.integers(0, len(model_df), len(model_df))
        sample = model_df.iloc[sample_idx]
        try:
            boot = smf.glm(formula, data=sample, family=sm.families.Binomial()).fit(maxiter=100, disp=0)
        except Exception:
            continue
        successful_bootstraps += 1
        for term in boot_signs:
            if term in boot.params and np.isfinite(boot.params[term]):
                boot_signs[term].append(np.sign(boot.params[term]))
    sign_consistency = {}
    for term, signs in boot_signs.items():
        expected_sign = np.sign(model.params[term])
        sign_consistency[term] = float(np.mean(np.asarray(signs) == expected_sign)) if signs else np.nan
    coefficients["BootstrapSignConsistency"] = coefficients["Term"].map(sign_consistency)
    coefficients.loc[coefficients["Term"].eq("Intercept"), "BootstrapSignConsistency"] = np.nan

    metrics = pd.DataFrame(
        [
            {"Metric": "Observations", "Value": len(model_df), "Notes": "All sanitized leads."},
            {"Metric": "Events", "Value": int(model_df["IsClosed"].sum()), "Notes": "Closed leads."},
            {"Metric": "Parameters", "Value": len(model.params), "Notes": "Includes intercept and encoded categories."},
            {"Metric": "Design matrix rank", "Value": int(np.linalg.matrix_rank(model.model.exog)), "Notes": "Should equal parameter count."},
            {"Metric": "Events per parameter", "Value": model_df["IsClosed"].sum() / len(model.params), "Notes": "Model complexity check."},
            {"Metric": "In-sample AUC", "Value": auc_rank(model_df["IsClosed"], predicted), "Notes": "Discrimination, not causal evidence."},
            {"Metric": "In-sample Brier score", "Value": float(np.mean((model_df["IsClosed"] - predicted) ** 2)), "Notes": "Lower is better."},
            {"Metric": "Temporal holdout observations", "Value": len(test), "Notes": f"After {pd.Timestamp(split_date).date()}."},
            {"Metric": "Temporal holdout events", "Value": int(test["IsClosed"].sum()), "Notes": "Closed leads in holdout."},
            {"Metric": "Temporal holdout AUC", "Value": auc_rank(test["IsClosed"], test_pred), "Notes": "Fit on first 80% by time."},
            {"Metric": "Temporal holdout Brier score", "Value": float(np.mean((test["IsClosed"] - test_pred) ** 2)), "Notes": "Fit on first 80% by time."},
            {"Metric": "Successful bootstrap fits", "Value": successful_bootstraps, "Notes": "Out of 100 resamples."},
            {"Metric": "Converged", "Value": int(bool(model.converged)), "Notes": "Statsmodels GLM convergence flag."},
        ]
    )
    return coefficients, metrics


def build_summary(df: pd.DataFrame, trends: pd.DataFrame, segments: pd.DataFrame, opportunities: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    closed = int(df["IsClosed"].sum())
    target_closes = math.ceil(total * TARGET_RATE)
    baseline = closed / total
    rows = [
        ("Total leads", total, "All source rows; Unknown remains in denominator."),
        ("Closed leads", closed, "Primary success outcome."),
        ("Baseline close rate", baseline, "Closed / all leads."),
        ("Target close rate", TARGET_RATE, "Assignment threshold."),
        ("Minimum closes at target", target_closes, "Ceiling(total leads x target rate)."),
        ("Incremental closes needed", target_closes - closed, "Minimum target closes less observed closes."),
        ("Observed CPL revenue", total * BASE_CPL, "Uses $30 baseline CPL."),
        ("Revenue at stated $33 CPL", total * OFFERED_CPL, "Uses the explicit $33 offer."),
        ("Revenue uplift at stated $33 CPL", total * (OFFERED_CPL - BASE_CPL), "The stated $30 to $33 change is 10%, not 20%."),
        ("Revenue at literal 20% CPL uplift", total * BASE_CPL * 1.20, "Sensitivity using $36 CPL."),
        ("Unknown status leads", int(df["IsUnknown"].sum()), "Includes blank CallStatus values."),
        ("Good progression leads", int(df["IsGoodProgression"].sum()), "EP Sent, EP Received, EP Confirmed."),
        ("Bad quality leads", int(df["IsBadQuality"].sum()), "Unable to contact, invalid profile, does not qualify."),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value", "Definition"])


def build_qa(
    df: pd.DataFrame,
    raw: pd.DataFrame,
    qa_meta: dict[str, int],
    summary: pd.DataFrame,
    target_scenarios: pd.DataFrame,
) -> pd.DataFrame:
    allowed_statuses = {"Closed", *GOOD_STATUSES, *BAD_STATUSES, "Unknown"}
    downstream_columns = set(df.columns)
    target_closes = math.ceil(len(df) * TARGET_RATE)
    checks = [
        ("Total lead count", len(df), 3021, len(df) == 3021),
        ("Closed lead count", int(df["IsClosed"].sum()), 245, int(df["IsClosed"].sum()) == 245),
        ("Baseline close rate", float(df["IsClosed"].mean()), 245 / 3021, math.isclose(df["IsClosed"].mean(), 245 / 3021, rel_tol=0, abs_tol=1e-12)),
        ("Status buckets reconcile", int(df[["IsClosed", "IsGoodProgression", "IsBadQuality", "IsUnknown"]].sum().sum()), len(df), int(df[["IsClosed", "IsGoodProgression", "IsBadQuality", "IsUnknown"]].sum().sum()) == len(df)),
        ("Outcome buckets sum to total", int(df["OutcomeBucket"].value_counts().sum()), len(df), int(df["OutcomeBucket"].value_counts().sum()) == len(df)),
        ("LeadKey uniqueness", int(df["LeadKey"].nunique()), len(df), int(df["LeadKey"].nunique()) == len(df)),
        ("PII columns absent downstream", len(PII_COLUMNS & downstream_columns), 0, len(PII_COLUMNS & downstream_columns) == 0),
        ("Sensitive values absent downstream", sensitive_value_count(df), 0, sensitive_value_count(df) == 0),
        ("VendorLeadID absent downstream", int("VendorLeadID" in downstream_columns), 0, "VendorLeadID" not in downstream_columns),
        ("Target closes arithmetic", target_closes, 291, target_closes == 291),
        ("Incremental closes arithmetic", target_closes - int(df["IsClosed"].sum()), 46, target_closes - int(df["IsClosed"].sum()) == 46),
        ("Minimum achieved rate meets target", target_closes / len(df), TARGET_RATE, target_closes / len(df) >= TARGET_RATE),
        ("All target scenarios meet threshold", int(target_scenarios["MeetsTarget"].sum()), len(target_scenarios), bool(target_scenarios["MeetsTarget"].all())),
        ("Widget sizes normalized", int(df["WidgetNameNormalized"].str.contains("300250", regex=False).sum()), 0, int(df["WidgetNameNormalized"].str.contains("300250", regex=False).sum()) == 0),
        ("Source schema includes expected PII", len(PII_COLUMNS & set(raw.columns)), len(PII_COLUMNS), len(PII_COLUMNS & set(raw.columns)) == len(PII_COLUMNS)),
    ]
    qa = pd.DataFrame(checks, columns=["CheckName", "Actual", "Expected", "Passed"])
    qa["Notes"] = ""
    qa.loc[qa["CheckName"].eq("LeadKey uniqueness"), "Notes"] = f"Source vendor IDs: {qa_meta['vendor_id_missing']} missing; {qa_meta['vendor_id_duplicate_values']} duplicated nonblank value."
    qa.loc[qa["CheckName"].eq("PII columns absent downstream"), "Notes"] = "Names, emails, IP, search query, and detailed URL fields removed."
    qa.loc[qa["CheckName"].eq("Sensitive values absent downstream"), "Notes"] = (
        f"Value-level scan passed after redacting {qa_meta['referral_ip_literals_redacted']} IP-literal referral domains."
    )
    return qa


def export_csv(df: pd.DataFrame, filename: str) -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(EXPORT_DIR / filename, index=False, date_format="%Y-%m-%d")


def main() -> None:
    for directory in [SANITIZED_DIR, EXPORT_DIR, QA_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    sheets = pd.ExcelFile(SOURCE_FILE).sheet_names
    raw = pd.read_excel(SOURCE_FILE, sheet_name="Sheet1")
    empty_sheets = {
        sheet: pd.read_excel(SOURCE_FILE, sheet_name=sheet).empty
        for sheet in sheets
        if sheet != "Sheet1"
    }
    clean = load_power_query_clean_leads()
    qa_meta = {
        "source_rows": len(raw),
        "vendor_id_missing": int(raw["VendorLeadID"].isna().sum()),
        "vendor_id_duplicate_rows": int(raw["VendorLeadID"].dropna().duplicated(keep=False).sum()),
        "vendor_id_duplicate_values": int(raw["VendorLeadID"].dropna().duplicated().sum()),
        "lead_key_duplicates": int(clean["LeadKey"].duplicated().sum()),
        "referral_ip_literals_redacted": int(clean["ReferralDomain"].eq("IP literal redacted").sum()),
    }
    weekly = aggregate_trend(clean, "WeekStart")
    monthly = aggregate_trend(clean, "MonthStart")
    tests = trend_tests(clean, monthly)
    segments = segment_performance(clean)
    opportunities = opportunity_inputs(segments)
    target_scenarios = build_target_scenarios(clean, segments)
    coefficients, model_metrics = fit_explanatory_model(clean)
    summary = build_summary(clean, monthly, segments, opportunities)
    qa = build_qa(clean, raw, qa_meta, summary, target_scenarios)

    if not qa["Passed"].all():
        failed = qa.loc[~qa["Passed"], "CheckName"].tolist()
        raise AssertionError(f"QA failed: {failed}")

    # CSV is used instead of Parquet because the bundled runtime has no Parquet engine.
    clean.to_csv(SANITIZED_DIR / "clean_leads.csv", index=False, date_format="%Y-%m-%d")
    export_csv(weekly, "weekly_trends.csv")
    export_csv(monthly, "monthly_trends.csv")
    export_csv(tests, "trend_tests.csv")
    export_csv(segments, "segment_performance.csv")
    export_csv(opportunities, "opportunity_inputs.csv")
    export_csv(target_scenarios, "target_scenarios.csv")
    export_csv(coefficients, "model_coefficients.csv")
    export_csv(model_metrics, "model_metrics.csv")
    export_csv(summary, "analysis_summary.csv")
    qa.to_csv(QA_DIR / "qa_checks.csv", index=False)

    manifest = {
        "source_file": SOURCE_FILE.name,
        "source_sha256": hashlib.sha256(SOURCE_FILE.read_bytes()).hexdigest(),
        "source_sheets": sheets,
        "empty_source_sheets": empty_sheets,
        "source_rows": len(raw),
        "source_columns": len(raw.columns),
        "sanitized_rows": len(clean),
        "sanitized_columns": len(clean.columns),
        "date_min": str(clean["LeadDate"].min().date()),
        "date_max": str(clean["LeadDate"].max().date()),
        "pii_columns_removed": sorted(PII_COLUMNS),
        "vendor_id_quality": qa_meta,
        "cleaning_source": str(WORKBOOK_FILE.relative_to(PROJECT_DIR)),
        "cleaning_sheet": "Clean Leads",
        "power_query": "LeadQualityCleaning",
        "assumptions": {
            "unknown_status_policy": "Blank and unmapped statuses are Unknown and remain in all-lead denominators.",
            "widget_size_normalization": "300250 is normalized to 302252.",
            "target_rate": TARGET_RATE,
            "minimum_segment_n": MIN_SEGMENT_N,
            "reliable_segment_n": RELIABLE_SEGMENT_N,
            "opportunity_overlap": "Dimension scenarios overlap and must not be added together.",
        },
    }
    (QA_DIR / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({
        "rows": len(clean),
        "closed": int(clean["IsClosed"].sum()),
        "close_rate": round(float(clean["IsClosed"].mean()), 6),
        "qa_passed": int(qa["Passed"].sum()),
        "qa_total": len(qa),
        "cleaning_source": str(WORKBOOK_FILE),
    }, indent=2))


if __name__ == "__main__":
    main()
