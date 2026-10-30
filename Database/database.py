import os
from sqlalchemy import create_engine

# Database file always lives in <project_root>/Database/water_leakage.db
# regardless of the directory the scripts are run from.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "water_leakage.db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False
)

if __name__ == "__main__":
    print(f"SQLite database configured at: {DB_PATH}")
