"""Automated Pipeline Test Suite.

Verifies:
- Relational integrity and key uniqueness
- Mathematical bounds (occupants <= capacity, utilization in [0, 1])
- Architectural spatial constraints (usable <= rentable area)
- Financial integrity (costs >= 0)
- Chronological consistency (lease start <= lease end)
- Geospatial mapping consistency
- Cross-tool reconciliation parity (Python vs. SQL database)
"""

import os
import pytest
import pandas as pd
import numpy as np
import duckdb

ANALYTICAL_DIR = os.path.join("data", "analytical")
DB_PATH = os.path.join("data", "cre_analytics.duckdb")


@pytest.fixture(scope="module")
def analytical_data():
    """Loads all analytical datasets for testing."""
    return {
        "prop": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_property.csv")),
        "geo": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_geography.csv")),
        "floor": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_floor.csv")),
        "space": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_space.csv")),
        "lease": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_lease.csv")),
        "date": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_date.csv")),
        "util": pd.read_csv(os.path.join(ANALYTICAL_DIR, "fact_daily_workplace_utilization.csv")),
        "room": pd.read_csv(os.path.join(ANALYTICAL_DIR, "fact_room_utilization.csv")),
        "cost": pd.read_csv(os.path.join(ANALYTICAL_DIR, "fact_monthly_property_cost.csv")),
        "headcount": pd.read_csv(os.path.join(ANALYTICAL_DIR, "fact_headcount.csv")),
        "dq": pd.read_csv(os.path.join(ANALYTICAL_DIR, "fact_data_quality.csv")),
    }


def test_property_keys_unique(analytical_data):
    """Rule: Property keys and property codes must be strictly unique."""
    df_prop = analytical_data["prop"]
    assert df_prop["PropertyKey"].is_unique, "PropertyKey must be unique"
    assert df_prop["PropertyCode"].is_unique, "PropertyCode must be unique"
    assert len(df_prop) == 25, "Expected exactly 25 properties in portfolio"


def test_foreign_keys_resolve(analytical_data):
    """Rule: All foreign keys in facts must resolve to parent dimensions."""
    df_prop = analytical_data["prop"]
    df_space = analytical_data["space"]
    df_floor = analytical_data["floor"]
    df_util = analytical_data["util"]
    df_cost = analytical_data["cost"]

    valid_prop_keys = set(df_prop["PropertyKey"])
    valid_space_keys = set(df_space["SpaceKey"])
    valid_floor_keys = set(df_floor["FloorKey"])

    assert set(df_util["PropertyKey"]).issubset(valid_prop_keys), "Orphaned PropertyKey in utilization"
    assert set(df_util["SpaceKey"]).issubset(valid_space_keys), "Orphaned SpaceKey in utilization"
    assert set(df_util["FloorKey"]).issubset(valid_floor_keys), "Orphaned FloorKey in utilization"
    assert set(df_cost["PropertyKey"]).issubset(valid_prop_keys), "Orphaned PropertyKey in cost"


def test_capacity_non_negative(analytical_data):
    """Rule: All capacity definitions must be non-negative."""
    df_prop = analytical_data["prop"]
    df_util = analytical_data["util"]
    assert (df_prop["CapacitySeats"] > 0).all(), "Property capacity must be > 0"
    assert (df_util["Capacity"] > 0).all(), "Space capacity in utilization must be > 0"


def test_occupants_within_capacity(analytical_data):
    """Rule: After cleaning, actual occupants cannot exceed structural capacity."""
    df_util = analytical_data["util"]
    violations = df_util[df_util["ActualOccupants"] > df_util["Capacity"]]
    assert len(violations) == 0, f"Found {len(violations)} records where ActualOccupants > Capacity"
    peak_violations = df_util[df_util["PeakOccupants"] > df_util["Capacity"]]
    assert len(peak_violations) == 0, f"Found {len(peak_violations)} records where PeakOccupants > Capacity"


def test_utilization_rate_bounds(analytical_data):
    """Rule: Daily utilization rates must fall strictly in [0.0, 1.0]."""
    df_util = analytical_data["util"]
    assert (df_util["UtilizationRate"] >= 0.0).all(), "UtilizationRate cannot be negative"
    assert (df_util["UtilizationRate"] <= 1.0).all(), "UtilizationRate cannot exceed 1.0"
    assert (df_util["PeakUtilizationRate"] >= 0.0).all(), "PeakUtilizationRate cannot be negative"
    assert (df_util["PeakUtilizationRate"] <= 1.0).all(), "PeakUtilizationRate cannot exceed 1.0"


