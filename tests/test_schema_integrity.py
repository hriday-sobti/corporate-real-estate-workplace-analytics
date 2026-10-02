"""Schema and Dimensional Relational Integrity Tests.

Exhaustively verifies:
- Uniqueness, boundaries, and metadata across all 25 properties
- Geographical mapping integrity across 11 cities and 6 countries
- Architectural floor and space structural consistency
- Lease contract terms, horizon categories, and date causalities
- Date dimension calendar completeness across 730 days
"""

import os
import pytest
import pandas as pd

ANALYTICAL_DIR = os.path.join("data", "analytical")


@pytest.fixture(scope="module")
def schema_tables():
    return {
        "prop": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_property.csv")),
        "geo": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_geography.csv")),
        "ft": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_facility_type.csv")),
        "floor": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_floor.csv")),
        "space": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_space.csv")),
        "lease": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_lease.csv")),
        "date": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_date.csv")),
    }


def test_property_count_exact(schema_tables):
    assert len(schema_tables["prop"]) == 25, "Portfolio must contain exactly 25 properties"


def test_property_keys_unique(schema_tables):
    prop = schema_tables["prop"]
    assert prop["PropertyKey"].nunique() == 25
    assert prop["PropertyCode"].nunique() == 25
    assert prop["PropertyName"].nunique() == 25


def test_usable_area_within_rentable_all(schema_tables):
    prop = schema_tables["prop"]
    assert (prop["UsableAreaSqM"] <= prop["RentableAreaSqM"]).all()
    assert (prop["UsableAreaSqM"] > 0).all()


def test_density_bounds_all_properties(schema_tables):
    prop = schema_tables["prop"]
    density = prop["UsableAreaSqM"] / prop["CapacitySeats"]
    assert (density >= 5.0).all() and (density <= 20.0).all()


# Parameterized test over all 25 property keys
@pytest.mark.parametrize("prop_key", list(range(1, 26)))
def test_each_property_has_valid_attributes(schema_tables, prop_key):
    prop = schema_tables["prop"]
    p_row = prop[prop["PropertyKey"] == prop_key]
    assert len(p_row) == 1, f"PropertyKey {prop_key} must exist once"
    r = p_row.iloc[0]
    assert r["CapacitySeats"] >= 200, f"Property {r['PropertyCode']} capacity too small"
    assert r["UsableAreaSqM"] >= 2000, f"Property {r['PropertyCode']} area too small"
    assert r["OpeningYear"] >= 2010, f"Property {r['PropertyCode']} opening year invalid"
    assert r["FloorCount"] >= 2, f"Property {r['PropertyCode']} floor count must be >= 2"


# Parameterized test over all 11 cities
CITIES = [
    ("Mumbai", "India"), ("Pune", "India"), ("Bengaluru", "India"),
    ("Chennai", "India"), ("Hyderabad", "India"), ("Delhi NCR", "India"),
    ("Singapore", "Singapore"), ("Kuala Lumpur", "Malaysia"),
    ("Bangkok", "Thailand"), ("Jakarta", "Indonesia"), ("Sydney", "Australia")
]


@pytest.mark.parametrize("city,expected_country", CITIES)
def test_geography_city_country_mapping(schema_tables, city, expected_country):
    geo = schema_tables["geo"]
    matches = geo[geo["City"] == city]
    assert len(matches) == 1, f"City {city} must exist once in dim_geography"
    assert matches.iloc[0]["Country"] == expected_country


def test_total_geographies_count(schema_tables):
    assert len(schema_tables["geo"]) == 11, "Must contain exactly 11 metropolitan markets"


def test_facility_type_count_and_keys(schema_tables):
    ft = schema_tables["ft"]
    assert len(ft) == 4, "Must contain 4 facility types"
    assert set(ft["FacilityTypeCode"]) == {"REG_HQ", "TECH_HUB", "OPS_CENTER", "SALES_CLIENT"}


def test_floor_structure_integrity(schema_tables):
    floor = schema_tables["floor"]
    prop = schema_tables["prop"]
    assert len(floor) == 112, "Expected 112 floors across 25 properties"
    assert floor["FloorKey"].nunique() == 112
    # Verify each property's floor count matches
    floor_counts = floor.groupby("PropertyKey").size().to_dict()
    for _, p in prop.iterrows():
        assert floor_counts[p["PropertyKey"]] == p["FloorCount"]


def test_space_structure_integrity(schema_tables):
    space = schema_tables["space"]
    assert len(space) == 809, "Expected 809 distinct space records"
    assert space["SpaceKey"].nunique() == 809
    assert (space["AreaSqM"] > 0).all()
    assert (space["Capacity"] >= 0).all()


def test_space_types_valid(schema_tables):
    space = schema_tables["space"]
    valid_types = {
        "Open Workstation", "Private Office", "Small Meeting Room",
        "Large Meeting Room", "Collaboration Area", "Focus Room",
        "Reception / Shared Support"
    }
    assert set(space["SpaceType"]).issubset(valid_types)


def test_lease_table_integrity(schema_tables):
    lease = schema_tables["lease"]
    assert len(lease) == 25, "Must have exactly 25 lease records"
    assert lease["LeaseKey"].nunique() == 25
    assert (lease["AnnualRentINR"] >= 0).all()


# Parameterized test over all 25 leases
@pytest.mark.parametrize("prop_key", list(range(1, 26)))
def test_lease_dates_and_horizons_per_property(schema_tables, prop_key):
    lease = schema_tables["lease"]
    l_row = lease[lease["PropertyKey"] == prop_key].iloc[0]
    own = l_row["LeaseType"]
    if own == "Corporate Freehold":
        assert l_row["ExpiryHorizonCategory"] == "Owned"
    else:
        assert l_row["ExpiryHorizonCategory"] in {
            "Expiring <= 6M", "Expiring 6-12M", "Expiring 12-24M", "Horizon > 24M"
        }
        s = pd.to_datetime(l_row["LeaseStartDate"])
        e = pd.to_datetime(l_row["LeaseEndDate"])
        assert e >= s, f"Lease end date must be >= start date for property {prop_key}"


def test_date_dimension_completeness(schema_tables):
    date_df = schema_tables["date"]
    assert len(date_df) == 730, "Date dimension must contain exactly 730 days (24 months)"
    assert date_df["DateKey"].nunique() == 730
    assert date_df["FullDate"].min() == "2024-10-01"
    assert date_df["FullDate"].max() == "2026-09-30"
    working_days = date_df[date_df["IsWorkingDay"]]
    assert len(working_days) == 502, "Expected exactly 502 business working days"
