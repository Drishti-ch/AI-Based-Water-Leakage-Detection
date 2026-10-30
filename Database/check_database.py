from sqlalchemy import inspect, text
from database import engine


inspector = inspect(engine)

tables = inspector.get_table_names()

print("\nTables in database:")
for table in tables:
    print("-", table)


print("\nRow counts:")

with engine.connect() as connection:

    for table in tables:

        count = connection.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        ).scalar()

        print(f"{table}: {count} rows")


print("\nPrediction status counts:")

with engine.connect() as connection:

    result = connection.execute(
        text("""
            SELECT status, COUNT(*) 
            FROM leakage_predictions
            GROUP BY status
        """)
    )

    for status, count in result:
        print(f"{status}: {count}")


print("\nDatabase verification completed successfully.")