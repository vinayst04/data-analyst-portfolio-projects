import pandas as pd


raw_folder = "data/raw"

files = [
    ["olist_customers", "olist_customers_dataset.csv"],
    ["olist_orders", "olist_orders_dataset.csv"],
    ["olist_order_items", "olist_order_items_dataset.csv"],
    ["olist_order_payments", "olist_order_payments_dataset.csv"],
    ["olist_order_reviews", "olist_order_reviews_dataset.csv"],
    ["olist_products", "olist_products_dataset.csv"],
    ["olist_sellers", "olist_sellers_dataset.csv"],
    ["product_category_translation", "product_category_name_translation.csv"],
]

for table_name, file_name in files:
    df = pd.read_csv(raw_folder + "/" + file_name)
    print(table_name, "rows:", len(df))

print("CSV files checked. Import these CSV files manually into MySQL Workbench.")
