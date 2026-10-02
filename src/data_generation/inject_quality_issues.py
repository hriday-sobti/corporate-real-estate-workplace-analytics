"""Quality issues injector and manifest generator.

Intentionally injects controlled realistic operational imperfections into RAW datasets:
- Missing fields (city, floor, lease dates)
- Inconsistent spelling and country-city mapping
- Duplicate property and observation rows
- Area unit/ratio violations (Usable > Rentable)
- Negative financial cost entries
- Physical impossibilities (occupants > capacity, utilization > 100%)
- Attended room bookings > scheduled bookings

Produces:
- data/quality_issue_manifest.csv
- data/raw/*.csv
"""

from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd


def inject_quality_issues_and_create_raw(
    df_geography: pd.DataFrame,
    df_facility_type: pd.DataFrame,
    df_property: pd.DataFrame,
    df_floor: pd.DataFrame,
    df_space: pd.DataFrame,
    df_lease: pd.DataFrame,
    df_date: pd.DataFrame,
    df_utilization: pd.DataFrame,
    df_room_utilization: pd.DataFrame,
    df_cost: pd.DataFrame,
    df_headcount: pd.DataFrame,
) -> Tuple[
    Dict[str, pd.DataFrame],  # raw_dfs
    pd.DataFrame,             # quality_manifest
]:
    """Creates raw versions of all tables with controlled injected defects and logs manifest."""
    manifest_rows = []
    issue_counter = 1

    def add_issue(table: str, rec_id: str, issue_type: str, rule: str, inj_val: Any, exp_val: Any, severity: str):
        nonlocal issue_counter
        manifest_rows.append({
            "issue_id": f"DQ-ISS-{issue_counter:03d}",
            "table_name": table,
            "record_identifier": str(rec_id),
            "issue_type": issue_type,
            "expected_rule": rule,
            "injected_value": str(inj_val),
            "expected_correct_value": str(exp_val),
            "severity": severity,
        })
        issue_counter += 1

    # Deep copies for raw
    raw_prop = df_property.copy()
    raw_lease = df_lease.copy()
    raw_space = df_space.copy()
    raw_cost = df_cost.copy()
    raw_util = df_utilization.copy()
    raw_room = df_room_utilization.copy()
    raw_floor = df_floor.copy()
    raw_geo = df_geography.copy()
    raw_ft = df_facility_type.copy()
    raw_date = df_date.copy()
    raw_hc = df_headcount.copy()

    # --- 1. Properties Injections ---
    # Add City and Country columns to raw_prop to represent typical denormalized source export
    geo_map = df_geography.set_index("GeographyKey").to_dict(orient="index")
    raw_prop["City"] = raw_prop["GeographyKey"].map(lambda k: geo_map[k]["City"])
    raw_prop["Country"] = raw_prop["GeographyKey"].map(lambda k: geo_map[k]["Country"])

    # Issue 1: Missing city
    idx1 = raw_prop[raw_prop["PropertyCode"] == "PROP-BOM-01"].index[0]
    orig_city = raw_prop.at[idx1, "City"]
    raw_prop.at[idx1, "City"] = ""
    add_issue("raw_properties", "PROP-BOM-01", "DQ009", "City must not be null or blank", "", orig_city, "Medium")

    # Issue 2: Inconsistent country-city mapping
    idx2 = raw_prop[raw_prop["PropertyCode"] == "PROP-BLR-02"].index[0]
    orig_country = raw_prop.at[idx2, "Country"]
    raw_prop.at[idx2, "Country"] = "Australia"
    add_issue("raw_properties", "PROP-BLR-02", "DQ005", "City must map to valid country", "Australia", orig_country, "High")

    # Issue 3: Inconsistent spelling / trailing whitespace
    idx4 = raw_prop[raw_prop["PropertyCode"] == "PROP-PNQ-03"].index[0]
    raw_prop.at[idx4, "City"] = "PUNE "
    add_issue("raw_properties", "PROP-PNQ-03", "DQ005", "City name must be properly capitalized and trimmed", "PUNE ", "Pune", "Medium")

    # Issue 4: Usable area > Rentable area
    idx5 = raw_prop[raw_prop["PropertyCode"] == "PROP-MAA-02"].index[0]
    orig_usable = raw_prop.at[idx5, "UsableAreaSqM"]
    raw_prop.at[idx5, "UsableAreaSqM"] = 8500.0  # Rentable is 7500.0!
    add_issue("raw_properties", "PROP-MAA-02", "DQ006", "Usable area cannot exceed rentable area", "8500.0", str(orig_usable), "High")

    # Issue 5: Duplicate property record
    dup_row = raw_prop[raw_prop["PropertyCode"] == "PROP-BOM-02"].copy()
    raw_prop = pd.concat([raw_prop, dup_row], ignore_index=True)
    add_issue("raw_properties", "PROP-BOM-02", "DQ001", "Property code must be unique", "Duplicate Record Injected", "Single Unique Record", "Critical")

    # --- 2. Lease Injections ---
    # Issue 6: Inverted lease dates
    idx6 = raw_lease[raw_lease["LeaseContractNumber"] == "LSE-DEL-01-2021"].index[0]
    orig_s = raw_lease.at[idx6, "LeaseStartDate"]
    orig_e = raw_lease.at[idx6, "LeaseEndDate"]
    raw_lease.at[idx6, "LeaseStartDate"] = orig_e
    raw_lease.at[idx6, "LeaseEndDate"] = orig_s
    add_issue("raw_leases", "LSE-DEL-01-2021", "DQ004", "Lease end date cannot precede lease start date", f"Start: {orig_e}, End: {orig_s}", f"Start: {orig_s}, End: {orig_e}", "Critical")

    # Issue 7: Another inverted lease date
    idx7 = raw_lease[raw_lease["LeaseContractNumber"] == "LSE-KUL-02-2023"].index[0]
    orig_s7 = raw_lease.at[idx7, "LeaseStartDate"]
    orig_e7 = raw_lease.at[idx7, "LeaseEndDate"]
    raw_lease.at[idx7, "LeaseStartDate"] = orig_e7
    raw_lease.at[idx7, "LeaseEndDate"] = orig_s7
    add_issue("raw_leases", "LSE-KUL-02-2023", "DQ004", "Lease end date cannot precede lease start date", f"Start: {orig_e7}, End: {orig_s7}", f"Start: {orig_s7}, End: {orig_e7}", "Critical")

    # Issue 8: Missing lease end date
    idx8 = raw_lease[raw_lease["LeaseContractNumber"] == "LSE-BKK-02-2023"].index[0]
    orig_e8 = raw_lease.at[idx8, "LeaseEndDate"]
    raw_lease.at[idx8, "LeaseEndDate"] = ""
    add_issue("raw_leases", "LSE-BKK-02-2023", "DQ009", "Lease end date must not be null or empty", "", orig_e8, "High")

    # --- 3. Cost Injections ---
    # Issues 9-11: Negative operating expenses
    idx9 = raw_cost[raw_cost["CostFactKey"] == 3045].index[0]
    orig_c9 = raw_cost.at[idx9, "RentCost"]
    raw_cost.at[idx9, "RentCost"] = -abs(orig_c9)
    raw_cost.at[idx9, "TotalOperatingCostLocal"] = round(raw_cost.at[idx9, "TotalOperatingCostLocal"] - 2 * abs(orig_c9), 2)
    raw_cost.at[idx9, "TotalOperatingCostINR"] = round(raw_cost.at[idx9, "TotalOperatingCostLocal"] * raw_cost.at[idx9, "FXRateToINR"], 2)
    add_issue("raw_property_costs", "COST-3045", "DQ008", "Operating cost values cannot be negative", str(-abs(orig_c9)), str(orig_c9), "High")

    idx10 = raw_cost[raw_cost["CostFactKey"] == 3120].index[0]
    orig_c10 = raw_cost.at[idx10, "EnergyCost"]
    raw_cost.at[idx10, "EnergyCost"] = -abs(orig_c10)
    add_issue("raw_property_costs", "COST-3120", "DQ008", "Energy cost cannot be negative", str(-abs(orig_c10)), str(orig_c10), "High")

    idx11 = raw_cost[raw_cost["CostFactKey"] == 3280].index[0]
    orig_c11 = raw_cost.at[idx11, "FacilitiesCost"]
    raw_cost.at[idx11, "FacilitiesCost"] = -abs(orig_c11)
    add_issue("raw_property_costs", "COST-3280", "DQ008", "Facilities cost cannot be negative", str(-abs(orig_c11)), str(orig_c11), "High")

    # --- 4. Spaces Injections ---
    # Issue 12: Missing space type
    idx12 = raw_space[raw_space["SpaceKey"] == 5015].index[0]
    orig_st12 = raw_space.at[idx12, "SpaceType"]
    raw_space.at[idx12, "SpaceType"] = ""
    add_issue("raw_spaces", "SP-5015", "DQ009", "Space type must not be blank", "", orig_st12, "Medium")

    # Issue 13: Inconsistent case
    idx13 = raw_space[raw_space["SpaceKey"] == 5120].index[0]
    raw_space.at[idx13, "SpaceType"] = "open_workstation"
    add_issue("raw_spaces", "SP-5120", "DQ005", "Space type must follow standard title case classification", "open_workstation", "Open Workstation", "Medium")

    # --- 5. Daily Utilization Injections ---
    # Issues 14-27: Utilization > 100% and occupants > capacity (14 instances)
    util_sample_indices = [105, 520, 1420, 2890, 4510, 8920, 15300, 24100, 38500, 52100, 71200, 89400, 102300, 115000]
    for u_idx in util_sample_indices:
        if u_idx < len(raw_util):
            rec_id = f"UTIL-{raw_util.at[u_idx, 'UtilizationFactKey']}"
            cap = raw_util.at[u_idx, "Capacity"]
            orig_occ = raw_util.at[u_idx, "ActualOccupants"]
            orig_rate = raw_util.at[u_idx, "UtilizationRate"]
            # Inject 140% utilization
            raw_util.at[u_idx, "ActualOccupants"] = int(cap * 1.45)
            raw_util.at[u_idx, "AverageOccupancy"] = round(cap * 1.38, 2)
            raw_util.at[u_idx, "PeakOccupants"] = int(cap * 1.55)
            raw_util.at[u_idx, "OccupiedHours"] = round(cap * 1.38 * 10.0, 2)
            raw_util.at[u_idx, "UtilizationRate"] = 1.3800
            raw_util.at[u_idx, "PeakUtilizationRate"] = 1.5500
            add_issue("raw_utilization", rec_id, "DQ003", "Utilization rate must be between 0% and 100%", "1.3800", str(orig_rate), "Critical")

    # Issues 28-35: Unexpected null/missing AverageOccupancy (8 instances)
    null_util_indices = [300, 1200, 7800, 19400, 33100, 47800, 68900, 95400]
    for n_idx in null_util_indices:
        if n_idx < len(raw_util):
            rec_id = f"UTIL-{raw_util.at[n_idx, 'UtilizationFactKey']}"
            orig_avg = raw_util.at[n_idx, "AverageOccupancy"]
            raw_util.at[n_idx, "AverageOccupancy"] = np.nan
            add_issue("raw_utilization", rec_id, "DQ009", "Average occupancy must not be null", "NaN / NULL", str(orig_avg), "High")

    # Issues 36-39: Duplicate observations (4 duplicate rows appended)
    dup_util_rows = raw_util.iloc[[150, 4500, 25000, 60000]].copy()
    raw_util = pd.concat([raw_util, dup_util_rows], ignore_index=True)
    for _, dup in dup_util_rows.iterrows():
        rec_id = f"UTIL-{dup['UtilizationFactKey']}"
        add_issue("raw_utilization", rec_id, "DQ010", "Only one observation per space per date", "Duplicate Observation Row", "Single Valid Record", "High")

    # --- 6. Room Utilization Injections ---
    # Issues 40-44: Attended booking count > total booking count (5 instances)
    room_sample_indices = [45, 890, 3420, 12500, 28400]
    for r_idx in room_sample_indices:
        if r_idx < len(raw_room):
            rec_id = f"ROOM-{raw_room.at[r_idx, 'RoomFactKey']}"
            bk_cnt = raw_room.at[r_idx, "BookingCount"]
            orig_att = raw_room.at[r_idx, "AttendedBookingCount"]
            inj_att = bk_cnt + 3
            raw_room.at[r_idx, "AttendedBookingCount"] = inj_att
            add_issue("raw_room_utilization", rec_id, "DQ011", "Attended bookings cannot exceed total scheduled bookings", str(inj_att), str(bk_cnt), "Medium")

    # Build manifest DataFrame
    df_manifest = pd.DataFrame(manifest_rows)

    raw_dfs = {
        "raw_geography": raw_geo,
        "raw_facility_type": raw_ft,
        "raw_properties": raw_prop,
        "raw_floors": raw_floor,
        "raw_spaces": raw_space,
        "raw_leases": raw_lease,
        "raw_date": raw_date,
        "raw_utilization": raw_util,
        "raw_room_utilization": raw_room,
        "raw_property_costs": raw_cost,
        "raw_headcount": raw_hc,
    }

    return raw_dfs, df_manifest
