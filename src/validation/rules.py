"""Codified Data Quality Rules (DQ001 - DQ012).

Implements programmatic evaluators for the 6 core quality dimensions:
Uniqueness, Validity, Temporal, Consistency, Referential, Completeness.
"""

from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np


def check_dq001_property_uniqueness(df_prop: pd.DataFrame) -> List[Dict[str, Any]]:
    """DQ001: Property code must be unique."""
    duplicates = df_prop[df_prop.duplicated(subset=["PropertyCode"], keep=False)]
    failures = []
    for _, row in duplicates.iterrows():
        failures.append({
            "rule_id": "DQ001",
            "dimension": "Uniqueness",
            "table_name": "raw_properties",
            "record_identifier": str(row["PropertyCode"]),
            "column": "PropertyCode",
            "severity": "Critical",
            "message": f"Duplicate property code found: {row['PropertyCode']}",
            "value": str(row["PropertyCode"]),
        })
    return failures


def check_dq002_occupants_within_capacity(df_util: pd.DataFrame) -> List[Dict[str, Any]]:
    """DQ002: Actual occupants cannot exceed structural capacity."""
    violations = df_util[df_util["ActualOccupants"] > df_util["Capacity"]]
    failures = []
    for _, row in violations.iterrows():
        failures.append({
            "rule_id": "DQ002",
            "dimension": "Validity",
            "table_name": "raw_utilization",
            "record_identifier": f"UTIL-{row['UtilizationFactKey']}",
            "column": "ActualOccupants",
            "severity": "Critical",
            "message": f"Actual occupants ({row['ActualOccupants']}) exceeds capacity ({row['Capacity']})",
            "value": f"{row['ActualOccupants']} > {row['Capacity']}",
        })
    return failures


def check_dq003_utilization_rate_bounds(df_util: pd.DataFrame) -> List[Dict[str, Any]]:
    """DQ003: Daily utilization rate must fall strictly between 0.0 and 1.0 (0% to 100%)."""
    violations = df_util[(df_util["UtilizationRate"] < 0.0) | (df_util["UtilizationRate"] > 1.0)]
    failures = []
    for _, row in violations.iterrows():
        failures.append({
            "rule_id": "DQ003",
            "dimension": "Validity",
            "table_name": "raw_utilization",
            "record_identifier": f"UTIL-{row['UtilizationFactKey']}",
            "column": "UtilizationRate",
            "severity": "Critical",
            "message": f"Utilization rate {row['UtilizationRate']:.4f} is outside feasible [0.0, 1.0] range",
            "value": str(row["UtilizationRate"]),
        })
    return failures


def check_dq004_lease_dates_chronology(df_lease: pd.DataFrame) -> List[Dict[str, Any]]:
    """DQ004: Lease end date cannot precede lease start date."""
    failures = []
    for _, row in df_lease.iterrows():
        s = str(row.get("LeaseStartDate", "")).strip()
        e = str(row.get("LeaseEndDate", "")).strip()
        if s and e and e != "N/A (Owned)" and not e.startswith("N/A"):
            try:
                if pd.to_datetime(e) < pd.to_datetime(s):
                    failures.append({
                        "rule_id": "DQ004",
                        "dimension": "Temporal Validity",
                        "table_name": "raw_leases",
                        "record_identifier": str(row["LeaseContractNumber"]),
                        "column": "LeaseEndDate",
                        "severity": "Critical",
                        "message": f"Lease end date ({e}) precedes start date ({s})",
                        "value": f"Start={s}, End={e}",
                    })
            except Exception:
                pass
    return failures


def check_dq005_geographic_and_naming_consistency(
    df_prop: pd.DataFrame,
    df_geo: pd.DataFrame,
    df_space: pd.DataFrame
) -> List[Dict[str, Any]]:
    """DQ005: Consistency in city-to-country mapping and casing."""
    failures = []
    valid_city_country = df_geo.set_index("City")["Country"].to_dict()

    for _, row in df_prop.iterrows():
        city_raw = str(row.get("City", ""))
        country_raw = str(row.get("Country", ""))
        city = city_raw.strip()

        # Check whitespace or casing
        if city_raw != city or (city.isupper() and len(city) > 3):
            failures.append({
                "rule_id": "DQ005",
                "dimension": "Consistency",
                "table_name": "raw_properties",
                "record_identifier": str(row["PropertyCode"]),
                "column": "City",
                "severity": "Medium",
                "message": f"City casing or whitespace issue: '{city_raw}'",
                "value": city_raw,
            })

        # Check country mapping
        if city in valid_city_country:
            expected_country = valid_city_country[city]
            if country_raw.strip() != expected_country:
                failures.append({
                    "rule_id": "DQ005",
                    "dimension": "Consistency",
                    "table_name": "raw_properties",
                    "record_identifier": str(row["PropertyCode"]),
                    "column": "Country",
                    "severity": "High",
                    "message": f"City '{city}' mapped to '{country_raw}', expected '{expected_country}'",
                    "value": country_raw,
                })

    # Space classification formatting
    for _, row in df_space.iterrows():
        st = str(row.get("SpaceType", ""))
        if "_" in st or (st.islower() and len(st) > 0):
            failures.append({
                "rule_id": "DQ005",
                "dimension": "Consistency",
                "table_name": "raw_spaces",
                "record_identifier": str(row["SpaceKey"]),
                "column": "SpaceType",
                "severity": "Medium",
                "message": f"Non-standard space type casing: '{st}'",
                "value": st,
            })

    return failures