def test_usable_area_within_rentable(analytical_data):
    """Rule: Usable office area cannot exceed gross rentable area."""
    df_prop = analytical_data["prop"]
    violations = df_prop[df_prop["UsableAreaSqM"] > df_prop["RentableAreaSqM"]]
    assert len(violations) == 0, f"Found {len(violations)} properties where usable > rentable area"


def test_operating_costs_non_negative(analytical_data):
    """Rule: All cost ledger items must be non-negative."""
    df_cost = analytical_data["cost"]
    cost_cols = ["RentCost", "ServiceCharge", "EnergyCost", "FacilitiesCost", "MaintenanceCost", "OtherOperatingCost", "TotalOperatingCostINR"]
    for col in cost_cols:
        assert (df_cost[col] >= 0.0).all(), f"Found negative values in cost column {col}"


def test_lease_dates_chronology(analytical_data):
    """Rule: Lease expiration cannot precede commencement date."""
    df_lease = analytical_data["lease"]
    for _, row in df_lease.iterrows():
        if row["LeaseType"] != "Corporate Freehold":
            start = pd.to_datetime(row["LeaseStartDate"])
            end = pd.to_datetime(row["LeaseEndDate"])
            assert end >= start, f"Lease {row['LeaseContractNumber']} has end date preceding start date"


def test_no_duplicate_daily_observations(analytical_data):
    """Rule: Each SpaceKey must have at most 1 observation per DateKey."""
    df_util = analytical_data["util"]
    dups = df_util[df_util.duplicated(subset=["DateKey", "SpaceKey"])]
    assert len(dups) == 0, f"Found {len(dups)} duplicate space-date observations"


def test_geography_mapping_consistency(analytical_data):
    """Rule: Properties must map consistently to their sovereign countries and cities."""
    df_prop = analytical_data["prop"]
    df_geo = analytical_data["geo"]
    geo_map = df_geo.set_index("GeographyKey").to_dict(orient="index")

    city_to_country = {
        "Mumbai": "India", "Pune": "India", "Bengaluru": "India",
        "Chennai": "India", "Hyderabad": "India", "Delhi NCR": "India",
        "Singapore": "Singapore", "Kuala Lumpur": "Malaysia",
        "Bangkok": "Thailand", "Jakarta": "Indonesia", "Sydney": "Australia"
    }

    for _, row in df_prop.iterrows():
        geo = geo_map[row["GeographyKey"]]
        expected_country = city_to_country[geo["City"]]
        assert geo["Country"] == expected_country, f"City {geo['City']} mapped to {geo['Country']}, expected {expected_country}"


def test_reconciliation_python_vs_sql(analytical_data):
    """Rule: Aggregated portfolio totals must reconcile between Python and SQL database."""
    df_prop = analytical_data["prop"]
    df_util = analytical_data["util"]
    df_cost = analytical_data["cost"]

    # Python calculations
    py_total_usable = df_prop["UsableAreaSqM"].sum()
    py_total_seats = df_prop["CapacitySeats"].sum()
    py_total_cost = df_cost["TotalOperatingCostINR"].sum()
    py_avg_util = round((df_util["OccupiedHours"].sum() / df_util["AvailableHours"].sum()) * 100, 2)

    # SQL calculations via DuckDB
    conn = duckdb.connect(DB_PATH)
    sql_usable = float(conn.execute("SELECT SUM(UsableAreaSqM) FROM dim_property").fetchone()[0])
    sql_seats = int(conn.execute("SELECT SUM(CapacitySeats) FROM dim_property").fetchone()[0])
    sql_cost = float(conn.execute("SELECT SUM(TotalOperatingCostINR) FROM fact_monthly_property_cost").fetchone()[0])
    sql_avg_util = float(conn.execute("SELECT ROUND((SUM(OccupiedHours) / SUM(AvailableHours)) * 100, 2) FROM fact_daily_workplace_utilization").fetchone()[0])
    conn.close()

    assert abs(py_total_usable - sql_usable) < 0.01, f"Usable area mismatch: Python={py_total_usable}, SQL={sql_usable}"
    assert py_total_seats == sql_seats, f"Seats mismatch: Python={py_total_seats}, SQL={sql_seats}"
    assert abs(py_total_cost - sql_cost) < 0.01, f"Cost mismatch: Python={py_total_cost}, SQL={sql_cost}"
    assert abs(py_avg_util - sql_avg_util) < 0.01, f"Average utilization mismatch: Python={py_avg_util}, SQL={sql_avg_util}"
