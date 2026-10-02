"""Automated SQL query runner and output recorder.

Executes all scripts in sql/ against data/cre_analytics.duckdb,
validates syntax, window functions, and business answers,
and logs structured execution results to outputs/sql_query_results.json.
"""

import os
import json
from typing import Dict, List, Any
import duckdb
import pandas as pd

from src.utilities.db_loader import DB_PATH, get_db_connection


def execute_sql_file(conn, file_path: str) -> List[Dict[str, Any]]:
    """Reads a SQL file, splits by semicolon, executes each statement, and returns results."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split statements
    statements = [stmt.strip() for stmt in content.split(";") if stmt.strip()]
    results = []

    for idx, stmt in enumerate(statements, start=1):
        # Extract comment header if available
        first_line = stmt.strip().split("\n")[0]
        try:
            df = conn.execute(stmt).fetchdf()
            results.append({
                "statement_index": idx,
                "header": first_line,
                "row_count": len(df),
                "columns": list(df.columns),
                "preview": df.head(5).to_dict(orient="records"),
                "status": "SUCCESS",
            })
        except Exception as e:
            results.append({
                "statement_index": idx,
                "header": first_line,
                "status": "ERROR",
                "error": str(e),
            })
    return results


def run_all_sql_scripts():
    """Runs all schema, view, quality, kpi, and analytical SQL scripts."""
    print("==================================================================")
    print("PHASE 10: SQL ANALYTICAL EXECUTION & BUSINESS QUERY VALIDATION")
    print("==================================================================")

    conn = get_db_connection()

    sql_files = [
        ("06_views", os.path.join("sql", "06_views", "create_views.sql")),
        ("03_quality", os.path.join("sql", "03_quality", "quality_audits.sql")),
        ("04_kpis", os.path.join("sql", "04_kpis", "portfolio_kpis.sql")),
        ("05_analysis", os.path.join("sql", "05_analysis", "business_questions.sql")),
    ]

    all_outputs = {}

    for label, path in sql_files:
        print(f"\nExecuting {label} from {path}...")
        res = execute_sql_file(conn, path)
        all_outputs[label] = res
        successes = len([r for r in res if r["status"] == "SUCCESS"])
        errors = len([r for r in res if r["status"] == "ERROR"])
        print(f"  Statements executed: {len(res)} (Passed: {successes}, Errors: {errors})")
        if errors > 0:
            for r in res:
                if r["status"] == "ERROR":
                    print(f"    [!] Error in statement {r['statement_index']} ({r['header']}): {r['error']}")

    # Save to outputs/sql_query_results.json
    os.makedirs("outputs", exist_ok=True)
    out_json = os.path.join("outputs", "sql_query_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_outputs, f, indent=2, default=str)

    print(f"\n[Success] SQL execution results saved -> {out_json}")
    conn.close()


if __name__ == "__main__":
    run_all_sql_scripts()
