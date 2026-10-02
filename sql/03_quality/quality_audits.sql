-- ====================================================================
-- Corporate Real Estate Portfolio & Workplace Analytics
-- Data Quality Audits: SQL Verification of Rules DQ001 to DQ012
-- ====================================================================

-- 1. Check DQ001: Property uniqueness
SELECT
    PropertyCode,
    COUNT(*) AS DuplicateCount
FROM dim_property
GROUP BY PropertyCode
HAVING COUNT(*) > 1;

-- 2. Check DQ002: Actual occupants within capacity
SELECT
    COUNT(*) AS TotalViolations,
    MAX(ActualOccupants - Capacity) AS MaxCapacityBreach
FROM fact_daily_workplace_utilization
WHERE ActualOccupants > Capacity;

-- 3. Check DQ003: Daily utilization rate between 0.0 and 1.0 (0% - 100%)
SELECT
    COUNT(*) AS OutOfBoundsCount,
    MIN(UtilizationRate) AS MinRate,
    MAX(UtilizationRate) AS MaxRate
FROM fact_daily_workplace_utilization
WHERE UtilizationRate < 0.0 OR UtilizationRate > 1.0;

-- 4. Check DQ004: Lease chronology (Start Date <= End Date)
SELECT
    LeaseKey,
    PropertyKey,
    LeaseStartDate,
    LeaseEndDate
FROM dim_lease
WHERE LeaseType != 'Corporate Freehold'
  AND CAST(LeaseEndDate AS DATE) < CAST(LeaseStartDate AS DATE);

-- 5. Check DQ005: Geographic alignment and casing
SELECT
    p.PropertyCode,
    p.PropertyName,
    g.City,
    g.Country
FROM dim_property p
JOIN dim_geography g ON p.GeographyKey = g.GeographyKey
WHERE TRIM(g.City) != g.City OR TRIM(g.Country) != g.Country;

-- 6. Check DQ006: Usable area <= Rentable area
SELECT
    PropertyCode,
    PropertyName,
    RentableAreaSqM,
    UsableAreaSqM,
    (RentableAreaSqM - UsableAreaSqM) AS CoreLossAreaSqM
FROM dim_property
WHERE UsableAreaSqM > RentableAreaSqM;

-- 7. Check DQ007: Referential integrity (Fact to Dimension foreign keys)
SELECT 'fact_daily_workplace_utilization -> dim_property' AS CheckName, COUNT(*) AS OrphanCount
FROM fact_daily_workplace_utilization u
WHERE NOT EXISTS (SELECT 1 FROM dim_property p WHERE p.PropertyKey = u.PropertyKey)
UNION ALL
SELECT 'fact_monthly_property_cost -> dim_property', COUNT(*)
FROM fact_monthly_property_cost c
WHERE NOT EXISTS (SELECT 1 FROM dim_property p WHERE p.PropertyKey = c.PropertyKey)
UNION ALL
SELECT 'fact_room_utilization -> dim_space', COUNT(*)
FROM fact_room_utilization r
WHERE NOT EXISTS (SELECT 1 FROM dim_space s WHERE s.SpaceKey = r.SpaceKey);

-- 8. Check DQ008: Non-negative operating expenses
SELECT
    COUNT(*) AS NegativeCostRecordCount
FROM fact_monthly_property_cost
WHERE RentCost < 0
   OR ServiceCharge < 0
   OR EnergyCost < 0
   OR FacilitiesCost < 0
   OR MaintenanceCost < 0
   OR OtherOperatingCost < 0
   OR TotalOperatingCostINR < 0;

-- 9. Check DQ011: Room attended bookings <= scheduled bookings
SELECT
    COUNT(*) AS AttendedExceedsBookedCount
FROM fact_room_utilization
WHERE AttendedBookingCount > BookingCount;

-- 10. Summary Audit of Logged Injected Issues from fact_data_quality
SELECT
    RuleID,
    Severity,
    COUNT(*) AS ExceptionCount,
    COUNT(DISTINCT RecordIdentifier) AS DistinctRecordsAffected
FROM fact_data_quality
GROUP BY RuleID, Severity
ORDER BY Severity, ExceptionCount DESC;
