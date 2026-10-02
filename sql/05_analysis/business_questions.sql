-- ====================================================================
-- Corporate Real Estate Portfolio & Workplace Analytics
-- Analytical Query Library: 16 Core Strategic Business Questions
-- ====================================================================

-- --------------------------------------------------------------------
-- QUESTION 1: How large is the overall portfolio?
-- --------------------------------------------------------------------
SELECT
    COUNT(DISTINCT p.PropertyKey) AS TotalProperties,
    COUNT(DISTINCT g.Country) AS CountriesRepresented,
    COUNT(DISTINCT g.City) AS CitiesRepresented,
    SUM(p.RentableAreaSqM) AS TotalRentableAreaSqM,
    SUM(p.UsableAreaSqM) AS TotalUsableAreaSqM,
    ROUND(SUM(p.RentableAreaSqM - p.UsableAreaSqM), 2) AS TotalCoreLossAreaSqM,
    ROUND(((SUM(p.RentableAreaSqM) - SUM(p.UsableAreaSqM)) / SUM(p.RentableAreaSqM)) * 100, 2) AS PortfolioLossFactorPct,
    SUM(p.CapacitySeats) AS TotalSeatCapacity,
    SUM(p.AssignedHeadcount) AS TotalAssignedHeadcount,
    ROUND(CAST(SUM(p.AssignedHeadcount) AS NUMERIC) / SUM(p.CapacitySeats), 2) AS PortfolioDeskSharingRatio
FROM dim_property p
JOIN dim_geography g ON p.GeographyKey = g.GeographyKey;

-- --------------------------------------------------------------------
-- QUESTION 2: How is usable area distributed across countries and cities?
-- --------------------------------------------------------------------
WITH GeoSummary AS (
    SELECT
        g.Region,
        g.Country,
        g.City,
        COUNT(p.PropertyKey) AS PropertyCount,
        SUM(p.UsableAreaSqM) AS TotalUsableAreaSqM,
        SUM(p.CapacitySeats) AS TotalSeats
    FROM dim_property p
    JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
    GROUP BY g.Region, g.Country, g.City
),
TotalArea AS (
    SELECT SUM(UsableAreaSqM) AS PortfolioArea FROM dim_property
)
SELECT
    gs.Region,
    gs.Country,
    gs.City,
    gs.PropertyCount,
    gs.TotalUsableAreaSqM,
    ROUND((gs.TotalUsableAreaSqM / ta.PortfolioArea) * 100, 2) AS AreaSharePct,
    gs.TotalSeats,
    ROUND(gs.TotalUsableAreaSqM / gs.TotalSeats, 2) AS DensitySqMPerSeat,
    RANK() OVER (ORDER BY gs.TotalUsableAreaSqM DESC) AS AreaRank
FROM GeoSummary gs
CROSS JOIN TotalArea ta
ORDER BY AreaRank;

-- --------------------------------------------------------------------
-- QUESTION 3: Which locations have the highest seat capacity?
-- --------------------------------------------------------------------
SELECT
    p.PropertyCode,
    p.PropertyName,
    g.City,
    g.Country,
    ft.FacilityTypeName,
    p.CapacitySeats,
    p.UsableAreaSqM,
    p.AssignedHeadcount,
    ROUND(CAST(p.AssignedHeadcount AS NUMERIC) / p.CapacitySeats, 2) AS SharingRatio,
    RANK() OVER (ORDER BY p.CapacitySeats DESC) AS CapacityRank,
    ROUND((p.CapacitySeats * 100.0) / SUM(p.CapacitySeats) OVER (), 2) AS CapacitySharePct
FROM dim_property p
JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
JOIN dim_facility_type ft ON p.FacilityTypeKey = ft.FacilityTypeKey
ORDER BY CapacityRank;

