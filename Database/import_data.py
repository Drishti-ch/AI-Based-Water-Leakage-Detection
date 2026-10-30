import os

import pandas as pd
from sqlalchemy import text
from database import engine


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

excel_file = os.path.join(BASE_DIR, "Data", "2018_SCADA.xlsx")

sheets = {
    "pressure": "pressure_readings",
    "demand ": "demand_readings",
    "flow_rate": "flow_readings",
    "water_level": "water_level_readings"
}


for sheet_name, table_name in sheets.items():

    print(f"\nReading {sheet_name} sheet...")

    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name
    )

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert timestamp column
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(
            df["Timestamp"],
            errors="coerce"
        )

    print(f"Rows found: {len(df)}")
    print(f"Columns found: {len(df.columns)}")

    print(f"Storing data in table: {table_name}")

    df.to_sql(
        table_name,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=5000
    )

    with engine.begin() as connection:
        connection.execute(text(
            f'CREATE INDEX IF NOT EXISTS "ix_{table_name}_timestamp" '
            f'ON "{table_name}" ("Timestamp")'
        ))

    print(f"{table_name} imported successfully.")


print("\nAll SCADA data imported successfully.")
