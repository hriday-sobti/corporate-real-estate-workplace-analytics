"""Capacity Consolidation & Shared-Space Sensitivity Scenario Engine.

Models illustrative adjustments to underutilized workplace assets:
- User-adjustable seat reduction percentages (10%, 15%, 20%)
- Variable cost elasticity assumption (60% variable, 40% fixed)
- Projects changes in capacity, usable area, operating expenses, resulting utilization, and peak pressure
- Strictly labeled: 'Illustrative project scenario - sensitivity model, not a guaranteed saving'
"""

import os
import json
from typing import Dict, Any, List
import numpy as np
import pandas as pd


def run_scenario_modeling() -> Dict[str, Any]:
    """Runs conservative, balanced, and strategic agile consolidation scenarios."""
    print("==================================================================")
    print("PHASE 13: CAPACITY CONSOLIDATION SENSITIVITY SCENARIO MODELING")
    print("==================================================================")

    analytical_dir = os.path.join("data", "analytical")
    df_pressure = pd.read_csv(os.path.join(analytical_dir, "mart_workplace_pressure_matrix.csv"))

    # Baseline portfolio totals
    total_baseline_seats = df_pressure["CapacitySeats"].sum()
    total_baseline_usable = df_pressure["UsableAreaSqM"].sum()
    total_baseline_cost_inr = df_pressure["AnnualOperatingCostINR"].sum()
    baseline_avg_presence = df_pressure["AverageDailyPresence"].sum()
    baseline_avg_util = round((baseline_avg_presence / total_baseline_seats) * 100, 2)

    # Filter target properties for consolidation: Underutilized or Peak-sensitive with avg util < 55%
    target_properties = df_pressure[df_pressure["AverageUtilizationPct"] < 55.0].copy()
    print(f"Identified {len(target_properties)} candidate properties with Average Utilization < 55%.")

    scenarios = [
        {
            "scenario_name": "Scenario 1: Conservative Adjustment",
            "seat_reduction_pct": 0.10,
            "cost_variable_ratio": 0.60,
            "description": "Modest 10% seat consolidation across underutilized assets; retains high buffer.",
        },
        {
            "scenario_name": "Scenario 2: Balanced Agile Optimization",
            "seat_reduction_pct": 0.15,
            "cost_variable_ratio": 0.60,
            "description": "Recommended 15% seat reduction with standard desk sharing policy (1.35:1).",
        },
        {
            "scenario_name": "Scenario 3: Strategic Footprint Rationalization",
            "seat_reduction_pct": 0.20,
            "cost_variable_ratio": 0.60,
            "description": "Aggressive 20% footprint surrender for expiring lease properties and underutilized hubs.",
        },
    ]

    scenario_results = []
    mart_scenario_rows = []

    for sc in scenarios:
        s_name = sc["scenario_name"]
        red_pct = sc["seat_reduction_pct"]
        var_ratio = sc["cost_variable_ratio"]

        # Calculate impacts across target properties
        sc_df = df_pressure.copy()
        is_target = sc_df["PropertyKey"].isin(target_properties["PropertyKey"])

        sc_df["SeatsSurrendered"] = np.where(is_target, np.round(sc_df["CapacitySeats"] * red_pct).astype(int), 0)
        sc_df["ProjectedSeats"] = sc_df["CapacitySeats"] - sc_df["SeatsSurrendered"]

        # Usable area surrender proportional to seats
        sc_df["AreaSurrenderedSqM"] = np.where(
            is_target,
            np.round(sc_df["UsableAreaSqM"] * (sc_df["SeatsSurrendered"] / sc_df["CapacitySeats"]), 2),
            0.0
        )
        sc_df["ProjectedUsableAreaSqM"] = sc_df["UsableAreaSqM"] - sc_df["AreaSurrenderedSqM"]

        # Cost savings (only variable component of operating costs changes)
        sc_df["AnnualCostSavingsINR"] = np.where(
            is_target,
            np.round(sc_df["AnnualOperatingCostINR"] * (sc_df["AreaSurrenderedSqM"] / sc_df["UsableAreaSqM"]) * var_ratio, 2),
            0.0
        )
        sc_df["ProjectedAnnualCostINR"] = sc_df["AnnualOperatingCostINR"] - sc_df["AnnualCostSavingsINR"]

        # Resulting utilization metrics
        sc_df["ProjectedAvgUtilPct"] = np.round(
            (sc_df["AverageDailyPresence"] / sc_df["ProjectedSeats"]) * 100, 2
        )
        # Peak occupancy increases proportionally with seat compression
        sc_df["ProjectedPeakUtilPct"] = np.round(
            sc_df["PeakUtilizationPct"] * (sc_df["CapacitySeats"] / sc_df["ProjectedSeats"]), 2
        )
        # Resulting capacity pressure flag
        sc_df["ProjectedPressureChokeFlag"] = sc_df["ProjectedPeakUtilPct"] >= 85.0

        # Portfolio aggregations for this scenario
        tot_surrendered_seats = int(sc_df["SeatsSurrendered"].sum())
        tot_surrendered_area = float(sc_df["AreaSurrenderedSqM"].sum())
        tot_cost_savings = float(sc_df["AnnualCostSavingsINR"].sum())
        tot_projected_seats = int(sc_df["ProjectedSeats"].sum())
        tot_projected_area = float(sc_df["ProjectedUsableAreaSqM"].sum())
        tot_projected_cost = float(sc_df["ProjectedAnnualCostINR"].sum())
        proj_portfolio_avg_util = round((baseline_avg_presence / tot_projected_seats) * 100, 2)
        target_props_in_pressure = int(sc_df[is_target]["ProjectedPressureChokeFlag"].sum())

        summary_metrics = {
            "scenario_name": s_name,
            "label": "Illustrative project scenario",
            "seat_reduction_pct": red_pct * 100,
            "cost_variability_assumption_pct": var_ratio * 100,
            "target_properties_affected": int(is_target.sum()),
            "potential_seats_surrendered": tot_surrendered_seats,
            "projected_portfolio_seats": tot_projected_seats,
            "potential_usable_area_reduction_sqm": round(tot_surrendered_area, 2),
            "projected_portfolio_usable_area_sqm": round(tot_projected_area, 2),
            "potential_annual_operating_cost_savings_inr": round(tot_cost_savings, 2),
            "projected_portfolio_annual_cost_inr": round(tot_projected_cost, 2),
            "portfolio_cost_reduction_pct": round((tot_cost_savings / total_baseline_cost_inr) * 100, 2),
            "baseline_portfolio_avg_utilization_pct": baseline_avg_util,
            "projected_portfolio_avg_utilization_pct": proj_portfolio_avg_util,
            "target_assets_exceeding_85pct_peak_buffer": target_props_in_pressure,
            "analyst_interpretation": (
                f"Under {s_name}, surrendering {tot_surrendered_seats:,} seats ({round(tot_surrendered_area):,} m²) "
                f"yields an illustrative estimated annual saving of ₹{tot_cost_savings/1e7:.2f} Cr, lifting overall "
                f"portfolio utilization from {baseline_avg_util}% to {proj_portfolio_avg_util}%. "
                f"Importantly, {target_props_in_pressure} target asset(s) would breach the 85% peak choke point, "
                f"indicating that consolidation must be paired with mid-week hoteling smoothing."
            )
        }
        scenario_results.append(summary_metrics)

        # Append to tabular mart
        for _, r in sc_df.iterrows():
            mart_scenario_rows.append({
                "ScenarioName": s_name,
                "PropertyKey": r["PropertyKey"],
                "PropertyCode": r["PropertyCode"],
                "PropertyName": r["PropertyName"],
                "City": r["City"],
                "Country": r["Country"],
                "BaselineSeats": r["CapacitySeats"],
                "ProjectedSeats": r["ProjectedSeats"],
                "SeatsSurrendered": r["SeatsSurrendered"],
                "BaselineAreaSqM": r["UsableAreaSqM"],
                "ProjectedAreaSqM": r["ProjectedUsableAreaSqM"],
                "AreaSurrenderedSqM": r["AreaSurrenderedSqM"],
                "BaselineAnnualCostINR": r["AnnualOperatingCostINR"],
                "ProjectedAnnualCostINR": r["ProjectedAnnualCostINR"],
                "AnnualSavingsINR": r["AnnualCostSavingsINR"],
                "BaselineAvgUtilPct": r["AverageUtilizationPct"],
                "ProjectedAvgUtilPct": r["ProjectedAvgUtilPct"],
                "BaselinePeakUtilPct": r["PeakUtilizationPct"],
                "ProjectedPeakUtilPct": r["ProjectedPeakUtilPct"],
                "ExceedsPeakBuffer": r["ProjectedPressureChokeFlag"],
            })

    df_mart_scenario = pd.DataFrame(mart_scenario_rows)
    scenario_mart_path = os.path.join(analytical_dir, "mart_scenario_consolidation.csv")
    df_mart_scenario.to_csv(scenario_mart_path, index=False)
    print(f"Saved scenario analytical mart -> {scenario_mart_path}")

    # Output json
    out_payload = {
        "disclaimer": "Illustrative project scenario - sensitivity model, not a guaranteed saving.",
        "baseline_summary": {
            "total_seat_capacity": int(total_baseline_seats),
            "total_usable_area_sqm": float(total_baseline_usable),
            "total_annual_operating_cost_inr": float(total_baseline_cost_inr),
            "portfolio_average_utilization_pct": baseline_avg_util,
        },
        "scenarios": scenario_results,
    }

    out_file = os.path.join("outputs", "scenario_consolidation_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out_payload, f, indent=2)

    print(f"Saved scenario results -> {out_file}")
    for sc in scenario_results:
        print(f"\n[{sc['scenario_name']}]")
        print(f"  Seats Surrendered:    {sc['potential_seats_surrendered']:,} seats")
        print(f"  Area Rationalized:    {sc['potential_usable_area_reduction_sqm']:,.1f} m²")
        print(f"  Annual Cost Savings:  ₹{sc['potential_annual_operating_cost_savings_inr']:,.0f}")
        print(f"  Resulting Util:       {sc['projected_portfolio_avg_utilization_pct']}% (was {baseline_avg_util}%)")

    return out_payload


if __name__ == "__main__":
    run_scenario_modeling()