-- --------------------------------------------------------------------
-- QUESTION 4: Which locations have the lowest average utilization?
-- --------------------------------------------------------------------
WITH PropertyUtil AS (
    SELECT
        u.PropertyKey,
        ROUND((SUM(u.OccupiedHours) / NULLIF(SUM(u.AvailableHours), 0)) * 100, 2) AS AverageUtilizationPct,
        ROUND(AVG(u.PeakUtilizationRate) * 100, 2) AS AvgPeakUtilizationPct,
        ROUND(MAX(u.PeakUtilizationRate) * 100, 2) AS MaxPeakUtilizationPct
    FROM fact_daily_workplace_utilization u
    GROUP BY u.PropertyKey
)
SELECT
    p.PropertyCode,
    p.PropertyName,
    g.City,
    g.Country,
    ft.FacilityTypeName,
    p.CapacitySeats,
    pu.AverageUtilizationPct,
    pu.AvgPeakUtilizationPct,
    pu.MaxPeakUtilizationPct,
    RANK() OVER (ORDER BY pu.AverageUtilizationPct ASC) AS UtilizationAscendingRank
FROM PropertyUtil pu
JOIN dim_property p ON pu.PropertyKey = p.PropertyKey
JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
JOIN dim_facility_type ft ON p.FacilityTypeKey = ft.FacilityTypeKey
ORDER BY UtilizationAscendingRank;

-- --------------------------------------------------------------------
-- QUESTION 5: Which locations experience the highest peak utilization?
-- --------------------------------------------------------------------
WITH PropertyPeak AS (
    SELECT
        u.PropertyKey,
        ROUND(AVG(u.PeakUtilizationRate) * 100, 2) AS AvgDailyPeakPct,
        ROUND(MAX(u.PeakUtilizationRate) * 100, 2) AS MaxObservedPeakPct,
        ROUND((SUM(u.OccupiedHours) / NULLIF(SUM(u.AvailableHours), 0)) * 100, 2) AS AverageUtilizationPct
    FROM fact_daily_workplace_utilization u
    GROUP BY u.PropertyKey
)
SELECT
    p.PropertyCode,
    p.PropertyName,
    g.City,
    g.Country,
    ft.FacilityTypeName,
    p.CapacitySeats,
    pp.AvgDailyPeakPct,
    pp.MaxObservedPeakPct,
    pp.AverageUtilizationPct,
    ROUND(pp.AvgDailyPeakPct - pp.AverageUtilizationPct, 2) AS PeakSpreadPct,
    DENSE_RANK() OVER (ORDER BY pp.AvgDailyPeakPct DESC) AS PeakRank
FROM PropertyPeak pp
JOIN dim_property p ON pp.PropertyKey = p.PropertyKey
JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
JOIN dim_facility_type ft ON p.FacilityTypeKey = ft.FacilityTypeKey
ORDER BY PeakRank;

-- --------------------------------------------------------------------
-- QUESTION 6: Where is there potential capacity pressure (days >= 85%)?
-- --------------------------------------------------------------------
SELECT
    p.PropertyCode,
    p.PropertyName,
    g.City,
    g.Country,
    COUNT(*) AS TotalWorkingDaysObserved,
    COUNT(CASE WHEN u.PeakUtilizationRate >= 0.85 THEN 1 END) AS DaysAtOrAbove85Pct,
    ROUND((COUNT(CASE WHEN u.PeakUtilizationRate >= 0.85 THEN 1 END) * 100.0) / COUNT(*), 2) AS CapacityPressurePct,
    ROUND(AVG(u.PeakUtilizationRate) * 100, 2) AS AveragePeakRatePct,
    CASE
        WHEN (COUNT(CASE WHEN u.PeakUtilizationRate >= 0.85 THEN 1 END) * 100.0) / COUNT(*) >= 25.0 THEN 'Acute Capacity Strain'
        WHEN (COUNT(CASE WHEN u.PeakUtilizationRate >= 0.85 THEN 1 END) * 100.0) / COUNT(*) >= 10.0 THEN 'Moderate Peak Sensitivity'
        ELSE 'Manageable Buffer'
    END AS PressureCategory
