"""Workplace Utilization Invariants and Dynamic Presence Tests.

Tests:
- Mathematical identities: AvailableHours == Capacity * 10, OccupiedHours == AverageOccupancy * 10
- Physical bounds: ActualOccupants <= Capacity, PeakOccupants <= Capacity
- Weekday distribution curve: Mid-week peaks (Tue-Thu) exceed Monday and Friday
- Room booking dynamics: Attended <= Bookings, NoShow == Bookings - Attended
"""

import os
import pytest
import pandas as pd
import numpy as np

ANALYTICAL_DIR = os.path.join("data", "analytical")


@pytest.fixture(scope="module")
def util_tables():
    return {
        "util": pd.read_csv(os.path.join(ANALYTICAL_DIR, "fact_daily_workplace_utilization.csv")),
        "room": pd.read_csv(os.path.join(ANALYTICAL_DIR, "fact_room_utilization.csv")),
        "date": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_date.csv")),
        "prop": pd.read_csv(os.path.join(ANALYTICAL_DIR, "dim_property.csv")),
    }


def test_utilization_row_count(util_tables):
    assert len(util_tables["util"]) == 168672, "Expected 168,672 daily workplace utilization facts"


def test_available_hours_calculation(util_tables):
    util = util_tables["util"]
    expected_avail = np.round(util["Capacity"] * 10.0, 2)
    assert np.allclose(util["AvailableHours"], expected_avail, atol=0.01)


def test_occupied_hours_calculation(util_tables):
    util = util_tables["util"]
    expected_occ = np.round(util["AverageOccupancy"] * 10.0, 2)
    assert np.allclose(util["OccupiedHours"], expected_occ, atol=0.01)


def test_utilization_rate_definition(util_tables):
    util = util_tables["util"]
    calc_rate = np.round(util["OccupiedHours"] / util["AvailableHours"], 4)
    assert np.allclose(util["UtilizationRate"], calc_rate, atol=0.001)


def test_peak_utilization_bounds(util_tables):
    util = util_tables["util"]
    assert (util["PeakUtilizationRate"] >= util["UtilizationRate"] - 0.05).all()
    assert (util["PeakUtilizationRate"] <= 1.0).all()


# Parameterized test over weekdays (Monday to Friday)
WEEKDAYS = [
    (1, "Monday", 45.0, 60.0),
    (2, "Tuesday", 65.0, 78.0),
    (3, "Wednesday", 68.0, 80.0),
    (4, "Thursday", 65.0, 78.0),
    (5, "Friday", 30.0, 45.0),
]


@pytest.mark.parametrize("dow,day_name,min_avg,max_avg", WEEKDAYS)
def test_weekday_utilization_distribution(util_tables, dow, day_name, min_avg, max_avg):
    util = util_tables["util"]
    date_df = util_tables["date"]
    merged = pd.merge(util, date_df[["DateKey", "DayOfWeek", "IsWorkingDay"]], on="DateKey")
    day_records = merged[(merged["DayOfWeek"] == dow) & (merged["IsWorkingDay"])]
    day_avg_pct = (day_records["OccupiedHours"].sum() / day_records["AvailableHours"].sum()) * 100
    assert day_avg_pct >= min_avg, f"{day_name} avg utilization ({day_avg_pct:.1f}%) below expected minimum {min_avg}%"
    assert day_avg_pct <= max_avg, f"{day_name} avg utilization ({day_avg_pct:.1f}%) exceeds expected maximum {max_avg}%"


def test_wednesday_exceeds_friday_by_substantial_margin(util_tables):
    util = util_tables["util"]
    date_df = util_tables["date"]
    merged = pd.merge(util, date_df[["DateKey", "DayOfWeek", "IsWorkingDay"]], on="DateKey")
    wed_avg = merged[merged["DayOfWeek"] == 3]["UtilizationRate"].mean()
    fri_avg = merged[merged["DayOfWeek"] == 5]["UtilizationRate"].mean()
    assert wed_avg >= fri_avg * 1.5, f"Wednesday ({wed_avg:.2f}) must exceed Friday ({fri_avg:.2f}) by >= 1.5x"


# Parameterized test over all 25 properties for positive presence
@pytest.mark.parametrize("prop_key", list(range(1, 26)))
def test_each_property_has_consistent_presence(util_tables, prop_key):
    util = util_tables["util"]
    p_util = util[util["PropertyKey"] == prop_key]
    assert len(p_util) > 0, f"Property {prop_key} has no utilization records"
    assert p_util["AverageOccupancy"].mean() > 0, f"Property {prop_key} has zero average presence"
    assert p_util["UtilizationRate"].mean() >= 0.30, f"Property {prop_key} has unrealistically low utilization"
    assert p_util["UtilizationRate"].mean() <= 0.85, f"Property {prop_key} has unrealistically high utilization"


def test_room_utilization_invariants(util_tables):
    room = util_tables["room"]
    assert len(room) == 112448, "Expected 112,448 room utilization records"
    assert (room["AttendedBookingCount"] <= room["BookingCount"]).all()
    assert (room["OccupiedHours"] <= room["BookedHours"]).all()
    expected_noshow = room["BookingCount"] - room["AttendedBookingCount"]
    assert (room["NoShowCount"] == expected_noshow).all()
    assert (room["RoomUtilizationRate"] >= 0.0).all() and (room["RoomUtilizationRate"] <= 1.0).all()


def test_room_attendee_surplus_in_large_rooms(util_tables):
    room = util_tables["room"]
    large_rooms = room[room["RoomType"] == "Large Meeting Room"]
    assert large_rooms["AverageAttendees"].mean() < 7.0, "Large 12-person rooms should exhibit small group mismatch"
