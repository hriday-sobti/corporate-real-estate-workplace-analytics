-- ====================================================================
-- Corporate Real Estate Portfolio & Workplace Analytics
-- Analytical Views Library (Reusable for SQL Queries, BI & Reporting)
-- ====================================================================

-- 1. Property Master View
CREATE OR REPLACE VIEW vw_property_master AS
SELECT
    p.PropertyKey,
    p.PropertyCode,
    p.PropertyName,
    g.Region,
    g.Country,
    g.CountryCode,
    g.City,
    g.MarketClassification,
    g.LocalCurrency,
    g.FixedFXToINR,
    ft.FacilityTypeCode,
    ft.FacilityTypeName,
    ft.TargetDensitySqM,
    p.OwnershipType,
    p.PropertyStatus,
    p.OpeningYear,
    p.RentableAreaSqM,
    p.UsableAreaSqM,
    p.CapacitySeats,
    p.AssignedHeadcount,
    ROUND(p.UsableAreaSqM / p.CapacitySeats, 2) AS DensitySqMPerSeat,
    ROUND(CAST(p.AssignedHeadcount AS NUMERIC) / p.CapacitySeats, 2) AS DeskSharingRatio,
    p.FloorCount,
    p.MeetingRoomCount,
    p.BaseRentAnnualINR
FROM dim_property p
JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
JOIN dim_facility_type ft ON p.FacilityTypeKey = ft.FacilityTypeKey;

-- 2. Daily Property Utilization View
CREATE OR REPLACE VIEW vw_daily_property_utilization AS
SELECT
    u.DateKey,
    d.FullDate,
    d.DayOfWeek,
    d.DayName,
    d.MonthYear,
    u.PropertyKey,
    p.PropertyCode,
    p.PropertyName,
    SUM(u.Capacity) AS TotalCapacity,
    SUM(u.ActualOccupants) AS TotalActualOccupants,
    ROUND(SUM(u.AverageOccupancy), 2) AS TotalAverageOccupancy,
    MAX(u.PeakOccupants) AS PropertyPeakOccupants,
    ROUND((SUM(u.OccupiedHours) / NULLIF(SUM(u.AvailableHours), 0)) * 100, 2) AS DailyUtilizationRatePct,
    ROUND(AVG(u.PeakUtilizationRate) * 100, 2) AS DailyPeakUtilizationRatePct,
    CASE WHEN MAX(u.PeakUtilizationRate) >= 0.85 THEN 1 ELSE 0 END AS HasCapacityPressureFlag
FROM fact_daily_workplace_utilization u
JOIN dim_date d ON u.DateKey = d.DateKey
JOIN dim_property p ON u.PropertyKey = p.PropertyKey
GROUP BY u.DateKey, d.FullDate, d.DayOfWeek, d.DayName, d.MonthYear, u.PropertyKey, p.PropertyCode, p.PropertyName;

-- 3. Monthly Cost Efficiency View
CREATE OR REPLACE VIEW vw_monthly_cost_efficiency AS
SELECT
    c.CostFactKey,
    c.MonthDateKey,
    d.MonthYear,
    d.Year,
    d.Month,
    c.PropertyKey,
    p.PropertyCode,
    p.PropertyName,
    g.Country,
    g.City,
    c.OriginalCurrency,
    c.TotalOperatingCostLocal,
    c.FXRateToINR,
    c.TotalOperatingCostINR,
    p.UsableAreaSqM,
    p.CapacitySeats,
    h.AverageDailyPresence,
    ROUND(c.TotalOperatingCostINR / p.UsableAreaSqM, 2) AS MonthlyCostPerUsableSqM_INR,
    ROUND(c.TotalOperatingCostINR / p.CapacitySeats, 2) AS MonthlyCostPerSeat_INR,
    ROUND(c.TotalOperatingCostINR / NULLIF(h.AverageDailyPresence, 0), 2) AS MonthlyCostPerOccupiedSeat_INR
FROM fact_monthly_property_cost c
JOIN dim_date d ON c.MonthDateKey = d.DateKey
JOIN dim_property p ON c.PropertyKey = p.PropertyKey
JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
JOIN fact_headcount h ON c.PropertyKey = h.PropertyKey AND c.MonthDateKey = h.MonthDateKey;

