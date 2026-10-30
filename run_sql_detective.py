import sqlite3
from pathlib import Path

# Locate the SQL file and database in the same directory as this script.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sql_detective.db"
SQL_PATH = BASE_DIR / "sql_detective.sql"


def run_queries():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        # Read all queries from the submission SQL file.
        with open(SQL_PATH, "r", encoding="utf-8") as file:
            sql_script = file.read()

        # Split the script into individual SQL statements.
        queries = [
            query.strip()
            for query in sql_script.split(";")
            if query.strip()
        ]

        if not queries:
            print("No SQL queries found in sql_detective.sql.")
            return

        # Execute and display the result of each query.
        cursor = connection.cursor()

        for index, query in enumerate(queries, start=1):
            print(f"\n{'=' * 50}")
            print(f"QUERY {index}")
            print("=" * 50)

            cursor.execute(query)
            results = cursor.fetchall()

            if results:
                for row in results:
                    print(dict(row))
            else:
                print("No results found.")

        print(f"\nSuccessfully executed {len(queries)} queries.")

    finally:
        connection.close()


if __name__ == "__main__":
    run_queries()
