"""Time-series fact tables generation engine.

Generates:
- dim_date (2024-10-01 to 2026-09-30, 730 days)
- fact_daily_workplace_utilization (~124,000 rows)
- fact_room_utilization (~35,000 rows)
- fact_monthly_property_cost (600 rows)
- fact_headcount (600 rows)

Incorporates:
- Realistic day-of-week utilization curve (Tue-Thu peaks, soft Fri/Mon)
- Seasonal weather/holiday patterns (Indian Diwali/summer HVAC, APAC Lunar New Year)
- Room capacity mismatch (2-3 attendees in 12-person boardrooms)
- Ghost booking / no-show rates (15-30%)
- Currency translations to INR using fixed reference rates
"""

from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta

from src.data_generation.constants import (
    RANDOM_SEED,
    REPORTING_DATE_STR,
    GEOGRAPHIES,
    PROPERTIES_CONFIG,
)


def generate_time_series(
    df_property: pd.DataFrame,
    df_floor: pd.DataFrame,
    df_space: pd.DataFrame,
) -> Tuple[
    pd.DataFrame,  # dim_date
    pd.DataFrame,  # fact_daily_workplace_utilization
    pd.DataFrame,  # fact_room_utilization
    pd.DataFrame,  # fact_monthly_property_cost
    pd.DataFrame,  # fact_headcount
]:
    """Generates all temporal dimensions and fact tables."""
    np.random.seed(RANDOM_SEED)

    start_date = date(2024, 10, 1)
    end_date = date(2026, 9, 30)
    total_days = (end_date - start_date).days + 1

    # Regional holidays lookup for realism
    holidays_set = {
        # 2024
        date(2024, 10, 2): "Gandhi Jayanti",
        date(2024, 10, 31): "Diwali",
        date(2024, 11, 1): "Diwali Holiday",
        date(2024, 12, 25): "Christmas Day",
        # 2025
        date(2025, 1, 1): "New Year's Day",
        date(2025, 1, 26): "Republic Day",
        date(2025, 1, 29): "Lunar New Year",
        date(2025, 1, 30): "Lunar New Year Holiday",
        date(2025, 3, 14): "Holi",
        date(2025, 4, 18): "Good Friday",
        date(2025, 5, 1): "Labour Day",
        date(2025, 8, 15): "Independence Day",
        date(2025, 10, 20): "Diwali",
        date(2025, 10, 21): "Diwali Holiday",
        date(2025, 12, 25): "Christmas Day",
        # 2026
        date(2026, 1, 1): "New Year's Day",
        date(2026, 1, 26): "Republic Day",
        date(2026, 2, 17): "Lunar New Year",
        date(2026, 2, 18): "Lunar New Year Holiday",
        date(2026, 4, 3): "Good Friday",
        date(2026, 5, 1): "Labour Day",
        date(2026, 8, 15): "Independence Day",
    }

    # 1. dim_date
    date_rows = []
    current_dt = start_date
    while current_dt <= end_date:
        d_key = int(current_dt.strftime("%Y%m%d"))
        y = current_dt.year
        m = current_dt.month
        q = (m - 1) // 3 + 1
        dow = current_dt.isoweekday()  # 1=Mon, 7=Sun
        is_wkday = (dow <= 5)
        is_holiday = (current_dt in holidays_set)
        is_working = is_wkday and not is_holiday

        date_rows.append({
            "DateKey": d_key,
            "FullDate": current_dt.strftime("%Y-%m-%d"),
            "Year": y,
            "Quarter": q,
            "QuarterName": f"Q{q} {y}",
            "Month": m,
            "MonthName": current_dt.strftime("%B"),
            "MonthYear": current_dt.strftime("%b %Y"),
            "WeekOfYear": current_dt.isocalendar()[1],
            "DayOfWeek": dow,
            "DayName": current_dt.strftime("%A"),
            "IsWeekday": is_wkday,
            "IsWorkingDay": is_working,
            "HolidayName": holidays_set.get(current_dt, None),
        })
        current_dt += timedelta(days=1)

    df_date = pd.DataFrame(date_rows)

    # Filter working dates for primary workplace utilization
    working_dates = df_date[df_date["IsWorkingDay"]].copy()

    # Pre-build lookup dictionaries for fast lookup
    prop_config_lookup = {p["PropertyCode"]: p for p in PROPERTIES_CONFIG}
    prop_row_lookup = df_property.set_index("PropertyKey").to_dict(orient="index")
    geo_lookup = {g["GeographyKey"]: g for g in GEOGRAPHIES}

    # Pre-filter spaces
    workstation_spaces = df_space[
        df_space["SpaceType"].isin(["Open Workstation", "Private Office"])
    ].to_dict(orient="records")

    meeting_room_spaces = df_space[
        df_space["SpaceType"].isin(["Small Meeting Room", "Large Meeting Room"])
    ].to_dict(orient="records")

    # 2. fact_daily_workplace_utilization
    # Day of week factors (Tue-Thu peaks, Fri lowest)
    dow_multipliers = {
        1: 0.88,  # Monday
        2: 1.18,  # Tuesday
        3: 1.25,  # Wednesday
        4: 1.19,  # Thursday
        5: 0.62,  # Friday
    }

    utilization_rows = []
    global_util_key = 1000001

    # Pre-generate day noises
    dates_list = working_dates.to_dict(orient="records")

    print(f"Generating utilization facts across {len(dates_list)} working days and {len(workstation_spaces)} spaces...")

    for d in dates_list:
        d_key = d["DateKey"]
        dow = d["DayOfWeek"]
        month = d["Month"]
        base_dow_mult = dow_multipliers.get(dow, 0.9)

        # Seasonal multiplier (Summer / Year-end dips)
        if month in [5, 6]:
            season_mult = 0.95
        elif month in [10, 11]:  # Festival / peak enterprise quarter
            season_mult = 1.04
        elif month == 12:  # Holiday season
            season_mult = 0.88
        else:
            season_mult = 1.00

        for sp in workstation_spaces:
            sp_key = sp["SpaceKey"]
            fl_key = sp["FloorKey"]
            p_key = sp["PropertyKey"]
            cap = sp["Capacity"]

            prop_meta = prop_row_lookup[p_key]
            prop_cfg = prop_config_lookup[prop_meta["PropertyCode"]]

            base_util = prop_cfg["BaseUtilization"]
            peak_mult = prop_cfg["PeakMultiplier"]

            # Space noise using Beta distribution around mean
            # Target mean = base_util * base_dow_mult * season_mult
            target_util = base_util * base_dow_mult * season_mult
            # Add subtle random variation per space
            space_noise = np.random.normal(0.0, 0.04)
            sim_util = float(np.clip(target_util + space_noise, 0.05, 0.98))

            assigned_cap = int(round(cap * 1.24))  # 1.24 sharing ratio on average
            avg_occupancy = round(cap * sim_util, 2)
            actual_occupants = int(min(cap, round(avg_occupancy * np.random.uniform(1.05, 1.15))))

            # Peak occupancy during highest hour of the day
            sim_peak_util = float(np.clip(sim_util * peak_mult + np.random.normal(0.0, 0.03), 0.10, 0.99))
            peak_occupants = int(min(cap, max(actual_occupants, round(cap * sim_peak_util))))

            available_hours = round(cap * 10.0, 2)
            occupied_hours = round(avg_occupancy * 10.0, 2)
            calc_util_rate = round(occupied_hours / available_hours, 4)
            calc_peak_rate = round(peak_occupants / cap, 4) if cap > 0 else 0.0

            source = "IoT Desk Sensor" if p_key % 3 == 0 else ("Wi-Fi AP Telemetry" if p_key % 2 == 0 else "Integrated Access Gateway")

            utilization_rows.append({
                "UtilizationFactKey": global_util_key,
                "DateKey": d_key,
                "PropertyKey": p_key,
                "FloorKey": fl_key,
                "SpaceKey": sp_key,
                "Capacity": cap,
                "AssignedCapacity": assigned_cap,
                "ActualOccupants": actual_occupants,
                "AverageOccupancy": avg_occupancy,
                "PeakOccupants": peak_occupants,
                "AvailableHours": available_hours,
                "OccupiedHours": occupied_hours,
                "UtilizationRate": calc_util_rate,
                "PeakUtilizationRate": calc_peak_rate,
                "ObservationSource": source,
            })
            global_util_key += 1

    df_utilization = pd.DataFrame(utilization_rows)
    print(f"Generated {len(df_utilization):,} workplace utilization rows.")

    # 3. fact_room_utilization
    # Sample meetings across working days for meeting rooms
    print(f"Generating room utilization facts for {len(meeting_room_spaces)} rooms...")
    room_rows = []
    global_room_key = 70001

    for d in dates_list:
        d_key = d["DateKey"]
        dow = d["DayOfWeek"]
        dow_mult = dow_multipliers.get(dow, 0.9)

        for rm in meeting_room_spaces:
            sp_key = rm["SpaceKey"]
            p_key = rm["PropertyKey"]
            rm_type = rm["SpaceType"]
            rm_cap = rm["Capacity"]

            # Small meeting rooms are more heavily booked than large boardrooms
            if rm_type == "Small Meeting Room":
                base_bookings = int(np.random.poisson(5 * dow_mult))
                base_bookings = max(1, min(9, base_bookings))
                # Attendee count matches capacity well
                avg_attendees = round(float(np.random.uniform(2.8, min(rm_cap, 5.2))), 1)
            else:  # Large Meeting Room (Boardroom 12 seats)
                base_bookings = int(np.random.poisson(3 * dow_mult))
                base_bookings = max(0, min(6, base_bookings))
                # Capacity mismatch: large room used by small groups!
                avg_attendees = round(float(np.random.uniform(3.2, 5.8)), 1)

            # Ghost booking / no-show rate ~18-30%
            no_show_prob = np.random.uniform(0.15, 0.32)
            no_show_count = int(round(base_bookings * no_show_prob))
            attended_count = max(0, base_bookings - no_show_count)

            booked_hrs = round(base_bookings * np.random.uniform(0.85, 1.25), 2)
            booked_hrs = min(10.0, booked_hrs)
            occupied_hrs = round(attended_count * np.random.uniform(0.80, 1.15), 2)
            occupied_hrs = min(booked_hrs, occupied_hrs)

            peak_attendees = int(min(rm_cap, round(avg_attendees * np.random.uniform(1.2, 1.5)))) if attended_count > 0 else 0
            rm_util_rate = round(occupied_hrs / 10.0, 4)

            room_rows.append({
                "RoomFactKey": global_room_key,
                "DateKey": d_key,
                "PropertyKey": p_key,
                "SpaceKey": sp_key,
                "RoomType": rm_type,
                "RoomCapacity": rm_cap,
                "BookingCount": base_bookings,
                "AttendedBookingCount": attended_count,
                "BookedHours": booked_hrs,
                "OccupiedHours": occupied_hrs,
                "AverageAttendees": avg_attendees if attended_count > 0 else 0.0,
                "PeakAttendees": peak_attendees,
                "NoShowCount": no_show_count,
                "RoomUtilizationRate": rm_util_rate,
            })
            global_room_key += 1

    df_room_utilization = pd.DataFrame(room_rows)
    print(f"Generated {len(df_room_utilization):,} room utilization rows.")

    # 4. fact_monthly_property_cost & 5. fact_headcount
    # Generate for every month in the 24-month horizon
    print("Generating monthly property cost and headcount facts...")
    cost_rows = []
    headcount_rows = []
    global_cost_key = 3001
    global_hc_key = 4001

    months_dt = pd.date_range(start="2024-10-01", end="2026-09-01", freq="MS")

    for m_dt in months_dt:
        m_date_key = int(m_dt.strftime("%Y%m%d"))
        m_num = m_dt.month
        m_year = m_dt.year

        for p in PROPERTIES_CONFIG:
            p_code = p["PropertyCode"]
            prop_meta = df_property[df_property["PropertyCode"] == p_code].iloc[0]
            p_key = int(prop_meta["PropertyKey"])
            geo = geo_lookup[prop_meta["GeographyKey"]]
            curr = geo["LocalCurrency"]
            fx_rate = geo["FixedFXToINR"]
            usable_sqm = float(prop_meta["UsableAreaSqM"])
            cap_seats = int(prop_meta["CapacitySeats"])
            assigned_hc = int(prop_meta["AssignedHeadcount"])

            # Base monthly rent (0 if owned)
            annual_base_rent_local = p["BaseRentAnnualLocal"]
            monthly_rent_local = round(annual_base_rent_local / 12.0, 2)

            # Service charges / CAM
            cam_rate = p["CAMLocalRatePerSqM"]
            monthly_cam_local = round(usable_sqm * cam_rate * np.random.uniform(0.98, 1.02), 2)

            # Energy / HVAC (higher in summer: Apr-Jun for India/SE Asia)
            if curr == "IDR":
                base_energy_rate = 65000.0  # IDR/sqm
            elif curr == "THB":
                base_energy_rate = 140.0
            elif curr == "MYR":
                base_energy_rate = 15.0
            elif curr == "SGD":
                base_energy_rate = 22.0
            elif curr == "AUD":
                base_energy_rate = 25.0
            else:  # INR
                base_energy_rate = 180.0

            summer_factor = 1.25 if m_num in [4, 5, 6, 7] else (0.85 if m_num in [11, 12, 1] else 1.0)
            monthly_energy_local = round(usable_sqm * base_energy_rate * summer_factor * np.random.uniform(0.96, 1.04), 2)

            # Facilities & staffing
            monthly_fac_local = round(monthly_cam_local * 0.70 * np.random.uniform(0.97, 1.03), 2)

            # Maintenance & repairs (occasional spikes)
            maint_spike = 1.6 if (m_num == 3 or m_num == 9) and (p_key % 4 == 0) else 1.0
            monthly_maint_local = round(monthly_cam_local * 0.40 * maint_spike * np.random.uniform(0.95, 1.05), 2)

            # Other operating costs
            monthly_other_local = round(monthly_cam_local * 0.25 * np.random.uniform(0.95, 1.05), 2)

            total_cost_local = round(
                monthly_rent_local + monthly_cam_local + monthly_energy_local +
                monthly_fac_local + monthly_maint_local + monthly_other_local,
                2
            )
            total_cost_inr = round(total_cost_local * fx_rate, 2)

            cost_rows.append({
                "CostFactKey": global_cost_key,
                "MonthDateKey": m_date_key,
                "PropertyKey": p_key,
                "OriginalCurrency": curr,
                "RentCost": monthly_rent_local,
                "ServiceCharge": monthly_cam_local,
                "EnergyCost": monthly_energy_local,
                "FacilitiesCost": monthly_fac_local,
                "MaintenanceCost": monthly_maint_local,
                "OtherOperatingCost": monthly_other_local,
                "TotalOperatingCostLocal": total_cost_local,
                "FXRateToINR": fx_rate,
                "TotalOperatingCostINR": total_cost_inr,
            })
            global_cost_key += 1

            # Headcount fact
            # Slight growth trend over 24 months for some properties
            growth_idx = (m_year - 2024) * 12 + (m_num - 10)
            growth_mult = 1.0 + (0.003 * growth_idx if p_key % 3 == 0 else -0.001 * growth_idx)
            m_assigned_hc = int(round(assigned_hc * growth_mult))

            # Average daily presence derived from property base utilization
            base_util = p["BaseUtilization"]
            avg_presence = round(cap_seats * base_util * np.random.uniform(0.96, 1.04), 1)
            peak_presence = int(min(cap_seats, round(avg_presence * p["PeakMultiplier"] * np.random.uniform(0.98, 1.03))))

            headcount_rows.append({
                "HeadcountFactKey": global_hc_key,
                "MonthDateKey": m_date_key,
                "PropertyKey": p_key,
                "AssignedHeadcount": m_assigned_hc,
                "AverageDailyPresence": avg_presence,
                "PeakDailyPresence": peak_presence,
            })
            global_hc_key += 1

    df_cost = pd.DataFrame(cost_rows)
    df_headcount = pd.DataFrame(headcount_rows)

    return df_date, df_utilization, df_room_utilization, df_cost, df_headcount
