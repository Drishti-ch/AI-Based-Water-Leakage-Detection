# 💧 AI-Based Water Leakage Detection

AI-powered anomaly detection for water SCADA sensor monitoring.

This project merges flow, pressure and water level readings, runs an **Isolation Forest** model over them to flag potential leaks, stores the results in **SQLite**, and presents everything in an interactive **Streamlit** dashboard.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![scikit-learn](https://img.shields.io/badge/scikit--learn-Isolation%20Forest-orange)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red)

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Getting Started](#-getting-started)
- [Running the Pipeline](#-running-the-pipeline)
- [Launching the Dashboard](#-launching-the-dashboard)
- [Model Details](#-model-details)
- [Dataset](#-dataset)

---

## 🔎 Overview

Water distribution networks generate large volumes of SCADA sensor data. This project turns the 2018 SCADA dataset into a simple end-to-end pipeline:

1. Load the raw Excel data into a SQLite database.
2. Merge and clean the flow, water level and pressure sensor data.
3. Train an Isolation Forest model to learn what normal behaviour looks like.
4. Label every reading as **Normal** or **Potential Leakage**.
5. Explore the results through a Streamlit dashboard.

---

## ✨ Features

**Data and model pipeline**
- Imports about 420k rows from Excel into SQLite
- Merges flow, water level and four pressure sensors on `Timestamp`
- Cleans missing values before modelling
- Trains and saves an Isolation Forest model (`.pkl`)
- Stores predictions in a dedicated `leakage_predictions` table
- Includes a database verification utility

**Dashboard**
- KPI overview: total, normal and potential leakage readings, plus anomaly rate
- Current system status based on the latest reading
- Latest sensor readings (flow, pressure, water level)
- Detection summary and anomaly trend over time
- Time-series charts for flow, pressure and water level
- Potential leakage alerts table
- CSV export of detection results
- Date-range filter applied across all charts

---

## 🧰 Tech Stack

| Area | Technology |
|---|---|
| Language | Python 3.14 |
| Machine learning | scikit-learn (Isolation Forest) |
| Data handling | pandas, SQLAlchemy |
| Database | SQLite |
| Dashboard | Streamlit |

---

## 📁 Project Structure

```
AI-Based-Water-Leakage-Detection/
├── Data/
│   └── 2018_SCADA.xlsx        # Raw SCADA sensor data (4 sheets)
├── Database/
│   ├── database.py            # SQLite engine configuration
│   ├── import_data.py         # Excel -> SQLite import
│   └── check_database.py      # Database verification utility
├── Model/
│   ├── preprocess.py          # Merge & clean sensor data
│   ├── train_model.py         # Train Isolation Forest, save .pkl
│   ├── save_predictions.py    # Run model -> leakage_predictions table
│   └── leakage_model.pkl      # Trained model
├── Dashboard/
│   └── app.py                 # Streamlit dashboard
├── requirements.txt
└── README.md
```

---

## ⚙️ How It Works

1. **Data ingestion**: four Excel sheets (pressure, demand, flow rate, water level) are loaded into SQLite tables with 105,120 rows each.
2. **Preprocessing**: flow, water level and four pressure sensors are inner-joined on `Timestamp` and cleaned of missing values.
3. **Model**: an `IsolationForest(n_estimators=100, contamination=0.05)` is trained on 8 features. Output: `1` = Normal, `-1` = Potential Leakage.
4. **Storage**: predictions are written to the `leakage_predictions` table.
5. **Visualization**: the Streamlit dashboard reads all tables and renders KPIs, charts and alert lists.

```
Excel (SCADA) → SQLite → Merge & Clean → Isolation Forest → leakage_predictions → Dashboard
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.14
- pip

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd AI-Based-Water-Leakage-Detection

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Running the Pipeline

Run the steps in this order:

```bash
python Database/import_data.py     # 1. Import Excel -> SQLite (420k rows)
python Model/preprocess.py         # 2. Merge + clean sensor data
python Model/train_model.py        # 3. Train Isolation Forest
python Model/save_predictions.py   # 4. Save predictions to SQLite
python Database/check_database.py  # 5. Verify database contents
```

---

## 📊 Launching the Dashboard

```bash
streamlit run Dashboard/app.py
```

Then open **http://localhost:8501** in your browser.

---

## 🧠 Model Details

| Setting | Value |
|---|---|
| Algorithm | Isolation Forest |
| `n_estimators` | 100 |
| `contamination` | 0.05 |
| Features (8) | `p227`, `p235`, `PUMP_1`, `T1`, `n1`, `n4`, `n31`, `n54` |
| Output | `1` = Normal, `-1` = Potential Leakage |

---

## 🗂️ Dataset

`Data/2018_SCADA.xlsx` contains four sheets: **pressure**, **demand**, **flow rate** and **water level**. Each sheet has 105,120 rows, and about 420k rows are imported in total.