FROM fact_daily_workplace_utilization u
JOIN dim_property p ON u.PropertyKey = p.PropertyKey
JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
GROUP BY p.PropertyCode, p.PropertyName, g.City, g.Country
ORDER BY CapacityPressurePct DESC;

-- --------------------------------------------------------------------
-- QUESTION 7: Which properties combine relatively high cost with relatively low utilization?
-- --------------------------------------------------------------------
WITH UtilStats AS (
    SELECT
        PropertyKey,
        ROUND((SUM(OccupiedHours) / NULLIF(SUM(AvailableHours), 0)) * 100, 2) AS AverageUtilizationPct
    FROM fact_daily_workplace_utilization
    GROUP BY PropertyKey
),
CostStats AS (
    SELECT
        c.PropertyKey,
        ROUND(SUM(c.TotalOperatingCostINR) / 2.0, 2) AS AnnualCostINR,
        AVG(h.AverageDailyPresence) AS AvgPresence
    FROM fact_monthly_property_cost c
    JOIN fact_headcount h ON c.PropertyKey = h.PropertyKey AND c.MonthDateKey = h.MonthDateKey
    GROUP BY c.PropertyKey
)
SELECT
    p.PropertyCode,
    p.PropertyName,
    g.City,
    g.Country,
    p.UsableAreaSqM,
    u.AverageUtilizationPct,
    ROUND(cs.AnnualCostINR / NULLIF(cs.AvgPresence, 0), 2) AS CostPerOccupiedSeatINR,
    ROUND(cs.AnnualCostINR / p.UsableAreaSqM, 2) AS CostPerUsableSqM_INR,
    CASE
        WHEN u.AverageUtilizationPct < 55.0 AND (cs.AnnualCostINR / NULLIF(cs.AvgPresence, 0)) >= 300000 THEN 'Primary Focus: High Cost & Low Utilization'
        WHEN u.AverageUtilizationPct < 55.0 THEN 'Secondary Focus: Low Utilization / Modest Cost'
        WHEN (cs.AnnualCostINR / NULLIF(cs.AvgPresence, 0)) >= 300000 THEN 'Cost Scrutiny: High Cost but High Utilization'
        ELSE 'Standard Operations'
    END AS ManagementFocusCategory
FROM dim_property p
JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
JOIN UtilStats u ON p.PropertyKey = u.PropertyKey
JOIN CostStats cs ON p.PropertyKey = cs.PropertyKey
ORDER BY CostPerOccupiedSeatINR DESC;

-- --------------------------------------------------------------------
-- QUESTION 8: Which locations have high utilization but relatively constrained capacity?
-- --------------------------------------------------------------------
WITH PropUtilDaily AS (
    SELECT
        u.PropertyKey,
        ROUND((SUM(u.OccupiedHours) / NULLIF(SUM(u.AvailableHours), 0)) * 100, 2) AS AverageUtilizationPct,
        ROUND(AVG(u.PeakUtilizationRate) * 100, 2) AS AvgPeakUtilizationPct,
        COUNT(CASE WHEN u.PeakUtilizationRate >= 0.85 THEN 1 END) AS PressureDaysCount,
        COUNT(*) AS TotalDays
    FROM fact_daily_workplace_utilization u
    GROUP BY u.PropertyKey
)
SELECT
    p.PropertyCode,
    p.PropertyName,
    g.City,
    ft.FacilityTypeName,
    p.CapacitySeats,
    p.AssignedHeadcount,
    ROUND(CAST(p.AssignedHeadcount AS NUMERIC) / p.CapacitySeats, 2) AS SharingRatio,
    pud.AverageUtilizationPct,
    pud.AvgPeakUtilizationPct,
    ROUND((pud.PressureDaysCount * 100.0) / pud.TotalDays, 2) AS PressureDaysPct
