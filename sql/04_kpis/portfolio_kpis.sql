-- ====================================================================
-- Corporate Real Estate Portfolio & Workplace Analytics
-- KPI Library: Core Portfolio Executive & Operational KPIs
-- ====================================================================

WITH PortfolioScale AS (
    SELECT
        COUNT(DISTINCT PropertyKey) AS TotalProperties,
        SUM(UsableAreaSqM) AS TotalUsableAreaSqM,
        SUM(RentableAreaSqM) AS TotalRentableAreaSqM,
        SUM(CapacitySeats) AS TotalSeatCapacity,
        SUM(AssignedHeadcount) AS TotalAssignedHeadcount,
        ROUND(AVG(UsableAreaSqM / NULLIF(CapacitySeats, 0)), 2) AS AvgDensitySqMPerSeat,
        ROUND(CAST(SUM(AssignedHeadcount) AS NUMERIC) / NULLIF(SUM(CapacitySeats), 0), 2) AS SharingRatio
    FROM dim_property
),
UtilizationMetrics AS (
    SELECT
        ROUND((SUM(OccupiedHours) / NULLIF(SUM(AvailableHours), 0)) * 100, 2) AS AverageUtilizationPct,
        ROUND(AVG(PeakUtilizationRate) * 100, 2) AS PortfolioAveragePeakPct,
        ROUND(MAX(PeakUtilizationRate) * 100, 2) AS AbsolutePeakUtilizationPct,
        ROUND((COUNT(CASE WHEN PeakUtilizationRate >= 0.85 THEN 1 END) * 100.0) / COUNT(*), 2) AS CapacityPressurePct
    FROM fact_daily_workplace_utilization
),
HeadcountPresence AS (
    SELECT
        ROUND(AVG(AverageDailyPresence), 1) AS AverageDailyPresence,
        ROUND(AVG(PeakDailyPresence), 1) AS PeakDailyPresence
    FROM fact_headcount
),
FinancialEfficiency AS (
    -- 24 months of observations -> annual cost is SUM / 2.0
    SELECT
        ROUND(SUM(TotalOperatingCostINR) / 2.0, 2) AS AnnualOperatingCostINR,
        ROUND((SUM(TotalOperatingCostINR) / 2.0) / (SELECT SUM(UsableAreaSqM) FROM dim_property), 2) AS CostPerUsableSqM_INR,
        ROUND((SUM(TotalOperatingCostINR) / 2.0) / (SELECT SUM(CapacitySeats) FROM dim_property), 2) AS CostPerSeat_INR,
        ROUND((SUM(TotalOperatingCostINR) / 2.0) / (SELECT SUM(AverageDailyPresence) FROM (
            SELECT PropertyKey, AVG(AverageDailyPresence) AS AverageDailyPresence FROM fact_headcount GROUP BY PropertyKey
        )), 2) AS CostPerOccupiedSeat_INR
    FROM fact_monthly_property_cost
),
LeaseMilestones AS (
    SELECT
        COUNT(CASE WHEN ExpiryHorizonCategory = 'Expiring <= 6M' THEN 1 END) AS LeasesExpiringIn6Months,
        COUNT(CASE WHEN ExpiryHorizonCategory IN ('Expiring <= 6M', 'Expiring 6-12M') THEN 1 END) AS LeasesExpiringIn12Months,
        COUNT(CASE WHEN ExpiryHorizonCategory IN ('Expiring <= 6M', 'Expiring 6-12M', 'Expiring 12-24M') THEN 1 END) AS LeasesExpiringIn24Months,
        COUNT(CASE WHEN ExpiryHorizonCategory = 'Owned' THEN 1 END) AS OwnedPropertiesCount
    FROM dim_lease
),
RoomMetrics AS (
    SELECT
        ROUND(AVG(RoomUtilizationRate) * 100, 2) AS AverageRoomUtilizationPct,
        ROUND((SUM(NoShowCount) * 100.0) / NULLIF(SUM(BookingCount), 0), 2) AS RoomNoShowRatePct,
        ROUND(AVG(AverageAttendees), 1) AS AvgAttendeesPerMeeting
    FROM fact_room_utilization
),
QualityMetrics AS (
    SELECT
        COUNT(*) AS DataQualityExceptionCount,
        ROUND(((282584 - COUNT(*)) * 100.0) / 282584, 2) AS DataQualityPassRatePct
    FROM fact_data_quality
)
SELECT
    -- Scale & Portfolio
    ps.TotalProperties,
    ps.TotalUsableAreaSqM,
    ps.TotalRentableAreaSqM,
    ps.TotalSeatCapacity,
    ps.TotalAssignedHeadcount,
    ps.AvgDensitySqMPerSeat,
    ps.SharingRatio,
    -- Utilization & Presence
    ROUND(hp.AverageDailyPresence * ps.TotalProperties, 0) AS TotalDailyPresenceRegional,
    ROUND(ps.TotalSeatCapacity - (hp.AverageDailyPresence * ps.TotalProperties), 0) AS TotalVacantSeatsRegional,
    um.AverageUtilizationPct,
    um.PortfolioAveragePeakPct,
    um.AbsolutePeakUtilizationPct,
    um.CapacityPressurePct,
    -- Financials (Annualized INR)
    fe.AnnualOperatingCostINR,
    fe.CostPerUsableSqM_INR,
    fe.CostPerSeat_INR,
    fe.CostPerOccupiedSeat_INR,
    -- Lease Commitments
    lm.LeasesExpiringIn6Months,
    lm.LeasesExpiringIn12Months,
    lm.LeasesExpiringIn24Months,
    lm.OwnedPropertiesCount,
    -- Room Metrics
    rm.AverageRoomUtilizationPct,
    rm.RoomNoShowRatePct,
    rm.AvgAttendeesPerMeeting,
    -- Quality
    qm.DataQualityExceptionCount,
    qm.DataQualityPassRatePct
FROM PortfolioScale ps
CROSS JOIN UtilizationMetrics um
CROSS JOIN HeadcountPresence hp
CROSS JOIN FinancialEfficiency fe
CROSS JOIN LeaseMilestones lm
CROSS JOIN RoomMetrics rm
CROSS JOIN QualityMetrics qm;
