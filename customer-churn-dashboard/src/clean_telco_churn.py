import pandas as pd


raw_file = "data/raw/telco_churn.csv"
clean_file = "data/processed/telco_churn_clean.csv"


df = pd.read_csv(raw_file)

df = df.rename(columns={
    "customerID": "customer_id",
    "SeniorCitizen": "senior_citizen",
    "PhoneService": "phone_service",
    "MultipleLines": "multiple_lines",
    "InternetService": "internet_service",
    "OnlineSecurity": "online_security",
    "OnlineBackup": "online_backup",
    "DeviceProtection": "device_protection",
    "TechSupport": "tech_support",
    "StreamingTV": "streaming_tv",
    "StreamingMovies": "streaming_movies",
    "PaperlessBilling": "paperless_billing",
    "PaymentMethod": "payment_method",
    "MonthlyCharges": "monthly_charges",
    "TotalCharges": "total_charges",
    "Churn": "churn",
})

df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce")
df["total_charges"] = df["total_charges"].fillna(0)

df["churn_flag"] = df["churn"].map({"Yes": 1, "No": 0})
df["is_senior"] = df["senior_citizen"].map({1: "Senior", 0: "Non-Senior"})

tenure_groups = []
for tenure in df["tenure"]:
    if tenure <= 6:
        tenure_groups.append("0-6 Months")
    elif tenure <= 12:
        tenure_groups.append("7-12 Months")
    elif tenure <= 24:
        tenure_groups.append("13-24 Months")
    elif tenure <= 48:
        tenure_groups.append("25-48 Months")
    else:
        tenure_groups.append("49+ Months")

df["tenure_group"] = tenure_groups

charge_groups = []
for monthly_charge in df["monthly_charges"]:
    if monthly_charge <= 35:
        charge_groups.append("Low Charge")
    elif monthly_charge <= 70:
        charge_groups.append("Medium Charge")
    else:
        charge_groups.append("High Charge")

df["charge_group"] = charge_groups

df["monthly_revenue_at_risk"] = df["monthly_charges"] * df["churn_flag"]
df["annual_revenue_at_risk"] = df["monthly_revenue_at_risk"] * 12

final_columns = [
    "customer_id",
    "gender",
    "senior_citizen",
    "is_senior",
    "Partner",
    "Dependents",
    "tenure",
    "tenure_group",
    "phone_service",
    "multiple_lines",
    "internet_service",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
    "Contract",
    "paperless_billing",
    "payment_method",
    "monthly_charges",
    "charge_group",
    "total_charges",
    "churn",
    "churn_flag",
    "monthly_revenue_at_risk",
    "annual_revenue_at_risk",
]

df = df[final_columns]
df = df.rename(columns={
    "Partner": "partner",
    "Dependents": "dependents",
    "Contract": "contract",
})

df.to_csv(clean_file, index=False)


print("Clean data saved:", clean_file)
print("Rows:", len(df))
print("Churn rate:", round(df["churn_flag"].mean() * 100, 2), "%")
