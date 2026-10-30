import pandas as pd
from sqlalchemy import text
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Database.database import engine


print("Reading data from SQLite database...")

# Read flow data
flow_df = pd.read_sql(
    text("SELECT * FROM flow_readings"),
    engine
)

# Read water level data
water_df = pd.read_sql(
    text("SELECT * FROM water_level_readings"),
    engine
)

# Read selected pressure sensors
pressure_df = pd.read_sql(
    text("""
        SELECT Timestamp, n1, n4, n31, n54
        FROM pressure_readings
    """),
    engine
)


print("Data loaded successfully.")

print("\nFlow data:", flow_df.shape)
print("Water level data:", water_df.shape)
print("Pressure data:", pressure_df.shape)


# Convert timestamps
flow_df["Timestamp"] = pd.to_datetime(flow_df["Timestamp"])
water_df["Timestamp"] = pd.to_datetime(water_df["Timestamp"])
pressure_df["Timestamp"] = pd.to_datetime(pressure_df["Timestamp"])


# Merge datasets using Timestamp
data = flow_df.merge(
    water_df,
    on="Timestamp",
    how="inner"
)

data = data.merge(
    pressure_df,
    on="Timestamp",
    how="inner"
)


# Sort by time
data = data.sort_values("Timestamp")


# Remove missing values
data = data.dropna()


print("\nCombined dataset shape:", data.shape)

print("\nColumns used for ML:")
print(data.columns.tolist())

print("\nMissing values:")
print(data.isnull().sum())

print("\nPreprocessing completed successfully.")