import pandas as pd
import sys
from dateutil.parser import parse
csv_file = sys.argv[1]
df = pd.read_csv(csv_file)
numeric_cols = []
categorical_cols = []
datetime_cols = []

cat_threshold = 15
datetime_formats = [
    "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d",
    "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"
]
for col in df.columns:
    series = df[col]
    non_null = series.dropna()
    if len(non_null) == 0:
        categorical_cols.append(col)
        continue
    if pd.api.types.is_numeric_dtype(series):
        if series.nunique() <= cat_threshold:
            categorical_cols.append(col)
        else:
            numeric_cols.append(col)
        continue
    is_datetime = False
    if series.dtype == "object":
        for val in non_null:
            try:
                parse(val, fuzzy=False)
            except:
                break
        else:
            is_datetime = True
    
    if is_datetime:
        datetime_cols.append(col)
        continue
    categorical_cols.append(col)
print("Column Type Counts:")
print("Numerical:", len(numeric_cols))
print("Categorical:", len(categorical_cols))
print("Datetime:", len(datetime_cols))

print("\nColumns by Type:")
print("Numerical Columns:", numeric_cols)
print("Categorical Columns:", categorical_cols)
print("Datetime Columns:", datetime_cols)