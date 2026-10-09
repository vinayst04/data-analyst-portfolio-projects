"""Prepare a privacy-safe staging file for Excel Power Query.

Python is intentionally limited to the privacy steps that must happen before
the data enters Excel. The remaining cleaning is performed in Power Query.
"""

import hashlib
import ipaddress
from pathlib import Path

import pandas as pd


PROJECT_FOLDER = Path(__file__).resolve().parents[1]
SOURCE_FILE = PROJECT_FOLDER / "data" / "source" / "Analyst_case_study_dataset_1.xls"
STAGING_FILE = PROJECT_FOLDER / "data" / "sanitized" / "sanitized_staging.csv"

SENSITIVE_COLUMNS = [
    "FirstName",
    "Email",
    "IP Address",
    "ReferralURL",
    "ReferralURL Parameters",
    "LandingPageURL",
    "Landing Page URL Parameters",
    "SearchQuery",
]


def is_ip_address(value):
    """Return True when the complete value is an IP address."""
    if pd.isna(value):
        return False

    try:
        ipaddress.ip_address(str(value).strip())
        return True
    except ValueError:
        return False


def create_lead_key(row):
    """Create a repeatable anonymous identifier without exposing VendorLeadID."""
    key_parts = [
        str(row["SourceRowNumber"]),
        pd.Timestamp(row["LeadCreated"]).isoformat(),
        str(row.get("VendorLeadID", "")),
        str(row.get("WidgetName", "")),
        str(row.get("CallStatus", "")),
    ]
    combined_value = "|".join(key_parts)
    digest = hashlib.sha256(combined_value.encode("utf-8")).hexdigest()
    return "LQ-" + digest[:16].upper()


def main():
    # 1. Load the recruiter-supplied worksheet without changing the source file.
    source = pd.read_excel(SOURCE_FILE, sheet_name="Sheet1")
    source["SourceRowNumber"] = range(2, len(source) + 2)

    # 2. Create an anonymous key before removing the original vendor identifier.
    source["LeadKey"] = source.apply(create_lead_key, axis=1)

    # 3. Remove direct identifiers and free-text URL/search fields.
    staging = source.drop(columns=SENSITIVE_COLUMNS)
    staging = staging.drop(columns=["VendorLeadID", "SourceRowNumber"])

    # 4. Redact IP literals that appear inside the otherwise useful domain field.
    ip_mask = staging["ReferralDomain"].apply(is_ip_address)
    redacted_ip_count = int(ip_mask.sum())
    staging.loc[ip_mask, "ReferralDomain"] = "IP literal redacted"

    # Put the anonymous key first so it is easy to find in Power Query.
    ordered_columns = ["LeadKey"] + [
        column for column in staging.columns if column != "LeadKey"
    ]
    staging = staging[ordered_columns]

    # 5. Save the privacy-safe input used by Excel Power Query.
    STAGING_FILE.parent.mkdir(parents=True, exist_ok=True)
    staging.to_csv(STAGING_FILE, index=False, date_format="%Y-%m-%d %H:%M:%S")

    # Simple checks that are easy to explain.
    assert len(staging) == 3021
    assert staging["LeadKey"].nunique() == len(staging)
    assert not any(column in staging.columns for column in SENSITIVE_COLUMNS)
    assert "VendorLeadID" not in staging.columns
    assert not staging["ReferralDomain"].apply(is_ip_address).any()

    print("Privacy-safe rows:", len(staging))
    print("Sensitive columns removed:", len(SENSITIVE_COLUMNS))
    print("IP values redacted:", redacted_ip_count)
    print("Staging file:", STAGING_FILE)
    print("The remaining cleaning is performed in Excel Power Query.")


if __name__ == "__main__":
    main()