FROM PropUtilDaily pud
JOIN dim_property p ON pud.PropertyKey = p.PropertyKey
JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
JOIN dim_facility_type ft ON p.FacilityTypeKey = ft.FacilityTypeKey
WHERE pud.AverageUtilizationPct >= 65.0 OR (pud.PressureDaysCount * 100.0) / pud.TotalDays >= 20.0
ORDER BY PressureDaysPct DESC;

-- --------------------------------------------------------------------
-- QUESTION 9: How do utilization patterns differ by weekday?
-- --------------------------------------------------------------------
SELECT
    d.DayOfWeek,
    d.DayName,
    COUNT(DISTINCT u.DateKey) AS WorkingDaysSampled,
    ROUND((SUM(u.OccupiedHours) / NULLIF(SUM(u.AvailableHours), 0)) * 100, 2) AS AverageUtilizationPct,
    ROUND(AVG(u.PeakUtilizationRate) * 100, 2) AS AveragePeakUtilizationPct,
    ROUND(MAX(u.PeakUtilizationRate) * 100, 2) AS MaxPeakUtilizationPct,
    ROUND(AVG(u.ActualOccupants), 1) AS AvgActualOccupantsPerSpace
FROM fact_daily_workplace_utilization u
JOIN dim_date d ON u.DateKey = d.DateKey
WHERE d.IsWorkingDay = TRUE
GROUP BY d.DayOfWeek, d.DayName
ORDER BY d.DayOfWeek;

-- --------------------------------------------------------------------
-- QUESTION 10: How do different facility types behave?
-- --------------------------------------------------------------------
WITH FacilityCost AS (
    SELECT
        p.FacilityTypeKey,
        ROUND(SUM(c.TotalOperatingCostINR) / 2.0, 2) AS AnnualCostINR
    FROM fact_monthly_property_cost c
    JOIN dim_property p ON c.PropertyKey = p.PropertyKey
    GROUP BY p.FacilityTypeKey
),
FacilityUtil AS (
    SELECT
        p.FacilityTypeKey,
        ROUND((SUM(u.OccupiedHours) / NULLIF(SUM(u.AvailableHours), 0)) * 100, 2) AS AverageUtilizationPct,
        ROUND(AVG(u.PeakUtilizationRate) * 100, 2) AS AvgPeakRatePct,
        ROUND((COUNT(CASE WHEN u.PeakUtilizationRate >= 0.85 THEN 1 END) * 100.0) / COUNT(*), 2) AS PressurePct
    FROM fact_daily_workplace_utilization u
    JOIN dim_property p ON u.PropertyKey = p.PropertyKey
    GROUP BY p.FacilityTypeKey
)
SELECT
    ft.FacilityTypeCode,
    ft.FacilityTypeName,
    COUNT(DISTINCT p.PropertyKey) AS PropertyCount,
    SUM(p.UsableAreaSqM) AS TotalUsableAreaSqM,
    SUM(p.CapacitySeats) AS TotalSeats,
    ROUND(SUM(p.UsableAreaSqM) / SUM(p.CapacitySeats), 2) AS ActualDensitySqM,
    ft.TargetDensitySqM,
    fu.AverageUtilizationPct,
    fu.AvgPeakRatePct,
    fu.PressurePct,
    ROUND(fc.AnnualCostINR / SUM(p.CapacitySeats), 2) AS CostPerSeatINR
FROM dim_facility_type ft
JOIN dim_property p ON ft.FacilityTypeKey = p.FacilityTypeKey
JOIN FacilityCost fc ON ft.FacilityTypeKey = fc.FacilityTypeKey
JOIN FacilityUtil fu ON ft.FacilityTypeKey = fu.FacilityTypeKey
GROUP BY ft.FacilityTypeCode, ft.FacilityTypeName, ft.TargetDensitySqM, fu.AverageUtilizationPct, fu.AvgPeakRatePct, fu.PressurePct, fc.AnnualCostINR
ORDER BY TotalSeats DESC;

