import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from Model.data_utils import FEATURES, load_sensor_data


print("Loading and validating data from SQLite database...")
data = load_sensor_data()
X = data[FEATURES]


print("\nTraining Isolation Forest model...")

model = Pipeline(
    steps=[
        ("scaler", StandardScaler()),
        ("detector", IsolationForest(
            n_estimators=200,
            contamination=0.05,
            random_state=42,
            n_jobs=-1
        ))
    ]
)

# Temporal holdout validation prevents evaluating only on the training rows.
split_at = max(int(len(X) * 0.8), 1)
validation_model = Pipeline(steps=[
    ("scaler", StandardScaler()),
    ("detector", IsolationForest(
        n_estimators=200, contamination=0.05, random_state=42, n_jobs=-1
    ))
])
validation_model.fit(X.iloc[:split_at])
validation_predictions = validation_model.predict(X.iloc[split_at:])
print(f"Temporal validation rows: {len(validation_predictions):,}")
print(f"Temporal validation anomalies: {(validation_predictions == -1).sum():,}")

# Fit the production model on all validated historical data.
model.fit(X)


# Generate anomaly predictions
data["prediction"] = model.predict(X)
data["anomaly_score"] = model.decision_function(X)

# Isolation Forest:
#  1  = normal
# -1  = anomaly

data["status"] = data["prediction"].map({
    1: "Normal",
    -1: "Potential Leakage"
})


# Save model
model_path = os.path.join(
    os.path.dirname(__file__),
    "leakage_model.pkl"
)

joblib.dump(model, model_path)


print("\nModel training completed successfully.")

print("\nPrediction summary:")
print(data["status"].value_counts())

print(f"\nModel saved at: {model_path}")
