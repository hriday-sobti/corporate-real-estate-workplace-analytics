"""Financial and Cost Efficiency Invariants Tests.

Tests:
- Total operating cost local identity: Rent + CAM + Energy + Facilities + Maint + Other
- Foreign exchange conversion accuracy to INR
- Non-negativity across all monthly financial ledgers
- Economic carrying penalty: Cost per Occupied Seat >= Cost per Available Seat
"""

import os
import pytest
import pandas as pd
import numpy as np

ANALYTICAL_DIR = os.path.join("data", "analytical")


@pytest.fixture(scope="module")
def financial_tables():
    return {
        "cost": pd.read_csv(os.path.join(ANALYTICAL_DIR, "fact_monthly_property_cost.csv")),
        "prop": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_property.csv")),
        "pressure": pd.read_csv(os.path.join(ANALYTICAL_DIR, "mart_workplace_pressure_matrix.csv")),
        "geo": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_geography.csv")),
    }


def test_monthly_cost_row_count(financial_tables):
    assert len(financial_tables["cost"]) == 600, "Expected exactly 600 monthly cost records (25 props * 24 months)"


def test_cost_components_sum_to_local_total(financial_tables):
    cost = financial_tables["cost"]
    sum_components = np.round(
        cost["RentCost"] + cost["ServiceCharge"] + cost["EnergyCost"] +
        cost["FacilitiesCost"] + cost["MaintenanceCost"] + cost["OtherOperatingCost"],
        2
    )
    assert np.allclose(cost["TotalOperatingCostLocal"], sum_components, atol=0.02)


def test_cost_currency_conversion_to_inr(financial_tables):
    cost = financial_tables["cost"]
    expected_inr = np.round(cost["TotalOperatingCostLocal"] * cost["FXRateToINR"], 2)
    assert np.allclose(cost["TotalOperatingCostINR"], expected_inr, atol=0.05)


def test_owned_properties_have_zero_base_rent(financial_tables):
    cost = financial_tables["cost"]
    prop = financial_tables["prop"]
    owned_keys = set(prop[prop["OwnershipType"] == "Owned"]["PropertyKey"])
    owned_costs = cost[cost["PropertyKey"].isin(owned_keys)]
    assert (owned_costs["RentCost"] == 0.0).all(), "Owned properties must have 0 rent cost"


# Parameterized test over all 25 properties in mart_workplace_pressure_matrix
@pytest.mark.parametrize("prop_key", list(range(1, 26)))
def test_each_property_carrying_cost_penalty(financial_tables, prop_key):
    pressure = financial_tables["pressure"]
    p_row = pressure[pressure["PropertyKey"] == prop_key].iloc[0]

    cost_avail = p_row["AnnualCostPerSeatINR"]
    cost_occ = p_row["AnnualCostPerOccupiedSeatINR"]
    usable_sqm = p_row["UsableAreaSqM"]
    ann_cost = p_row["AnnualOperatingCostINR"]

    assert ann_cost > 0, f"Property {prop_key} has non-positive annual cost"
    assert cost_avail > 0, f"Property {prop_key} has non-positive cost per seat"
    assert cost_occ >= cost_avail, f"Property {prop_key} cost per occupied seat ({cost_occ}) must be >= available seat ({cost_avail})"
    assert np.isclose(cost_avail, ann_cost / p_row["CapacitySeats"], atol=1.0)
    assert np.isclose(p_row["AnnualCostPerSqMINR"], ann_cost / usable_sqm, atol=1.0)


def test_portfolio_annual_cost_total(financial_tables):
    cost = financial_tables["cost"]
    annual_cost = cost["TotalOperatingCostINR"].sum() / 2.0
    # Expected ₹5,974,505,898
    assert 5.9e9 <= annual_cost <= 6.1e9, f"Unexpected annual cost: {annual_cost}"


def test_fx_rates_consistency(financial_tables):
    geo = financial_tables["geo"]
    cost = financial_tables["cost"]
    fx_dict = geo.set_index("LocalCurrency")["FixedFXToINR"].to_dict()
    for curr, fx in fx_dict.items():
        curr_costs = cost[cost["OriginalCurrency"] == curr]
        if len(curr_costs) > 0:
            assert np.allclose(curr_costs["FXRateToINR"], fx), f"FX rate mismatch for {curr}"
