"""Database loading and SQL management utility.

Initializes the local relational analytics database (DuckDB / SQLite),
creates tables from DDL, loads clean CSV datasets, and validates referential integrity.
"""

import os
import duckdb
import pandas as pd


DB_PATH = os.path.join("data", "cre_analytics.duckdb")


def get_db_connection():
    """Returns a connected DuckDB database connection."""
    return duckdb.connect(DB_PATH)


def initialize_and_load_db():
    """Initializes tables from DDL and ingests validated clean data."""
    print("==================================================================")
    print("PHASE 9: DATABASE INITIALIZATION & RELATIONAL SCHEMA LOADING")
    print("==================================================================")

    # Remove stale DB if exists
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass

    conn = get_db_connection()

    # Read DDL
    ddl_path = os.path.join("sql", "01_schema", "create_schema.sql")
    print(f"\nExecuting DDL from {ddl_path}...")
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl_sql = f.read()

    # DuckDB handles ANSI SQL statements separated by semicolons
    statements = [stmt.strip() for stmt in ddl_sql.split(";") if stmt.strip()]
    for stmt in statements:
        # Ignore unsupported DDL flags if any
        try:
            conn.execute(stmt)
        except Exception as e:
            print(f"  Note during DDL execution: {e}")

    # Load data from data/clean/
    clean_dir = os.path.join("data", "clean")
    tables_to_load = [
        ("dim_geography", "dim_geography.csv"),
        ("dim_facility_type", "dim_facility_type.csv"),
        ("dim_property", "dim_property.csv"),
        ("dim_lease", "dim_lease.csv"),
        ("dim_floor", "dim_floor.csv"),
        ("dim_space", "dim_space.csv"),
        ("dim_date", "dim_date.csv"),
        ("fact_daily_workplace_utilization", "fact_daily_workplace_utilization.csv"),
        ("fact_room_utilization", "fact_room_utilization.csv"),
        ("fact_monthly_property_cost", "fact_monthly_property_cost.csv"),
        ("fact_headcount", "fact_headcount.csv"),
        ("fact_data_quality", "fact_data_quality.csv"),
    ]

    print("\nIngesting validated clean CSVs into relational tables...")
    for table_name, csv_file in tables_to_load:
        csv_path = os.path.join(clean_dir, csv_file).replace("\\", "/")
        # Use DuckDB native high-speed CSV reader
        insert_sql = f"INSERT INTO {table_name} SELECT * FROM read_csv_auto('{csv_path}')"
        conn.execute(insert_sql)
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"  Loaded {table_name:<34} : {count:,} records")

    # Verify referential integrity
    print("\nVerifying relational foreign key integrity...")
    fk_checks = [
        ("fact_daily_workplace_utilization -> dim_property",
         "SELECT COUNT(*) FROM fact_daily_workplace_utilization u WHERE NOT EXISTS (SELECT 1 FROM dim_property p WHERE p.PropertyKey = u.PropertyKey)"),
        ("fact_daily_workplace_utilization -> dim_space",
         "SELECT COUNT(*) FROM fact_daily_workplace_utilization u WHERE NOT EXISTS (SELECT 1 FROM dim_space s WHERE s.SpaceKey = u.SpaceKey)"),
        ("fact_monthly_property_cost -> dim_property",
         "SELECT COUNT(*) FROM fact_monthly_property_cost c WHERE NOT EXISTS (SELECT 1 FROM dim_property p WHERE p.PropertyKey = c.PropertyKey)"),
        ("dim_property -> dim_geography",
         "SELECT COUNT(*) FROM dim_property p WHERE NOT EXISTS (SELECT 1 FROM dim_geography g WHERE g.GeographyKey = p.GeographyKey)"),
    ]

    all_passed = True
    for label, query in fk_checks:
        orphan_count = conn.execute(query).fetchone()[0]
        if orphan_count == 0:
            print(f"  [PASSED] {label} (0 orphans)")
        else:
            print(f"  [FAILED] {label} ({orphan_count} orphans found!)")
            all_passed = False

    conn.close()
    if all_passed:
        print("\nDatabase initialization, schema constraints, and data loading successful.")
    else:
        raise ValueError("Referential integrity checks failed during relational loading.")


if __name__ == "__main__":
    initialize_and_load_db()
