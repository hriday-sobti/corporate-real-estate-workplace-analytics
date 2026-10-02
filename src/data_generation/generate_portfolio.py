"""Portfolio dimension generation engine.

Generates:
- dim_geography
- dim_facility_type
- dim_property
- dim_floor
- dim_space
- dim_lease
with deterministic identifiers, spatial consistency, and realistic layouts.
"""

from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from datetime import datetime

from src.data_generation.constants import (
    RANDOM_SEED,
    REPORTING_DATE_STR,
    GEOGRAPHIES,
    FACILITY_TYPES,
    PROPERTIES_CONFIG,
)


def generate_portfolio_dimensions() -> Tuple[
    pd.DataFrame,  # dim_geography
    pd.DataFrame,  # dim_facility_type
    pd.DataFrame,  # dim_property
    pd.DataFrame,  # dim_floor
    pd.DataFrame,  # dim_space
    pd.DataFrame,  # dim_lease
]:
    """Builds clean foundational dimensional tables."""
    np.random.seed(RANDOM_SEED)

    # 1. dim_geography
    df_geography = pd.DataFrame(GEOGRAPHIES)

    # 2. dim_facility_type
    df_facility_type = pd.DataFrame(FACILITY_TYPES)

    # Lookup helpers
    geo_lookup = {g["GeographyKey"]: g for g in GEOGRAPHIES}
    ft_lookup = {f["FacilityTypeKey"]: f for f in FACILITY_TYPES}

    # 3. dim_property
    properties_rows = []
    floor_rows = []
    space_rows = []
    lease_rows = []

    reporting_date = datetime.strptime(REPORTING_DATE_STR, "%Y-%m-%d").date()

    global_floor_key = 1001
    global_space_key = 5001
    global_lease_key = 201

    for idx, prop in enumerate(PROPERTIES_CONFIG, start=1):
        prop_key = idx
        prop_code = prop["PropertyCode"]
        prop_name = prop["PropertyName"]
        geo_key = prop["GeographyKey"]
        ft_key = prop["FacilityTypeKey"]
        ownership = prop["OwnershipType"]
        opening_year = prop["OpeningYear"]
        rentable_sqm = float(prop["RentableAreaSqM"])
        usable_sqm = float(prop["UsableAreaSqM"])
        total_capacity = int(prop["CapacitySeats"])
        assigned_hc = int(prop["AssignedHeadcount"])
        floor_count = int(prop["FloorCount"])

        geo = geo_lookup[geo_key]
        fx_rate = geo["FixedFXToINR"]
        base_rent_local = prop["BaseRentAnnualLocal"]
        base_rent_inr = round(base_rent_local * fx_rate, 2)

        # Count meeting rooms dynamically during space allocation
        prop_meeting_room_count = 0

        # Create Floors and Spaces
        area_per_floor = round(usable_sqm / floor_count, 2)
        seats_per_floor = total_capacity // floor_count
        remainder_seats = total_capacity % floor_count

        prop_floors = []
        for fl_idx in range(1, floor_count + 1):
            fl_key = global_floor_key
            global_floor_key += 1
            fl_code = f"{prop_code.replace('PROP-', '')}-FL{fl_idx:02d}"
            fl_name = f"Floor {fl_idx}"
            fl_usable = area_per_floor
            fl_seats = seats_per_floor + (1 if fl_idx <= remainder_seats else 0)

            prop_floors.append(fl_key)
            floor_rows.append({
                "FloorKey": fl_key,
                "PropertyKey": prop_key,
                "FloorNumber": fl_idx,
                "FloorCode": fl_code,
                "FloorName": fl_name,
                "UsableAreaSqM": fl_usable,
                "CapacitySeats": fl_seats,
            })

            # Create spaces per floor:
            # Space 1: Primary Open Workstation Bay A (45% of floor seats)
            # Space 2: Primary Open Workstation Bay B (35% of floor seats)
            # Space 3: Private Offices / Agile Pod (10% of floor seats)
            # Space 4: Small Meeting Room (1 room, 4-6 seats)
            # Space 5: Large Meeting Room / Boardroom (1 room, 10-14 seats)
            # Space 6: Focus / Phone Rooms (3-4 seats)
            # Space 7: Collaboration / Lounge (casual touchdown, 5 seats)
            s1_seats = int(fl_seats * 0.48)
            s2_seats = int(fl_seats * 0.36)
            s3_seats = max(2, int(fl_seats * 0.08))
            s6_seats = max(2, int(fl_seats * 0.04))
            s1_2_3_sum = s1_seats + s2_seats + s3_seats + s6_seats
            # Adjust s1 so desk seats match fl_seats
            s1_seats += (fl_seats - s1_2_3_sum)

            # Space allocations for this floor
            floor_spaces = [
                {
                    "SpaceCode": f"{fl_code}-WKA",
                    "SpaceName": f"Open Workstation Bay A - {fl_name}",
                    "SpaceType": "Open Workstation",
                    "AreaSqM": round(fl_usable * 0.46, 2),
                    "Capacity": s1_seats,
                    "IsBookable": False,
                },
                {
                    "SpaceCode": f"{fl_code}-WKB",
                    "SpaceName": f"Open Workstation Bay B - {fl_name}",
                    "SpaceType": "Open Workstation",
                    "AreaSqM": round(fl_usable * 0.34, 2),
                    "Capacity": s2_seats,
                    "IsBookable": False,
                },
                {
                    "SpaceCode": f"{fl_code}-OFF",
                    "SpaceName": f"Executive & Managerial Pod - {fl_name}",
                    "SpaceType": "Private Office",
                    "AreaSqM": round(fl_usable * 0.07, 2),
                    "Capacity": s3_seats,
                    "IsBookable": False,
                },
                {
                    "SpaceCode": f"{fl_code}-SMR",
                    "SpaceName": f"Huddle Meeting Room - {fl_name}",
                    "SpaceType": "Small Meeting Room",
                    "AreaSqM": round(fl_usable * 0.04, 2),
                    "Capacity": 6,
                    "IsBookable": True,
                },
                {
                    "SpaceCode": f"{fl_code}-LMR",
                    "SpaceName": f"Conference Room - {fl_name}",
                    "SpaceType": "Large Meeting Room",
                    "AreaSqM": round(fl_usable * 0.05, 2),
                    "Capacity": 12,
                    "IsBookable": True,
                },
                {
                    "SpaceCode": f"{fl_code}-FOC",
                    "SpaceName": f"Focus & Phone Booths - {fl_name}",
                    "SpaceType": "Focus Room",
                    "AreaSqM": round(fl_usable * 0.02, 2),
                    "Capacity": s6_seats,
                    "IsBookable": False,
                },
                {
                    "SpaceCode": f"{fl_code}-COL",
                    "SpaceName": f"Agile Collaboration Lounge - {fl_name}",
                    "SpaceType": "Collaboration Area",
                    "AreaSqM": round(fl_usable * 0.02, 2),
                    "Capacity": 8,
                    "IsBookable": False,
                },
            ]

            # If Floor 1, add Reception
            if fl_idx == 1:
                floor_spaces.append({
                    "SpaceCode": f"{fl_code}-REC",
                    "SpaceName": f"Main Reception & Welcome Hub",
                    "SpaceType": "Reception / Shared Support",
                    "AreaSqM": round(fl_usable * 0.04, 2),
                    "Capacity": 4,
                    "IsBookable": False,
                })

            for sp in floor_spaces:
                sp_key = global_space_key
                global_space_key += 1
                if sp["SpaceType"] in ["Small Meeting Room", "Large Meeting Room"]:
                    prop_meeting_room_count += 1

                space_rows.append({
                    "SpaceKey": sp_key,
                    "FloorKey": fl_key,
                    "PropertyKey": prop_key,
                    "SpaceCode": sp["SpaceCode"],
                    "SpaceName": sp["SpaceName"],
                    "SpaceType": sp["SpaceType"],
                    "AreaSqM": sp["AreaSqM"],
                    "Capacity": sp["Capacity"],
                    "IsBookable": sp["IsBookable"],
                })

        # Property record
        properties_rows.append({
            "PropertyKey": prop_key,
            "PropertyCode": prop_code,
            "PropertyName": prop_name,
            "GeographyKey": geo_key,
            "FacilityTypeKey": ft_key,
            "OwnershipType": ownership,
            "PropertyStatus": "Operational",
            "OpeningYear": opening_year,
            "RentableAreaSqM": rentable_sqm,
            "UsableAreaSqM": usable_sqm,
            "CapacitySeats": total_capacity,
            "AssignedHeadcount": assigned_hc,
            "FloorCount": floor_count,
            "MeetingRoomCount": prop_meeting_room_count,
            "BaseRentAnnualINR": base_rent_inr,
        })

        # Lease Record
        lease_start = datetime.strptime(prop["LeaseStart"], "%Y-%m-%d").date()
        lease_end = datetime.strptime(prop["LeaseEnd"], "%Y-%m-%d").date()

        # Compute horizon category
        if ownership == "Owned":
            expiry_cat = "Owned"
            lease_status = "Active (Owned)"
        else:
            days_to_expiry = (lease_end - reporting_date).days
            if days_to_expiry < 0:
                expiry_cat = "Expired"
                lease_status = "Expired"
            elif days_to_expiry <= 182:  # 6 months
                expiry_cat = "Expiring <= 6M"
                lease_status = "Expiring Near-Term"
            elif days_to_expiry <= 365:  # 12 months
                expiry_cat = "Expiring 6-12M"
                lease_status = "Active"
            elif days_to_expiry <= 730:  # 24 months
                expiry_cat = "Expiring 12-24M"
                lease_status = "Active"
            else:
                expiry_cat = "Horizon > 24M"
                lease_status = "Active"

        lease_rows.append({
            "LeaseKey": global_lease_key,
            "PropertyKey": prop_key,
            "LeaseContractNumber": f"LSE-{prop_code.replace('PROP-', '')}-{lease_start.year}",
            "LeaseStartDate": lease_start.strftime("%Y-%m-%d"),
            "LeaseEndDate": lease_end.strftime("%Y-%m-%d") if ownership == "Leased" else "N/A (Owned)",
            "LeaseType": "Triple Net (NNN)" if ownership == "Leased" else "Corporate Freehold",
            "RenewalOption": "5-Year Extension at Market Rate" if ownership == "Leased" else "Not Applicable",
            "NoticePeriodMonths": 6 if ownership == "Leased" else 0,
            "AnnualRentINR": base_rent_inr,
            "LeaseStatus": lease_status,
            "ExpiryHorizonCategory": expiry_cat,
        })
        global_lease_key += 1

    df_property = pd.DataFrame(properties_rows)
    df_floor = pd.DataFrame(floor_rows)
    df_space = pd.DataFrame(space_rows)
    df_lease = pd.DataFrame(lease_rows)

    return (
        df_geography,
        df_facility_type,
        df_property,
        df_floor,
        df_space,
        df_lease,
    )