def check_dq006_usable_vs_rentable_area(df_prop: pd.DataFrame) -> List[Dict[str, Any]]:
    """DQ006: Usable area cannot exceed gross rentable area."""
    violations = df_prop[df_prop["UsableAreaSqM"] > df_prop["RentableAreaSqM"]]
    failures = []
    for _, row in violations.iterrows():
        failures.append({
            "rule_id": "DQ006",
            "dimension": "Spatial Validity",
            "table_name": "raw_properties",
            "record_identifier": str(row["PropertyCode"]),
            "column": "UsableAreaSqM",
            "severity": "High",
            "message": f"Usable area ({row['UsableAreaSqM']}) exceeds rentable area ({row['RentableAreaSqM']})",
            "value": f"{row['UsableAreaSqM']} > {row['RentableAreaSqM']}",
        })
    return failures


def check_dq007_referential_integrity(
    df_util: pd.DataFrame,
    df_space: pd.DataFrame,
    df_prop: pd.DataFrame
) -> List[Dict[str, Any]]:
    """DQ007: Foreign keys in fact tables must resolve to parent dimensions."""
    failures = []
    valid_spaces = set(df_space["SpaceKey"].unique())
    valid_props = set(df_prop["PropertyKey"].unique())

    orphaned_spaces = df_util[~df_util["SpaceKey"].isin(valid_spaces)]
    for _, row in orphaned_spaces.head(10).iterrows():
        failures.append({
            "rule_id": "DQ007",
            "dimension": "Referential Integrity",
            "table_name": "raw_utilization",
            "record_identifier": f"UTIL-{row['UtilizationFactKey']}",
            "column": "SpaceKey",
            "severity": "Critical",
            "message": f"Orphaned SpaceKey: {row['SpaceKey']}",
            "value": str(row["SpaceKey"]),
        })

    orphaned_props = df_util[~df_util["PropertyKey"].isin(valid_props)]
    for _, row in orphaned_props.head(10).iterrows():
        failures.append({
            "rule_id": "DQ007",
            "dimension": "Referential Integrity",
            "table_name": "raw_utilization",
            "record_identifier": f"UTIL-{row['UtilizationFactKey']}",
            "column": "PropertyKey",
            "severity": "Critical",
            "message": f"Orphaned PropertyKey: {row['PropertyKey']}",
            "value": str(row["PropertyKey"]),
        })

    return failures


def check_dq008_non_negative_costs(df_cost: pd.DataFrame) -> List[Dict[str, Any]]:
    """DQ008: Operating cost values cannot be negative."""
    cost_cols = ["RentCost", "ServiceCharge", "EnergyCost", "FacilitiesCost", "MaintenanceCost", "OtherOperatingCost"]
    failures = []
    for col in cost_cols:
        if col in df_cost.columns:
            negs = df_cost[df_cost[col] < 0]
            for _, row in negs.iterrows():
                failures.append({
                    "rule_id": "DQ008",
                    "dimension": "Financial Validity",
                    "table_name": "raw_property_costs",
                    "record_identifier": f"COST-{row['CostFactKey']}",
                    "column": col,
                    "severity": "High",
                    "message": f"Negative cost detected in {col}: {row[col]}",
                    "value": str(row[col]),
                })
    return failures


