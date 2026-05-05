import pandas as pd
import numpy as np

range_date = pd.date_range('2026-01-01', '2026-05-05').date


full_trans_list = []
for transaction_date in range_date:

    # Số lượng giao dịch của ngày
    transaction_count_day = np.random.choice(range(30,90))

    for trans in range(transaction_count_day):
        store_id = np.random.choice(["S"+str(i) for i in range(1,11)])
        product_id = np.random.choice(["P"+str(i) for i in range(100,106)])
        quantity = np.random.choice(range(1,10))

        # Giao dịch
        transaction_info = [store_id, product_id, quantity, transaction_date]
        full_trans_list.append(transaction_info)

df = pd.DataFrame(
    data = full_trans_list,
    index = range(1,len(full_trans_list)+1),
    columns = ["store_id", "product_id", "quantity", "transaction_date"]
)


products_df = pd.DataFrame(
    [
        ["P100", "Drink", 10],
        ["P101", "Noodle", 30],
        ["P102", "Snack", 12],
        ["P103", "Cake", 20],
        ["P104", "Scream", 15],
        ["P105", "Chicken", 15]
    ],
    columns = ["product_id", "category", "price"]
)

df_merged = df.merge(products_df, on="product_id", how="left")

df_merged['transaction_id'] = range(1,len(df_merged)+1)

full_df = df_merged[["transaction_id", "store_id", "product_id", "category", "quantity", "price", "transaction_date"]]


# Ghi dữ liệu
from pathlib import Path

BASE_PATH = Path("/Users/trung/Desktop/demo_spark_docker")
CSV_FOLDER = "my_csv"
Path.mkdir(BASE_PATH / CSV_FOLDER)
CSV_FILE = "transactions_data.csv"
CSV_PATH = BASE_PATH / CSV_FOLDER / CSV_FILE

full_df.to_csv(CSV_PATH, index=False,)