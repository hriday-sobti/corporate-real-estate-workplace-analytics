"""Export clean analytical datasets to powerbi/dashboard_preview/dashboard_data.json.

Supplies the interactive dashboard preview with pre-computed facts,
mart aggregates, property details, and data quality records for zero-dependency exploration.
"""

import os
import json
import pandas as pd


def export_dashboard_payload():
    """Compiles analytical tables into JSON for the interactive client preview."""
    analytical_dir = os.path.join("data", "analytical")
    out_dir = os.path.join("powerbi", "dashboard_preview")
    os.makedirs(out_dir, exist_ok=True)

    df_prop = pd.read_csv(os.path.join(analytical_dir, "dim_property.csv"))
    df_geo = pd.read_csv(os.path.join(analytical_dir, "dim_geography.csv"))
    df_ft = pd.read_csv(os.path.join(analytical_dir, "dim_facility_type.csv"))
    df_floor = pd.read_csv(os.path.join(analytical_dir, "dim_floor.csv"))
    df_lease = pd.read_csv(os.path.join(analytical_dir, "dim_lease.csv"))
    df_pressure = pd.read_csv(os.path.join(analytical_dir, "mart_workplace_pressure_matrix.csv"))
    df_attention = pd.read_csv(os.path.join(analytical_dir, "mart_portfolio_attention_index.csv"))
    df_monthly = pd.read_csv(os.path.join(analytical_dir, "mart_property_monthly_summary.csv"))
    df_dq = pd.read_csv(os.path.join(analytical_dir, "fact_data_quality.csv"))

    # Convert to json records
    payload = {
        "properties": df_prop.to_dict(orient="records"),
        "geography": df_geo.to_dict(orient="records"),
        "facility_types": df_ft.to_dict(orient="records"),
        "floors": df_floor.to_dict(orient="records"),
        "leases": df_lease.to_dict(orient="records"),
        "pressure_matrix": df_pressure.to_dict(orient="records"),
        "attention_index": df_attention.to_dict(orient="records"),
        "monthly_summary": df_monthly.to_dict(orient="records"),
        "data_quality": df_dq.to_dict(orient="records"),
    }

    out_file = os.path.join(out_dir, "dashboard_data.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    print(f"Exported dashboard preview data -> {out_file} ({os.path.getsize(out_file):,} bytes)")


if __name__ == "__main__":
    export_dashboard_payload()
