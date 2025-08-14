import sqlite3
import pandas as pd

# Load CSV (use local file instead of Google Drive for reliability)
df = pd.read_csv("Dataset_Statathon_CSV.csv")

# Save to SQLite
conn = sqlite3.connect("nfhs.db")  # Changed from data.db to nfhs.db
df.to_sql("nfhs_data", conn, if_exists="replace", index=False)  # Fixed table name
conn.close()
print("Database successfully created with these columns:")
print(df.columns.tolist())