-- 4. Meeting Room Performance View
CREATE OR REPLACE VIEW vw_meeting_room_performance AS
SELECT
    r.PropertyKey,
    p.PropertyCode,
    p.PropertyName,
    r.RoomType,
    COUNT(DISTINCT r.SpaceKey) AS TotalRooms,
    ROUND(AVG(r.RoomCapacity), 1) AS AvgRoomCapacity,
    SUM(r.BookingCount) AS TotalBookings,
    SUM(r.AttendedBookingCount) AS TotalAttendedBookings,
    SUM(r.NoShowCount) AS TotalNoShows,
    ROUND((SUM(r.NoShowCount) * 100.0) / NULLIF(SUM(r.BookingCount), 0), 2) AS NoShowRatePct,
    ROUND(SUM(r.OccupiedHours), 2) AS TotalOccupiedHours,
    ROUND(AVG(r.RoomUtilizationRate) * 100, 2) AS AvgRoomUtilizationPct,
    ROUND(AVG(r.AverageAttendees), 1) AS AvgAttendeesPerMeeting,
    ROUND(AVG(r.RoomCapacity) - AVG(r.AverageAttendees), 1) AS AvgSurplusChairsPerMeeting
FROM fact_room_utilization r
JOIN dim_property p ON r.PropertyKey = p.PropertyKey
GROUP BY r.PropertyKey, p.PropertyCode, p.PropertyName, r.RoomType;

-- 5. Workplace Pressure Quadrants View
CREATE OR REPLACE VIEW vw_workplace_pressure_quadrants AS
WITH OverallStats AS (
    SELECT
        u.PropertyKey,
        ROUND((SUM(u.OccupiedHours) / NULLIF(SUM(u.AvailableHours), 0)) * 100, 2) AS AverageUtilizationPct,
        ROUND(AVG(u.PeakUtilizationRate) * 100, 2) AS PeakUtilizationPct,
        ROUND((COUNT(CASE WHEN u.PeakUtilizationRate >= 0.85 THEN 1 END) * 100.0) / COUNT(*), 2) AS CapacityPressurePct
    FROM fact_daily_workplace_utilization u
    GROUP BY u.PropertyKey
)
SELECT
    p.PropertyKey,
    p.PropertyCode,
    p.PropertyName,
    g.Region,
    g.Country,
    g.City,
    ft.FacilityTypeName,
    p.CapacitySeats,
    p.UsableAreaSqM,
    os.AverageUtilizationPct,
    os.PeakUtilizationPct,
    os.CapacityPressurePct,
    CASE
        WHEN os.AverageUtilizationPct < 55.0 AND os.PeakUtilizationPct < 80.0 THEN 'Underutilized'
        WHEN os.AverageUtilizationPct < 55.0 AND os.PeakUtilizationPct >= 80.0 THEN 'Peak-sensitive'
        WHEN os.AverageUtilizationPct >= 55.0 AND os.PeakUtilizationPct < 80.0 THEN 'Consistently active'
        ELSE 'Capacity-constrained'
    END AS PressureQuadrant
FROM OverallStats os
JOIN dim_property p ON os.PropertyKey = p.PropertyKey
JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
JOIN dim_facility_type ft ON p.FacilityTypeKey = ft.FacilityTypeKey;

-- 6. Lease Critical Horizons View
CREATE OR REPLACE VIEW vw_lease_critical_horizons AS
SELECT
    l.LeaseKey,
    p.PropertyCode,
    p.PropertyName,
    g.Country,
    g.City,
    p.OwnershipType,
    l.LeaseContractNumber,
    l.LeaseStartDate,
    l.LeaseEndDate,
    l.LeaseType,
    l.RenewalOption,
    l.NoticePeriodMonths,
    l.AnnualRentINR,
    l.LeaseStatus,
    l.ExpiryHorizonCategory,
    CASE l.ExpiryHorizonCategory
        WHEN 'Expiring <= 6M' THEN 1
        WHEN 'Expiring 6-12M' THEN 2
        WHEN 'Expiring 12-24M' THEN 3
        WHEN 'Horizon > 24M' THEN 4
        ELSE 5
    END AS HorizonSortOrder
FROM dim_lease l
JOIN dim_property p ON l.PropertyKey = p.PropertyKey
JOIN dim_geography g ON p.GeographyKey = g.GeographyKey;

-- 7. Data Quality Audit View
CREATE OR REPLACE VIEW vw_data_quality_summary AS
SELECT
    RuleID,
    Severity,
    TableName,
    COUNT(*) AS TotalViolations,
    ExpectedRule,
    RemediationStatus
FROM fact_data_quality
GROUP BY RuleID, Severity, TableName, ExpectedRule, RemediationStatus;