-- --------------------------------------------------------------------
-- QUESTION 11: Which meeting-room categories appear mismatched to demand?
-- --------------------------------------------------------------------
SELECT
    RoomType,
    COUNT(DISTINCT SpaceKey) AS TotalRoomsProvisioned,
    ROUND(AVG(RoomCapacity), 1) AS RatedCapacity,
    ROUND(AVG(BookingCount), 1) AS AvgBookingsPerDay,
    ROUND(AVG(AttendedBookingCount), 1) AS AvgAttendedPerDay,
    ROUND(AVG(AverageAttendees), 1) AS AvgPhysicalAttendees,
    ROUND(AVG(RoomCapacity) - AVG(AverageAttendees), 1) AS SeatSurplusPerMeeting,
    ROUND((SUM(NoShowCount) * 100.0) / NULLIF(SUM(BookingCount), 0), 2) AS NoShowRatePct,
    ROUND(AVG(RoomUtilizationRate) * 100, 2) AS AverageUtilizationPct
FROM fact_room_utilization
GROUP BY RoomType;

-- --------------------------------------------------------------------
-- QUESTION 12: Which lease events are approaching (Decision Horizon)?
-- --------------------------------------------------------------------
SELECT
    l.ExpiryHorizonCategory,
    COUNT(*) AS ContractCount,
    SUM(p.UsableAreaSqM) AS TotalUsableAreaSqM,
    SUM(p.CapacitySeats) AS TotalSeatsInScope,
    ROUND(SUM(l.AnnualRentINR), 2) AS TotalAnnualBaseRentINR,
    ROUND((SUM(l.AnnualRentINR) * 100.0) / SUM(SUM(l.AnnualRentINR)) OVER (), 2) AS RentExposurePct
FROM dim_lease l
JOIN dim_property p ON l.PropertyKey = p.PropertyKey
GROUP BY l.ExpiryHorizonCategory
ORDER BY
    CASE l.ExpiryHorizonCategory
        WHEN 'Expiring <= 6M' THEN 1
        WHEN 'Expiring 6-12M' THEN 2
        WHEN 'Expiring 12-24M' THEN 3
        WHEN 'Horizon > 24M' THEN 4
        ELSE 5
    END;

-- --------------------------------------------------------------------
-- QUESTION 13: Which properties require data-quality attention?
-- --------------------------------------------------------------------
SELECT
    p.PropertyCode,
    p.PropertyName,
    g.City,
    g.Country,
    COUNT(q.DQFactKey) AS LoggedExceptionCount,
    COUNT(CASE WHEN q.Severity = 'Critical' THEN 1 END) AS CriticalCount,
    COUNT(CASE WHEN q.Severity = 'High' THEN 1 END) AS HighCount,
    COUNT(CASE WHEN q.Severity = 'Medium' THEN 1 END) AS MediumCount,
    STRING_AGG(DISTINCT q.RuleID, ', ') AS ViolatedRules
FROM fact_data_quality q
JOIN dim_property p ON q.RecordIdentifier LIKE '%' || p.PropertyCode || '%'
JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
GROUP BY p.PropertyCode, p.PropertyName, g.City, g.Country
ORDER BY LoggedExceptionCount DESC;

-- --------------------------------------------------------------------
-- QUESTION 14: Which portfolio areas contribute most to total operating cost?
-- --------------------------------------------------------------------
WITH PropertyAnnualCost AS (
    SELECT
        p.PropertyKey,
        p.PropertyCode,
        p.PropertyName,
        g.City,
        g.Country,
        ROUND(SUM(c.TotalOperatingCostINR) / 2.0, 2) AS AnnualCostINR
    FROM fact_monthly_property_cost c
    JOIN dim_property p ON c.PropertyKey = p.PropertyKey
    JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
    GROUP BY p.PropertyKey, p.PropertyCode, p.PropertyName, g.City, g.Country
),
TotalCost AS (
    SELECT SUM(AnnualCostINR) AS TotalPortfolioCostINR FROM PropertyAnnualCost
)
SELECT
    pac.PropertyCode,
    pac.PropertyName,
    pac.City,
    pac.Country,
    pac.AnnualCostINR,
    ROUND((pac.AnnualCostINR / tc.TotalPortfolioCostINR) * 100, 2) AS CostSharePct,
    ROUND(SUM(pac.AnnualCostINR) OVER (ORDER BY pac.AnnualCostINR DESC) * 100.0 / tc.TotalPortfolioCostINR, 2) AS CumulativeCostSharePct,
    RANK() OVER (ORDER BY pac.AnnualCostINR DESC) AS CostRank
