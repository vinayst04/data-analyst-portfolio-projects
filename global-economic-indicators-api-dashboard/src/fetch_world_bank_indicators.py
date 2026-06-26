import requests
import pandas as pd
import json


processed_folder = "data/processed"


START_YEAR = 2014
END_YEAR = 2024

country_codes = "IND;USA;CHN;DEU;GBR;JPN;BRA;ZAF"

indicators = {
    "NY.GDP.MKTP.CD": ["GDP Current US$", "GDP", "current US$", "currency"],
    "NY.GDP.MKTP.KD.ZG": ["GDP Growth %", "GDP Growth", "annual %", "percent"],
    "FP.CPI.TOTL.ZG": ["Inflation %", "Inflation", "annual %", "percent"],
    "SL.UEM.TOTL.ZS": ["Unemployment %", "Unemployment", "% of labor force", "percent"],
    "SP.POP.TOTL": ["Population", "Population", "people", "number"],
    "IT.NET.USER.ZS": ["Internet Users %", "Internet Users", "% of population", "percent"],
    "SP.DYN.LE00.IN": ["Life Expectancy", "Life Expectancy", "years", "number"],
}

country_metadata = [
    ["IND", "India", "South Asia", "Lower middle income", "New Delhi", 77.225, 28.6353],
    ["USA", "United States", "North America", "High income", "Washington D.C.", -77.032, 38.8895],
    ["CHN", "China", "East Asia & Pacific", "Upper middle income", "Beijing", 116.286, 40.0495],
    ["DEU", "Germany", "Europe & Central Asia", "High income", "Berlin", 13.4115, 52.5235],
    ["GBR", "United Kingdom", "Europe & Central Asia", "High income", "London", -0.126236, 51.5002],
    ["JPN", "Japan", "East Asia & Pacific", "High income", "Tokyo", 139.77, 35.67],
    ["BRA", "Brazil", "Latin America & Caribbean", "Upper middle income", "Brasilia", -47.9292, -15.7801],
    ["ZAF", "South Africa", "Sub-Saharan Africa", "Upper middle income", "Pretoria", 28.1871, -25.746],
]

country_metadata_df = pd.DataFrame(
    country_metadata,
    columns=["country_code", "country_name", "region", "income_level", "capital_city", "longitude", "latitude"],
)

all_rows = []

for indicator_code, details in indicators.items():
    short_name = details[0]
    dashboard_name = details[1]
    unit = details[2]
    format_type = details[3]

    url = (
        f"https://api.worldbank.org/v2/country/{country_codes}/indicator/{indicator_code}"
        f"?format=json&date={START_YEAR}:{END_YEAR}&per_page=20000"
    )

    response = requests.get(url, timeout=60)
    data = response.json()


    for item in data[1]:
        all_rows.append({
            "country_code": item["countryiso3code"],
            "country_name": item["country"]["value"],
            "indicator_code": indicator_code,
            "short_name": short_name,
            "dashboard_name": dashboard_name,
            "unit": unit,
            "format_type": format_type,
            "year": int(item["date"]),
            "value": item["value"],
        })


world_bank_df = pd.DataFrame(all_rows)
world_bank_df["value"] = pd.to_numeric(world_bank_df["value"], errors="coerce")
world_bank_df = world_bank_df.sort_values(["country_name", "short_name", "year"])

latest_df = (
    world_bank_df
    .dropna(subset=["value"])
    .sort_values("year")
    .drop_duplicates(["country_code", "indicator_code"], keep="last")
    .rename(columns={"year": "latest_year"})
)

wide_column_order = [
    "GDP",
    "GDP Growth",
    "Inflation",
    "Internet Users",
    "Life Expectancy",
    "Population",
    "Unemployment",
]

wide_df = (
    world_bank_df
    .pivot_table(
        index=["country_code", "country_name", "year"],
        columns="dashboard_name",
        values="value",
        aggfunc="first",
    )
    .reset_index()
)

wide_df.columns.name = None
wide_df = wide_df.reindex(columns=["country_code", "country_name", "year"] + wide_column_order)
wide_df["Population"] = wide_df["Population"].astype("Int64")

indicator_metadata_df = pd.DataFrame([
    {
        "indicator_code": indicator_code,
        "short_name": details[0],
        "dashboard_name": details[1],
        "unit": details[2],
        "format_type": details[3],
    }
    for indicator_code, details in indicators.items()
])

world_bank_df.to_csv(processed_folder + "/world_bank_indicators_clean.csv", index=False)
latest_df.to_csv(processed_folder + "/world_bank_latest_indicators.csv", index=False)
wide_df.to_csv(processed_folder + "/country_year_indicators_wide.csv", index=False)
country_metadata_df.to_csv(processed_folder + "/country_metadata.csv", index=False)
indicator_metadata_df.to_csv(processed_folder + "/indicator_metadata.csv", index=False)


print("Total rows:", len(world_bank_df))
print("Countries:", world_bank_df["country_name"].nunique())
print("Indicators:", world_bank_df["indicator_code"].nunique())
