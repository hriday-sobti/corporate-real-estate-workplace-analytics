"""Portfolio Attention Index and Sensitivity Scenario Model Tests.

Tests:
- Portfolio Attention Index (PAI) component bounds and weighting logic
- Attention ranking uniqueness (1 through 25)
- Sensitivity analysis robustness (Spearman rank correlation > 0.95)
- Space consolidation scenario projections and elasticity calculations
"""

import os
import json
import pytest
import pandas as pd

ANALYTICAL_DIR = os.path.join("data", "analytical")
OUTPUTS_DIR = "outputs"


@pytest.fixture(scope="module")
def attention_data():
    return pd.read_csv(os.path.join(ANALYTICAL_DIR, "mart_portfolio_attention_index.csv"))


@pytest.fixture(scope="module")
def sensitivity_json():
    with open(os.path.join(OUTPUTS_DIR, "attention_index_sensitivity.json"), "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def scenario_json():
    with open(os.path.join(OUTPUTS_DIR, "scenario_consolidation_results.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def test_pai_score_bounds(attention_data):
    pai = attention_data["PortfolioAttentionIndex"]
    assert (pai >= 0.0).all() and (pai <= 100.0).all()
    # Check individual components
    assert (attention_data["Score_UtilizationInefficiency"] >= 0).all() and (attention_data["Score_UtilizationInefficiency"] <= 100).all()
    assert (attention_data["Score_CostIntensity"] >= 0).all() and (attention_data["Score_CostIntensity"] <= 100).all()
    assert (attention_data["Score_LeaseExposure"] >= 0).all() and (attention_data["Score_LeaseExposure"] <= 100).all()
    assert (attention_data["Score_CapacityPressure"] >= 0).all() and (attention_data["Score_CapacityPressure"] <= 100).all()
    assert (attention_data["Score_DataQualityRisk"] >= 0).all() and (attention_data["Score_DataQualityRisk"] <= 100).all()


def test_pai_ranks_unique_1_to_25(attention_data):
    ranks = attention_data["AttentionRank"]
    assert set(ranks) == set(range(1, 26))


# Parameterized test over all 25 properties in PAI
@pytest.mark.parametrize("rank", list(range(1, 26)))
def test_each_pai_rank_has_valid_driver_and_tier(attention_data, rank):
    row = attention_data[attention_data["AttentionRank"] == rank].iloc[0]
    assert row["PrimaryAttentionDriver"] in {
        "Low Utilization", "High Cost Intensity", "Near-Term Lease Expiry",
        "Peak Capacity Pressure", "Data Quality Discrepancies"
    }
    assert row["AttentionTier"] in {"Immediate Attention", "Elevated Priority", "Stable Operations"}


SCHEMES = [
    "Equal Weighting (20% Each)",
    "Cost-Dominant Strategy",
    "Operational-Dominant Strategy"
]


@pytest.mark.parametrize("scheme_name", SCHEMES)
def test_pai_sensitivity_schemes_rank_stability(sensitivity_json, scheme_name):
    corrs = sensitivity_json["rank_correlations_vs_baseline"]
    assert scheme_name in corrs
    rho = corrs[scheme_name]["spearman_rho"]
    assert rho >= 0.95, f"Weighting scheme {scheme_name} had unacceptably low rank correlation: {rho}"


def test_scenario_model_three_scenarios_exist(scenario_json):
    scenarios = scenario_json["scenarios"]
    assert len(scenarios) == 3
    names = [s["scenario_name"] for s in scenarios]
    assert "Scenario 1: Conservative Adjustment" in names[0]
    assert "Scenario 2: Balanced Agile Optimization" in names[1]
    assert "Scenario 3: Strategic Footprint Rationalization" in names[2]


@pytest.mark.parametrize("sc_idx", [0, 1, 2])
def test_each_scenario_impacts_are_positive(scenario_json, sc_idx):
    sc = scenario_json["scenarios"][sc_idx]
    baseline_util = scenario_json["baseline_summary"]["portfolio_average_utilization_pct"]
    assert sc["potential_seats_surrendered"] > 0
    assert sc["potential_usable_area_reduction_sqm"] > 0
    assert sc["potential_annual_operating_cost_savings_inr"] > 0
    assert sc["projected_portfolio_avg_utilization_pct"] > baseline_util
    assert sc["label"] == "Illustrative project scenario"