FROM PropertyAnnualCost pac
CROSS JOIN TotalCost tc
ORDER BY CostRank;

-- --------------------------------------------------------------------
-- QUESTION 15: How does cost per occupied seat differ from cost per available seat?
-- --------------------------------------------------------------------
WITH CostSeatComp AS (
    SELECT
        p.PropertyCode,
        p.PropertyName,
        g.City,
        p.CapacitySeats,
        ROUND(AVG(h.AverageDailyPresence), 1) AS AvgDailyPresence,
        ROUND(SUM(c.TotalOperatingCostINR) / 2.0, 2) AS AnnualCostINR
    FROM fact_monthly_property_cost c
    JOIN dim_property p ON c.PropertyKey = p.PropertyKey
    JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
    JOIN fact_headcount h ON c.PropertyKey = h.PropertyKey AND c.MonthDateKey = h.MonthDateKey
    GROUP BY p.PropertyCode, p.PropertyName, g.City, p.CapacitySeats
)
SELECT
    PropertyCode,
    PropertyName,
    City,
    CapacitySeats,
    AvgDailyPresence,
    ROUND(CapacitySeats - AvgDailyPresence, 0) AS VacantSeatsCount,
    ROUND(AnnualCostINR / CapacitySeats, 2) AS CostPerAvailableSeatINR,
    ROUND(AnnualCostINR / NULLIF(AvgDailyPresence, 0), 2) AS CostPerOccupiedSeatINR,
    ROUND((AnnualCostINR / NULLIF(AvgDailyPresence, 0)) - (AnnualCostINR / CapacitySeats), 2) AS UtilizationCostPremiumINR,
    ROUND((((AnnualCostINR / NULLIF(AvgDailyPresence, 0)) - (AnnualCostINR / CapacitySeats)) / (AnnualCostINR / CapacitySeats)) * 100, 2) AS InefficiencyMultiplierPct
FROM CostSeatComp
ORDER BY CostPerOccupiedSeatINR DESC;

-- --------------------------------------------------------------------
-- QUESTION 16: Stability of findings over 24-month horizon (rolling 3-month trend)
-- --------------------------------------------------------------------
WITH MonthlyUtil AS (
    SELECT
        u.PropertyKey,
        (d.Year * 100 + d.Month) AS YearMonthKey,
        d.MonthYear,
        ROUND((SUM(u.OccupiedHours) / NULLIF(SUM(u.AvailableHours), 0)) * 100, 2) AS MonthlyAvgUtilPct
    FROM fact_daily_workplace_utilization u
    JOIN dim_date d ON u.DateKey = d.DateKey
    GROUP BY u.PropertyKey, (d.Year * 100 + d.Month), d.MonthYear
)
SELECT
    p.PropertyCode,
    p.PropertyName,
    mu.MonthYear,
    mu.MonthlyAvgUtilPct,
    ROUND(AVG(mu.MonthlyAvgUtilPct) OVER (
        PARTITION BY mu.PropertyKey
        ORDER BY mu.YearMonthKey
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS Rolling3MonthAvgUtilPct,
    ROUND(mu.MonthlyAvgUtilPct - LAG(mu.MonthlyAvgUtilPct, 1) OVER (
        PARTITION BY mu.PropertyKey
        ORDER BY mu.YearMonthKey
    ), 2) AS MoM_ChangePct
FROM MonthlyUtil mu
JOIN dim_property p ON mu.PropertyKey = p.PropertyKey
ORDER BY p.PropertyCode, mu.YearMonthKey;
