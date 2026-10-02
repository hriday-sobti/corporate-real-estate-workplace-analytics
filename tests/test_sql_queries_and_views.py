"""SQL Queries, Views, and Relational Database Tests.

Tests:
- All 7 analytical views exist and return populated datasets
- All 16 business analytical SQL queries return valid row counts with 0 errors
- Zero orphaned foreign keys across the database
"""

import os
import json
import pytest
import duckdb

DB_PATH = os.path.join("data", "cre_analytics.duckdb")
RESULTS_JSON = os.path.join("outputs", "sql_query_results.json")


@pytest.fixture(scope="module")
def db_conn():
    conn = duckdb.connect(DB_PATH, read_only=True)
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def sql_execution_results():
    with open(RESULTS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


VIEWS = [
    ("vw_property_master", 25),
    ("vw_daily_property_utilization", 25 * 502),
    ("vw_monthly_cost_efficiency", 600),
    ("vw_meeting_room_performance", 25 * 2),
    ("vw_workplace_pressure_quadrants", 25),
    ("vw_lease_critical_horizons", 25),
    ("vw_data_quality_summary", None),
]


@pytest.mark.parametrize("view_name,expected_min_rows", VIEWS)
def test_analytical_views_exist_and_populate(db_conn, view_name, expected_min_rows):
    res = db_conn.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()[0]
    assert res > 0, f"View {view_name} returned 0 rows"
    if expected_min_rows:
        assert res >= expected_min_rows * 0.9, f"View {view_name} returned fewer rows than expected: {res}"


def test_no_foreign_key_orphans_in_db(db_conn):
    checks = [
        "SELECT COUNT(*) FROM fact_daily_workplace_utilization u WHERE NOT EXISTS (SELECT 1 FROM dim_property p WHERE p.PropertyKey = u.PropertyKey)",
        "SELECT COUNT(*) FROM fact_daily_workplace_utilization u WHERE NOT EXISTS (SELECT 1 FROM dim_space s WHERE s.SpaceKey = u.SpaceKey)",
        "SELECT COUNT(*) FROM fact_monthly_property_cost c WHERE NOT EXISTS (SELECT 1 FROM dim_property p WHERE p.PropertyKey = c.PropertyKey)",
        "SELECT COUNT(*) FROM dim_property p WHERE NOT EXISTS (SELECT 1 FROM dim_geography g WHERE g.GeographyKey = p.GeographyKey)",
    ]
    for q in checks:
        assert db_conn.execute(q).fetchone()[0] == 0, f"Found orphan records for query: {q}"


# Parameterized test over all 16 business questions
@pytest.mark.parametrize("q_idx", list(range(1, 17)))
def test_all_16_business_questions_executed_successfully(sql_execution_results, q_idx):
    analysis_queries = sql_execution_results.get("05_analysis", [])
    assert len(analysis_queries) == 16, "Expected exactly 16 business question statements in results"
    stmt = analysis_queries[q_idx - 1]
    assert stmt["status"] == "SUCCESS", f"Business question {q_idx} failed: {stmt.get('error')}"
    assert stmt["row_count"] > 0, f"Business question {q_idx} returned 0 rows"


def test_core_kpi_query_succeeded(sql_execution_results):
    kpi_queries = sql_execution_results.get("04_kpis", [])
    assert len(kpi_queries) == 1
    assert kpi_queries[0]["status"] == "SUCCESS"
    assert kpi_queries[0]["row_count"] == 1