def check_dq009_mandatory_completeness(
    df_prop: pd.DataFrame,
    df_lease: pd.DataFrame,
    df_space: pd.DataFrame,
    df_util: pd.DataFrame
) -> List[Dict[str, Any]]:
    """DQ009: Mandatory fields must not be null, empty string, or NaN."""
    failures = []

    # Properties
    for col in ["City", "PropertyCode", "OwnershipType"]:
        missing = df_prop[df_prop[col].isna() | (df_prop[col].astype(str).str.strip() == "")]
        for _, row in missing.iterrows():
            failures.append({
                "rule_id": "DQ009",
                "dimension": "Completeness",
                "table_name": "raw_properties",
                "record_identifier": str(row["PropertyCode"]),
                "column": col,
                "severity": "Medium",
                "message": f"Missing mandatory field '{col}'",
                "value": "NULL / Empty",
            })

    # Leases
    missing_lease = df_lease[df_lease["LeaseEndDate"].isna() | (df_lease["LeaseEndDate"].astype(str).str.strip() == "")]
    for _, row in missing_lease.iterrows():
        failures.append({
            "rule_id": "DQ009",
            "dimension": "Completeness",
            "table_name": "raw_leases",
            "record_identifier": str(row["LeaseContractNumber"]),
            "column": "LeaseEndDate",
            "severity": "High",
            "message": "Missing contractual lease end date",
            "value": "NULL / Empty",
        })

    # Spaces
    missing_space = df_space[df_space["SpaceType"].isna() | (df_space["SpaceType"].astype(str).str.strip() == "")]
    for _, row in missing_space.iterrows():
        failures.append({
            "rule_id": "DQ009",
            "dimension": "Completeness",
            "table_name": "raw_spaces",
            "record_identifier": str(row["SpaceKey"]),
            "column": "SpaceType",
            "severity": "Medium",
            "message": "Missing space category classification",
            "value": "NULL / Empty",
        })

    # Utilization
    null_avg = df_util[df_util["AverageOccupancy"].isna()]
    for _, row in null_avg.iterrows():
        failures.append({
            "rule_id": "DQ009",
            "dimension": "Completeness",
            "table_name": "raw_utilization",
            "record_identifier": f"UTIL-{row['UtilizationFactKey']}",
            "column": "AverageOccupancy",
            "severity": "High",
            "message": "Missing AverageOccupancy value",
            "value": "NaN / NULL",
        })

    return failures


def check_dq010_daily_observation_uniqueness(df_util: pd.DataFrame) -> List[Dict[str, Any]]:
    """DQ010: Only one observation record per SpaceKey per DateKey."""
    duplicates = df_util[df_util.duplicated(subset=["DateKey", "SpaceKey"], keep=False)]
    failures = []
    for _, row in duplicates.iterrows():
        failures.append({
            "rule_id": "DQ010",
            "dimension": "Uniqueness",
            "table_name": "raw_utilization",
            "record_identifier": f"UTIL-{row['UtilizationFactKey']}",
            "column": "DateKey+SpaceKey",
            "severity": "High",
            "message": f"Duplicate observation for SpaceKey {row['SpaceKey']} on DateKey {row['DateKey']}",
            "value": f"DateKey={row['DateKey']}, SpaceKey={row['SpaceKey']}",
        })
    return failures


def check_dq011_room_attended_within_scheduled(df_room: pd.DataFrame) -> List[Dict[str, Any]]:
    """DQ011: Attended meeting bookings cannot exceed total scheduled bookings."""
    violations = df_room[df_room["AttendedBookingCount"] > df_room["BookingCount"]]
    failures = []
    for _, row in violations.iterrows():
        failures.append({
            "rule_id": "DQ011",
            "dimension": "Range Validity",
            "table_name": "raw_room_utilization",
            "record_identifier": f"ROOM-{row['RoomFactKey']}",
            "column": "AttendedBookingCount",
            "severity": "Medium",
            "message": f"Attended bookings ({row['AttendedBookingCount']}) exceeds scheduled ({row['BookingCount']})",
            "value": f"{row['AttendedBookingCount']} > {row['BookingCount']}",
        })
    return failures


def check_dq012_density_plausibility(df_prop: pd.DataFrame) -> List[Dict[str, Any]]:
    """DQ012: Workplace density (m2/seat) must fall within plausible limits (5.0 to 25.0)."""
    failures = []
    for _, row in df_prop.iterrows():
        usable = float(row.get("UsableAreaSqM", 0))
        seats = int(row.get("CapacitySeats", 1))
        density = usable / seats if seats > 0 else 0
        if density < 5.0 or density > 25.0:
            failures.append({
                "rule_id": "DQ012",
                "dimension": "Density Plausibility",
                "table_name": "raw_properties",
                "record_identifier": str(row["PropertyCode"]),
                "column": "UsableAreaSqM / CapacitySeats",
                "severity": "Warning",
                "message": f"Workplace density {density:.1f} m2/seat is outside typical limits (5.0 - 25.0)",
                "value": f"{density:.2f} m2/seat",
            })
    return failures
