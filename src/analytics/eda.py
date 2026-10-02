"""Exploratory Data Analysis and Diagnostic Visualization Engine.

Generates:
- Statistical profiles across portfolio dimensions
- Weekday utilization curves and peak-to-average spreads
- Cost intensity vs utilization scatter relationships
- Meeting room capacity mismatch profiles
- Diagnostic charts saved to outputs/charts/ for report/deck inclusion
"""

import os
from typing import Dict, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Restrained professional aesthetic
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "DejaVu Sans"]
plt.rcParams["axes.edgecolor"] = "#CCCCCC"
plt.rcParams["axes.linewidth"] = 0.8


CHARTS_DIR = os.path.join("outputs", "charts")


def run_exploratory_analysis() -> Dict[str, Any]:
    """Computes analytical summaries and renders diagnostic charts."""
    print("==================================================================")
    print("PHASE 11: PYTHON ANALYTICAL VALIDATION & EXPLORATORY PROFILING")
    print("==================================================================")

    os.makedirs(CHARTS_DIR, exist_ok=True)
    analytical_dir = os.path.join("data", "analytical")

    df_prop = pd.read_csv(os.path.join(analytical_dir, "dim_property.csv"))
    df_geo = pd.read_csv(os.path.join(analytical_dir, "dim_geography.csv"))
    df_date = pd.read_csv(os.path.join(analytical_dir, "dim_date.csv"))
    df_util = pd.read_csv(os.path.join(analytical_dir, "fact_daily_workplace_utilization.csv"))
    df_room = pd.read_csv(os.path.join(analytical_dir, "fact_room_utilization.csv"))
    df_cost = pd.read_csv(os.path.join(analytical_dir, "fact_monthly_property_cost.csv"))
    df_hc = pd.read_csv(os.path.join(analytical_dir, "fact_headcount.csv"))
    df_pressure = pd.read_csv(os.path.join(analytical_dir, "mart_workplace_pressure_matrix.csv"))
    df_attention = pd.read_csv(os.path.join(analytical_dir, "mart_portfolio_attention_index.csv"))

    print("\n[Step 1/5] Analyzing Portfolio Scale & Geographic Concentration...")
    total_props = len(df_prop)
    total_usable = df_prop["UsableAreaSqM"].sum()
    total_seats = df_prop["CapacitySeats"].sum()
    total_assigned = df_prop["AssignedHeadcount"].sum()
    total_annual_cost_inr = df_cost["TotalOperatingCostINR"].sum() / 2.0  # 24-month horizon

    print(f"  Total Properties:          {total_props}")
    print(f"  Total Usable Area:         {total_usable:,.0f} m²")
    print(f"  Total Seat Capacity:       {total_seats:,} seats")
    print(f"  Total Assigned Headcount:  {total_assigned:,} personnel")
    print(f"  Annual Operating Cost:     ₹{total_annual_cost_inr:,.0f}")
    print(f"  Portfolio Density:         {total_usable / total_seats:.2f} m²/seat")
    print(f"  Portfolio Sharing Ratio:   {total_assigned / total_seats:.2f}:1")

    # -------------------------------------------------------------
    # CHART 1: Weekday Utilization Profile (Tue-Thu peaks, Fri drop)
    # -------------------------------------------------------------
    print("\n[Step 2/5] Generating Chart 1: Weekday Utilization Profile...")
    df_util_date = pd.merge(df_util, df_date[["DateKey", "DayOfWeek", "DayName", "IsWorkingDay"]], on="DateKey")
    df_working = df_util_date[df_util_date["IsWorkingDay"]].copy()

    dow_summary = df_working.groupby(["DayOfWeek", "DayName"]).agg(
        AvgUtil=("UtilizationRate", "mean"),
        PeakUtil=("PeakUtilizationRate", "mean"),
    ).reset_index()
    dow_summary["AvgUtilPct"] = dow_summary["AvgUtil"] * 100
    dow_summary["PeakUtilPct"] = dow_summary["PeakUtil"] * 100

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    x = np.arange(len(dow_summary))
    width = 0.35

    bar1 = ax.bar(x - width/2, dow_summary["AvgUtilPct"], width, label="Average Daily Utilization %", color="#1F4E79")
    bar2 = ax.bar(x + width/2, dow_summary["PeakUtilPct"], width, label="Average Peak Utilization %", color="#E07A5F")

    ax.set_ylabel("Utilization Rate (%)", fontsize=10, fontweight="bold", color="#333333")
    ax.set_title("Workplace Utilization by Day of Week: Mid-Week Peak vs. Friday Trough", fontsize=12, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(dow_summary["DayName"], fontsize=10)
    ax.set_ylim(0, 100)
    ax.axhline(85, color="#D9534F", linestyle="--", linewidth=1.2, label="Capacity Pressure Choke Point (85%)")
    ax.legend(frameon=True, facecolor="white", edgecolor="#DDDDDD", loc="upper left", fontsize=9)

    for b in bar1:
        h = b.get_height()
        ax.annotate(f"{h:.1f}%", xy=(b.get_x() + b.get_width() / 2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8, color="#1F4E79", fontweight="bold")
    for b in bar2:
        h = b.get_height()
        ax.annotate(f"{h:.1f}%", xy=(b.get_x() + b.get_width() / 2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8, color="#C0392B", fontweight="bold")

    plt.tight_layout()
    chart1_path = os.path.join(CHARTS_DIR, "eda_weekday_utilization.png")
    plt.savefig(chart1_path)
    plt.close()
    print(f"  Saved -> {chart1_path}")

    # -------------------------------------------------------------
    # CHART 2: Workplace Pressure Matrix (Average vs Peak Utilization)
    # -------------------------------------------------------------
    print("\n[Step 3/5] Generating Chart 2: Workplace Pressure Matrix...")
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)

    # Quadrant reference lines
    ax.axvline(55.0, color="#888888", linestyle=":", linewidth=1.2)
    ax.axhline(80.0, color="#888888", linestyle=":", linewidth=1.2)

    quadrant_colors = {
        "Underutilized": "#4A90E2",
        "Peak-sensitive": "#E67E22",
        "Consistently active": "#27AE60",
        "Capacity-constrained": "#C0392B",
    }

    for quad, grp in df_pressure.groupby("PressureQuadrant"):
        ax.scatter(
            grp["AverageUtilizationPct"],
            grp["PeakUtilizationPct"],
            s=grp["UsableAreaSqM"] / 40.0,  # Bubble size by usable area
            color=quadrant_colors.get(quad, "#777777"),
            alpha=0.75,
            edgecolors="#333333",
            linewidth=1.0,
            label=f"{quad} ({len(grp)} assets)"
        )

    # Annotate top notable properties
    for _, row in df_pressure.iterrows():
        if row["AverageUtilizationPct"] < 45 or row["PeakUtilizationPct"] > 90 or row["UsableAreaSqM"] > 14000:
            ax.annotate(
                row["PropertyCode"],
                xy=(row["AverageUtilizationPct"], row["PeakUtilizationPct"]),
                xytext=(5, 4),
                textcoords="offset points",
                fontsize=7.5,
                color="#222222",
                fontweight="bold"
            )

    # Quadrant watermarks
    ax.text(25, 60, "UNDERUTILIZED\n(Candidates for consolidation)", fontsize=9, color="#4A90E2", alpha=0.6, ha="center")
    ax.text(25, 92, "PEAK-SENSITIVE\n(Mid-week surge / low avg)", fontsize=9, color="#E67E22", alpha=0.6, ha="center")
    ax.text(68, 65, "CONSISTENTLY ACTIVE\n(Predictable baseline)", fontsize=9, color="#27AE60", alpha=0.6, ha="center")
    ax.text(68, 92, "CAPACITY-CONSTRAINED\n(Critical expansion strain)", fontsize=9, color="#C0392B", alpha=0.6, ha="center")

    ax.set_xlabel("Average Daily Workplace Utilization (%)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Peak Workplace Utilization (%)", fontsize=10, fontweight="bold")
    ax.set_title("Workplace Pressure Matrix: Portfolio Distribution by Average vs. Peak Utilization", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlim(15, 85)
    ax.set_ylim(45, 102)
    ax.legend(frameon=True, facecolor="white", edgecolor="#CCCCCC", loc="lower right", fontsize=8.5)

    plt.tight_layout()
    chart2_path = os.path.join(CHARTS_DIR, "eda_pressure_matrix.png")
    plt.savefig(chart2_path)
    plt.close()
    print(f"  Saved -> {chart2_path}")

    # -------------------------------------------------------------
    # CHART 3: Cost Efficiency Scatter (Cost per Occupied Seat vs Utilization)
    # -------------------------------------------------------------
    print("\n[Step 4/5] Generating Chart 3: Cost Efficiency vs. Utilization...")
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    # Separate India and APAC
    for reg, grp in df_pressure.groupby("Region"):
        color = "#1F4E79" if reg == "India" else "#E07A5F"
        marker = "o" if reg == "India" else "s"
        ax.scatter(
            grp["AverageUtilizationPct"],
            grp["AnnualCostPerOccupiedSeatINR"] / 1000.0,
            s=grp["CapacitySeats"] / 2.0,
            color=color,
            marker=marker,
            alpha=0.75,
            edgecolors="#333333",
            linewidth=1.0,
            label=f"{reg} ({len(grp)} properties)"
        )

    # Annotate high-cost outliers (Singapore, Sydney, Mumbai HQ)
    for _, row in df_pressure.iterrows():
        cost_k = row["AnnualCostPerOccupiedSeatINR"] / 1000.0
        if cost_k > 350.0 or (row["AverageUtilizationPct"] < 45.0 and cost_k > 180.0):
            ax.annotate(
                f"{row['PropertyName'][:20]}...\n(₹{cost_k:,.0f}k/seat)",
                xy=(row["AverageUtilizationPct"], cost_k),
                xytext=(6, 5),
                textcoords="offset points",
                fontsize=7.5,
                color="#111111",
                fontweight="bold"
            )

    ax.set_xlabel("Average Workplace Utilization (%)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Annual Cost per Occupied Seat (₹ Thousands)", fontsize=10, fontweight="bold")
    ax.set_title("Economic Efficiency: Cost per Occupied Seat vs. Utilization by Geography", fontsize=12, fontweight="bold", pad=12)
    ax.axvline(55.0, color="#888888", linestyle="--", linewidth=1.0)
    ax.axhline(df_pressure["AnnualCostPerOccupiedSeatINR"].median() / 1000.0, color="#888888", linestyle="--", linewidth=1.0, label="Regional Median Cost/Occupied Seat")
    ax.legend(frameon=True, facecolor="white", edgecolor="#CCCCCC", loc="upper right", fontsize=8.5)

    plt.tight_layout()
    chart3_path = os.path.join(CHARTS_DIR, "eda_cost_vs_utilization.png")
    plt.savefig(chart3_path)
    plt.close()
    print(f"  Saved -> {chart3_path}")

    # -------------------------------------------------------------
    # CHART 4: Top Properties by Portfolio Attention Index
    # -------------------------------------------------------------
    print("\n[Step 5/5] Generating Chart 4: Portfolio Attention Index Ranking...")
    top_attention = df_attention.head(10).sort_values("PortfolioAttentionIndex", ascending=True)

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    bars = ax.barh(top_attention["PropertyName"], top_attention["PortfolioAttentionIndex"], color="#C0392B", alpha=0.85, height=0.6)

    ax.set_xlabel("Portfolio Attention Index (0 - 100 Analytical Prioritization Score)", fontsize=10, fontweight="bold")
    ax.set_title("Top 10 Locations Warranting Operational & Strategic Review", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlim(0, 100)

    for b, driver in zip(bars, top_attention["PrimaryAttentionDriver"]):
        w = b.get_width()
        y = b.get_y() + b.get_height() / 2
        ax.annotate(f"{w:.1f} ({driver})", xy=(w, y), xytext=(5, 0),
                    textcoords="offset points", ha="left", va="center", fontsize=8, color="#333333", fontweight="bold")

    plt.tight_layout()
    chart4_path = os.path.join(CHARTS_DIR, "eda_attention_ranking.png")
    plt.savefig(chart4_path)
    plt.close()
    print(f"  Saved -> {chart4_path}")

    # -------------------------------------------------------------
    # CHART 5: Meeting Room Mismatch & No-Show Behavior
    # -------------------------------------------------------------
    room_summary = df_room.groupby("RoomType").agg(
        AvgCapacity=("RoomCapacity", "mean"),
        AvgAttendees=("AverageAttendees", "mean"),
        NoShowRate=("NoShowCount", lambda s: (s.sum() / df_room.loc[s.index, "BookingCount"].sum()) * 100),
        UtilizationRate=("RoomUtilizationRate", lambda s: s.mean() * 100),
    ).reset_index()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)

    # Subplot 1: Attendees vs Capacity
    x_rm = np.arange(len(room_summary))
    w_rm = 0.35
    ax1.bar(x_rm - w_rm/2, room_summary["AvgCapacity"], w_rm, label="Rated Room Capacity (Chairs)", color="#4A90E2")
    ax1.bar(x_rm + w_rm/2, room_summary["AvgAttendees"], w_rm, label="Average Physical Attendees", color="#E67E22")
    ax1.set_xticks(x_rm)
    ax1.set_xticklabels(room_summary["RoomType"], fontsize=9)
    ax1.set_ylabel("Count of People / Seats", fontsize=9, fontweight="bold")
    ax1.set_title("Room Capacity vs. Actual Attendees", fontsize=10, fontweight="bold")
    ax1.legend(frameon=True, fontsize=8)

    # Subplot 2: No-show rate and Room Util
    ax2.bar(x_rm - w_rm/2, room_summary["UtilizationRate"], w_rm, label="Active Room Utilization %", color="#27AE60")
    ax2.bar(x_rm + w_rm/2, room_summary["NoShowRate"], w_rm, label="Ghost Booking / No-Show %", color="#C0392B")
    ax2.set_xticks(x_rm)
    ax2.set_xticklabels(room_summary["RoomType"], fontsize=9)
    ax2.set_ylabel("Percentage (%)", fontsize=9, fontweight="bold")
    ax2.set_title("Room Utilization vs. Ghost Booking Rate", fontsize=10, fontweight="bold")
    ax2.legend(frameon=True, fontsize=8)

    plt.tight_layout()
    chart5_path = os.path.join(CHARTS_DIR, "eda_room_mismatch.png")
    plt.savefig(chart5_path)
    plt.close()
    print(f"  Saved -> {chart5_path}")

    print("\nEDA profiling and diagnostic visualization suite completed successfully.")
    return {
        "status": "COMPLETED",
        "charts_generated": [chart1_path, chart2_path, chart3_path, chart4_path, chart5_path],
    }


if __name__ == "__main__":
    run_exploratory_analysis()
