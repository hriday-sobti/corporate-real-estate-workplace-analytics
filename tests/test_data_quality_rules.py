"""Data Quality Framework and Rule Evaluator Tests.

Tests:
- Manifest structure and schema contract
- Evaluators for rules DQ001 through DQ012 individually
- Verification that raw layer has expected defects and clean layer has 0 critical/high violations
"""

import os
import pytest
import pandas as pd
from src.validation.rules import (
    check_dq001_property_uniqueness,
    check_dq002_occupants_within_capacity,
    check_dq003_utilization_rate_bounds,
    check_dq004_lease_dates_chronology,
    check_dq005_geographic_and_naming_consistency,
    check_dq006_usable_vs_rentable_area,
    check_dq007_referential_integrity,
    check_dq008_non_negative_costs,
    check_dq009_mandatory_completeness,
    check_dq010_daily_observation_uniqueness,
    check_dq011_room_attended_within_scheduled,
    check_dq012_density_plausibility,
)

RAW_DIR = os.path.join("data", "raw")
CLEAN_DIR = os.path.join("data", "clean")


@pytest.fixture(scope="module")
def raw_data():
    return {
        "prop": pd.read_csv(os.path.join(RAW_DIR, "raw_properties.csv")),
        "geo": pd.read_csv(os.path.join(RAW_DIR, "raw_geography.csv")),
        "space": pd.read_csv(os.path.join(RAW_DIR, "raw_spaces.csv")),
        "lease": pd.read_csv(os.path.join(RAW_DIR, "raw_leases.csv")),
        "cost": pd.read_csv(os.path.join(RAW_DIR, "raw_property_costs.csv")),
        "util": pd.read_csv(os.path.join(RAW_DIR, "raw_utilization.csv")),
        "room": pd.read_csv(os.path.join(RAW_DIR, "raw_room_utilization.csv")),
        "manifest": pd.read_csv(os.path.join("data", "quality_issue_manifest.csv")),
    }


@pytest.fixture(scope="module")
def clean_data():
    return {
        "prop": pd.read_csv(os.path.join(CLEAN_DIR, "dim_property.csv")),
        "geo": pd.read_csv(os.path.join(CLEAN_DIR, "dim_geography.csv")),
        "space": pd.read_csv(os.path.join(CLEAN_DIR, "dim_space.csv")),
        "lease": pd.read_csv(os.path.join(CLEAN_DIR, "dim_lease.csv")),
        "cost": pd.read_csv(os.path.join(CLEAN_DIR, "fact_monthly_property_cost.csv")),
        "util": pd.read_csv(os.path.join(CLEAN_DIR, "fact_daily_workplace_utilization.csv")),
        "room": pd.read_csv(os.path.join(CLEAN_DIR, "fact_room_utilization.csv")),
    }


def test_manifest_contract(raw_data):
    manifest = raw_data["manifest"]
    expected_cols = [
        "issue_id", "table_name", "record_identifier", "issue_type",
        "expected_rule", "injected_value", "expected_correct_value", "severity"
    ]
    assert list(manifest.columns) == expected_cols
    assert len(manifest) == 44, "Manifest must contain exactly 44 logged defect events"
    assert set(manifest["severity"]).issubset({"Critical", "High", "Medium", "Warning"})


DQ_RULES = ["DQ001", "DQ003", "DQ004", "DQ005", "DQ006", "DQ008", "DQ009", "DQ010", "DQ011"]


@pytest.mark.parametrize("rule_code", DQ_RULES)
def test_manifest_covers_rule(raw_data, rule_code):
    manifest = raw_data["manifest"]
    rule_issues = manifest[manifest["issue_type"] == rule_code]
    assert len(rule_issues) > 0, f"Manifest must contain at least 1 issue for {rule_code}"


def test_dq001_detects_duplicate_in_raw(raw_data):
    failures = check_dq001_property_uniqueness(raw_data["prop"])
    assert len(failures) == 2, "Raw properties should have 1 duplicate pair (2 rows)"


def test_dq001_passes_in_clean(clean_data):
    failures = check_dq001_property_uniqueness(clean_data["prop"])
    assert len(failures) == 0, "Clean properties must have 0 duplicate property codes"


def test_dq002_passes_in_clean(clean_data):
    failures = check_dq002_occupants_within_capacity(clean_data["util"])
    assert len(failures) == 0, "Clean utilization must have 0 capacity breaches"


def test_dq003_detects_overutilization_in_raw(raw_data):
    failures = check_dq003_utilization_rate_bounds(raw_data["util"])
    assert len(failures) == 14, "Raw utilization should detect 14 over-utilization flaws"


def test_dq003_passes_in_clean(clean_data):
    failures = check_dq003_utilization_rate_bounds(clean_data["util"])
    assert len(failures) == 0, "Clean utilization must have 0 rate out of bounds"


def test_dq004_detects_inverted_dates_in_raw(raw_data):
    failures = check_dq004_lease_dates_chronology(raw_data["lease"])
    assert len(failures) == 2, "Raw leases should have 2 inverted lease date contracts"


def test_dq004_passes_in_clean(clean_data):
    failures = check_dq004_lease_dates_chronology(clean_data["lease"])
    assert len(failures) == 0, "Clean leases must have 0 chronological inversions"


def test_dq006_detects_area_inversion_in_raw(raw_data):
    failures = check_dq006_usable_vs_rentable_area(raw_data["prop"])
    assert len(failures) == 1, "Raw properties should detect 1 usable > rentable area flaw"


def test_dq006_passes_in_clean(clean_data):
    failures = check_dq006_usable_vs_rentable_area(clean_data["prop"])
    assert len(failures) == 0, "Clean properties must have 0 usable > rentable area violations"


def test_dq007_referential_integrity_clean(clean_data):
    failures = check_dq007_referential_integrity(clean_data["util"], clean_data["space"], clean_data["prop"])
    assert len(failures) == 0, "Clean facts must have 0 orphaned keys"


def test_dq008_detects_negative_costs_in_raw(raw_data):
    failures = check_dq008_non_negative_costs(raw_data["cost"])
    assert len(failures) == 3, "Raw costs should detect 3 negative cost items"


def test_dq008_passes_in_clean(clean_data):
    failures = check_dq008_non_negative_costs(clean_data["cost"])
    assert len(failures) == 0, "Clean costs must have 0 negative cost entries"


def test_dq010_detects_duplicate_observations_in_raw(raw_data):
    failures = check_dq010_daily_observation_uniqueness(raw_data["util"])
    assert len(failures) == 8, "Raw utilization should detect 4 duplicate pairs (8 rows)"


def test_dq010_passes_in_clean(clean_data):
    failures = check_dq010_daily_observation_uniqueness(clean_data["util"])
    assert len(failures) == 0, "Clean utilization must have 0 duplicate observations"


def test_dq011_detects_attended_exceeds_booked_in_raw(raw_data):
    failures = check_dq011_room_attended_within_scheduled(raw_data["room"])
    assert len(failures) == 5, "Raw room utilization should detect 5 attended > booked flaws"


def test_dq011_passes_in_clean(clean_data):
    failures = check_dq011_room_attended_within_scheduled(clean_data["room"])
    assert len(failures) == 0, "Clean room utilization must have 0 attended > booked violations"


def test_dq012_density_plausibility_clean(clean_data):
    failures = check_dq012_density_plausibility(clean_data["prop"])
    assert len(failures) == 0, "All clean properties must have plausible density between 5 and 25 m2/seat"
