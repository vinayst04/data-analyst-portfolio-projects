import pandas as pd


raw_file = "data/raw/superstore.csv"
clean_file = "data/processed/superstore_clean.csv"


df = pd.read_csv(raw_file, encoding="latin1")

df.columns = df.columns.str.strip()
df.columns = df.columns.str.lower()
df.columns = df.columns.str.replace(" ", "_")
df.columns = df.columns.str.replace("-", "_")

df["order_date"] = pd.to_datetime(df["order_date"], format="%m/%d/%Y")
df["ship_date"] = pd.to_datetime(df["ship_date"], format="%m/%d/%Y")

df["postal_code"] = df["postal_code"].astype(str)
df["year"] = df["order_date"].dt.year
df["month"] = df["order_date"].dt.month
df["year_month"] = df["order_date"].dt.strftime("%Y-%m")
df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days
df["profit_margin"] = df["profit"] / df["sales"]

discount_bands = []
for discount in df["discount"]:
    if discount == 0:
        discount_bands.append("No Discount")
    elif discount <= 0.10:
        discount_bands.append("Low Discount")
    elif discount <= 0.30:
        discount_bands.append("Medium Discount")
    else:
        discount_bands.append("High Discount")

df["discount_band"] = discount_bands

df.to_csv(clean_file, index=False)


print("Rows:", len(df))
