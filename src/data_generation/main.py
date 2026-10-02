"""Master orchestration script for synthetic data generation and raw data layer creation."""

import os
import sys
import pandas as pd

from src.data_generation.generate_portfolio import generate_portfolio_dimensions
from src.data_generation.generate_time_series import generate_time_series
from src.data_generation.inject_quality_issues import inject_quality_issues_and_create_raw


def run_data_generation():
    """Generates baseline data, injects controlled quality flaws, and saves RAW CSVs."""
    print("==================================================================")
    print("PHASE 5 & 6: SYNTHETIC DATA GENERATION & CONTROLLED QUALITY INJECTION")
    print("==================================================================")

    # 1. Generate clean baseline portfolio dimensions
    print("\n[Step 1/3] Generating dimensional entities (properties, floors, spaces, leases)...")
    df_geo, df_ft, df_prop, df_floor, df_space, df_lease = generate_portfolio_dimensions()
    print(f"Generated {len(df_prop)} properties, {len(df_floor)} floors, {len(df_space)} spaces, {len(df_lease)} leases.")

    # 2. Generate time-series facts
    print("\n[Step 2/3] Generating 24-month operational time series (utilization, rooms, costs, headcount)...")
    df_date, df_util, df_room, df_cost, df_hc = generate_time_series(df_prop, df_floor, df_space)
    print(f"Generated {len(df_date)} calendar dates.")
    print(f"Generated {len(df_util):,} daily workplace utilization rows.")
    print(f"Generated {len(df_room):,} room utilization rows.")
    print(f"Generated {len(df_cost)} monthly property cost rows.")
    print(f"Generated {len(df_hc)} monthly headcount rows.")

    # 3. Inject controlled quality issues and create RAW data layer
    print("\n[Step 3/3] Injecting controlled operational defects and generating quality issue manifest...")
    raw_dfs, df_manifest = inject_quality_issues_and_create_raw(
        df_geo, df_ft, df_prop, df_floor, df_space, df_lease,
        df_date, df_util, df_room, df_cost, df_hc
    )

    # Save to data/raw/
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/clean", exist_ok=True)
    os.makedirs("data/analytical", exist_ok=True)

    for name, df in raw_dfs.items():
        out_path = os.path.join("data", "raw", f"{name}.csv")
        df.to_csv(out_path, index=False)
        print(f"  Saved RAW entity -> {out_path} ({len(df):,} rows)")

    # Save quality issue manifest
    manifest_path = os.path.join("data", "quality_issue_manifest.csv")
    df_manifest.to_csv(manifest_path, index=False)
    print(f"\n[Success] Quality issue manifest written -> {manifest_path} ({len(df_manifest)} logged defects)")

    total_fact_rows = len(df_util) + len(df_room) + len(df_cost) + len(df_hc)
    print(f"\n[Summary] Total observation rows across fact tables: {total_fact_rows:,}")
    print("Synthetic data generation and RAW ingestion completed successfully.")


if __name__ == "__main__":
    run_data_generation()
