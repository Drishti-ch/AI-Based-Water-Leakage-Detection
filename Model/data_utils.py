import os
import sys

import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Database.database import engine


FEATURES = ["p227", "p235", "PUMP_1", "T1", "n1", "n4", "n31", "n54"]


def load_sensor_data():
    flow = pd.read_sql(text("SELECT * FROM flow_readings"), engine)
    water = pd.read_sql(text("SELECT Timestamp, T1 FROM water_level_readings"), engine)
    pressure = pd.read_sql(
        text("SELECT Timestamp, n1, n4, n31, n54 FROM pressure_readings"), engine
    )

    frames = [flow, water, pressure]
    for frame in frames:
        if "Timestamp" not in frame.columns:
            raise ValueError("Every sensor table must contain a Timestamp column.")
        frame["Timestamp"] = pd.to_datetime(frame["Timestamp"], errors="coerce")
        if frame["Timestamp"].isna().any():
            raise ValueError("Invalid timestamps found in sensor data.")
        if frame["Timestamp"].duplicated().any():
            raise ValueError("Duplicate timestamps found in sensor data.")

    data = flow.merge(water, on="Timestamp", how="inner")
    data = data.merge(pressure, on="Timestamp", how="inner")
    data = data.sort_values("Timestamp")

    missing_features = [column for column in FEATURES if column not in data.columns]
    if missing_features:
        raise ValueError(f"Missing required model features: {missing_features}")

    data = data.dropna(subset=FEATURES).reset_index(drop=True)
    if data.empty:
        raise ValueError("No usable sensor rows remain after cleaning.")

    return data
