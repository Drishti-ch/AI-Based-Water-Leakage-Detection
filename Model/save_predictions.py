import pandas as pd
import joblib
from sqlalchemy import text
from datetime import datetime, timezone

import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from Database.database import engine
from Model.data_utils import FEATURES, load_sensor_data


print("Loading and validating sensor data from SQLite...")
data = load_sensor_data()
X = data[FEATURES]


# Load trained model
model_path = os.path.join(
    os.path.dirname(__file__),
    "leakage_model.pkl"
)

model = joblib.load(model_path)

print("Trained model loaded successfully.")


# Generate predictions
data["prediction"] = model.predict(X)
data["anomaly_score"] = model.decision_function(X)


# Convert model output to readable status
data["status"] = data["prediction"].map({
    1: "Normal",
    -1: "Potential Leakage"
})


# Keep only useful columns for the prediction table
predictions = data[
    ["Timestamp", "prediction", "status", "anomaly_score"]
].copy()

predictions["model_version"] = "isolation_forest_v2"
predictions["predicted_at"] = datetime.now(timezone.utc).isoformat()

# Group consecutive anomalies into alert events to reduce one-reading noise.
predictions["anomaly_event_id"] = (
    predictions["status"].ne("Potential Leakage").cumsum()
)
predictions.loc[predictions["status"] == "Normal", "anomaly_event_id"] = None


# Save predictions to SQLite
predictions.to_sql(
    "leakage_predictions",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=5000
)

# Preserve each run for auditability while keeping leakage_predictions as the
# current snapshot consumed by the dashboard.
predictions.to_sql(
    "leakage_predictions_history",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000
)

with engine.begin() as connection:
    connection.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_leakage_predictions_timestamp "
        "ON leakage_predictions (Timestamp)"
    ))
    connection.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_leakage_predictions_status "
        "ON leakage_predictions (status)"
    ))


print("\nPredictions saved successfully.")

print("\nPrediction summary:")
print(predictions["status"].value_counts())

print("\nSQLite table created:")
print("leakage_predictions")

print("\nPrediction storage completed successfully.")
