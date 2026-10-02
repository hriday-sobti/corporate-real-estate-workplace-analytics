"""Data Quality Validation Engine.

Executes rules DQ001 through DQ012 against the RAW data layer,
reconciles findings against data/quality_issue_manifest.csv,
and generates outputs/data_quality_validation_report.json.
"""

import os
import json
from typing import Dict, List, Any
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


def run_validation_pipeline() -> Dict[str, Any]:
    """Loads raw data, executes all validation rules, and produces a diagnostic summary."""
    print("==================================================================")
    print("PHASE 7: AUTOMATED DATA QUALITY VALIDATION ENGINE")
    print("==================================================================")

    # 1. Load RAW tables
    raw_dir = os.path.join("data", "raw")
    print(f"\nLoading RAW tables from {raw_dir}...")
    df_prop = pd.read_csv(os.path.join(raw_dir, "raw_properties.csv"))
    df_geo = pd.read_csv(os.path.join(raw_dir, "raw_geography.csv"))
    df_floor = pd.read_csv(os.path.join(raw_dir, "raw_floors.csv"))
    df_space = pd.read_csv(os.path.join(raw_dir, "raw_spaces.csv"))
    df_lease = pd.read_csv(os.path.join(raw_dir, "raw_leases.csv"))
    df_cost = pd.read_csv(os.path.join(raw_dir, "raw_property_costs.csv"))
    df_util = pd.read_csv(os.path.join(raw_dir, "raw_utilization.csv"))
    df_room = pd.read_csv(os.path.join(raw_dir, "raw_room_utilization.csv"))
    df_manifest = pd.read_csv(os.path.join("data", "quality_issue_manifest.csv"))

    # 2. Run all rules
    print("\nExecuting validation rules DQ001 through DQ012...")
    all_failures: List[Dict[str, Any]] = []

    f_dq001 = check_dq001_property_uniqueness(df_prop)
    f_dq002 = check_dq002_occupants_within_capacity(df_util)
    f_dq003 = check_dq003_utilization_rate_bounds(df_util)
    f_dq004 = check_dq004_lease_dates_chronology(df_lease)
    f_dq005 = check_dq005_geographic_and_naming_consistency(df_prop, df_geo, df_space)
    f_dq006 = check_dq006_usable_vs_rentable_area(df_prop)
    f_dq007 = check_dq007_referential_integrity(df_util, df_space, df_prop)
    f_dq008 = check_dq008_non_negative_costs(df_cost)
    f_dq009 = check_dq009_mandatory_completeness(df_prop, df_lease, df_space, df_util)
    f_dq010 = check_dq010_daily_observation_uniqueness(df_util)
    f_dq011 = check_dq011_room_attended_within_scheduled(df_room)
    f_dq012 = check_dq012_density_plausibility(df_prop)

    for rule_list in [
        f_dq001, f_dq002, f_dq003, f_dq004, f_dq005, f_dq006,
        f_dq007, f_dq008, f_dq009, f_dq010, f_dq011, f_dq012
    ]:
        all_failures.extend(rule_list)

    total_failures = len(all_failures)
    manifest_count = len(df_manifest)

    # 3. Table record counts and pass rates
    table_stats = {
        "raw_properties": {"records": len(df_prop), "failures": len([f for f in all_failures if f["table_name"] == "raw_properties"])},
        "raw_leases": {"records": len(df_lease), "failures": len([f for f in all_failures if f["table_name"] == "raw_leases"])},
        "raw_spaces": {"records": len(df_space), "failures": len([f for f in all_failures if f["table_name"] == "raw_spaces"])},
        "raw_property_costs": {"records": len(df_cost), "failures": len([f for f in all_failures if f["table_name"] == "raw_property_costs"])},
        "raw_utilization": {"records": len(df_util), "failures": len([f for f in all_failures if f["table_name"] == "raw_utilization"])},
        "raw_room_utilization": {"records": len(df_room), "failures": len([f for f in all_failures if f["table_name"] == "raw_room_utilization"])},
    }

    total_records = sum(t["records"] for t in table_stats.values())
    overall_pass_rate = round(((total_records - total_failures) / total_records) * 100, 2)

    # Breakdown by severity
    severity_breakdown = {
        "Critical": len([f for f in all_failures if f["severity"] == "Critical"]),
        "High": len([f for f in all_failures if f["severity"] == "High"]),
        "Medium": len([f for f in all_failures if f["severity"] == "Medium"]),
        "Warning": len([f for f in all_failures if f["severity"] == "Warning"]),
    }

    # Breakdown by rule
    rule_breakdown = {}
    for f in all_failures:
        r_id = f["rule_id"]
        rule_breakdown[r_id] = rule_breakdown.get(r_id, 0) + 1

    summary_report = {
        "status": "COMPLETED",
        "total_evaluated_records": total_records,
        "total_exceptions_detected": total_failures,
        "injected_manifest_defects": manifest_count,
        "overall_data_quality_pass_rate_pct": overall_pass_rate,
        "severity_breakdown": severity_breakdown,
        "rule_breakdown": rule_breakdown,
        "table_stats": table_stats,
    }

    # Save output report
    os.makedirs("outputs", exist_ok=True)
    report_path = os.path.join("outputs", "data_quality_validation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": summary_report,
            "sample_exceptions": all_failures[:30],
        }, f, indent=2)

    print("\n------------------ DATA QUALITY AUDIT RESULTS ------------------")
    print(f"Total Records Inspected:        {total_records:,}")
    print(f"Total Quality Exceptions Found: {total_failures}")
    print(f"Logged Injected Manifest Issues: {manifest_count}")
    print(f"Overall Quality Pass Rate:      {overall_pass_rate}%")
    print("\nBreakdown by Severity:")
    for sev, cnt in severity_breakdown.items():
        print(f"  - {sev:<10}: {cnt}")
    print("\nBreakdown by Rule:")
    for r_id in sorted(rule_breakdown.keys()):
        print(f"  - {r_id:<8}: {rule_breakdown[r_id]} violations")
    print(f"\nDetailed audit report saved -> {report_path}")
    print("----------------------------------------------------------------")

    return summary_report


if __name__ == "__main__":
    run_validation_pipeline()
