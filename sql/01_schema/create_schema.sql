-- ====================================================================
-- Corporate Real Estate Portfolio & Workplace Analytics
-- Schema: Analytical Star Schema DDL (PostgreSQL & ANSI SQL Compatible)
-- ====================================================================

-- Drop existing tables if re-running
DROP TABLE IF EXISTS fact_room_utilization CASCADE;
DROP TABLE IF EXISTS fact_daily_workplace_utilization CASCADE;
DROP TABLE IF EXISTS fact_monthly_property_cost CASCADE;
DROP TABLE IF EXISTS fact_headcount CASCADE;
DROP TABLE IF EXISTS fact_data_quality CASCADE;
DROP TABLE IF EXISTS dim_space CASCADE;
DROP TABLE IF EXISTS dim_floor CASCADE;
DROP TABLE IF EXISTS dim_lease CASCADE;
DROP TABLE IF EXISTS dim_property CASCADE;
DROP TABLE IF EXISTS dim_facility_type CASCADE;
DROP TABLE IF EXISTS dim_geography CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

-- --------------------------------------------------------------------
-- 1. DIMENSION TABLES
-- --------------------------------------------------------------------

CREATE TABLE dim_date (
    DateKey         INTEGER PRIMARY KEY,
    FullDate        DATE NOT NULL UNIQUE,
    Year            INTEGER NOT NULL,
    Quarter         INTEGER NOT NULL CHECK (Quarter BETWEEN 1 AND 4),
    QuarterName     VARCHAR(10) NOT NULL,
    Month           INTEGER NOT NULL CHECK (Month BETWEEN 1 AND 12),
    MonthName       VARCHAR(20) NOT NULL,
    MonthYear       VARCHAR(10) NOT NULL,
    WeekOfYear      INTEGER NOT NULL CHECK (WeekOfYear BETWEEN 1 AND 53),
    DayOfWeek       INTEGER NOT NULL CHECK (DayOfWeek BETWEEN 1 AND 7),
    DayName         VARCHAR(15) NOT NULL,
    IsWeekday       BOOLEAN NOT NULL,
    IsWorkingDay    BOOLEAN NOT NULL,
    HolidayName     VARCHAR(50)
);

CREATE TABLE dim_geography (
    GeographyKey            INTEGER PRIMARY KEY,
    Region                  VARCHAR(20) NOT NULL,
    Country                 VARCHAR(50) NOT NULL,
    CountryCode             VARCHAR(3) NOT NULL,
    City                    VARCHAR(50) NOT NULL,
    MarketClassification    VARCHAR(30) NOT NULL,
    LocalCurrency           VARCHAR(3) NOT NULL,
    FixedFXToINR            NUMERIC(10,4) NOT NULL CHECK (FixedFXToINR > 0)
);

CREATE TABLE dim_facility_type (
    FacilityTypeKey     INTEGER PRIMARY KEY,
    FacilityTypeCode    VARCHAR(10) NOT NULL UNIQUE,
    FacilityTypeName    VARCHAR(50) NOT NULL,
    PrimaryPurpose      VARCHAR(100) NOT NULL,
    TargetDensitySqM    NUMERIC(4,1) NOT NULL CHECK (TargetDensitySqM > 0)
);

CREATE TABLE dim_property (
    PropertyKey         INTEGER PRIMARY KEY,
    PropertyCode        VARCHAR(20) NOT NULL UNIQUE,
    PropertyName        VARCHAR(100) NOT NULL,
    GeographyKey        INTEGER NOT NULL REFERENCES dim_geography(GeographyKey),
    FacilityTypeKey     INTEGER NOT NULL REFERENCES dim_facility_type(FacilityTypeKey),
    OwnershipType       VARCHAR(20) NOT NULL CHECK (OwnershipType IN ('Leased', 'Owned')),
    PropertyStatus      VARCHAR(20) NOT NULL,
    OpeningYear         INTEGER NOT NULL CHECK (OpeningYear >= 1990),
    RentableAreaSqM     NUMERIC(10,2) NOT NULL CHECK (RentableAreaSqM > 0),
    UsableAreaSqM       NUMERIC(10,2) NOT NULL CHECK (UsableAreaSqM > 0),
    CapacitySeats       INTEGER NOT NULL CHECK (CapacitySeats > 0),
    AssignedHeadcount   INTEGER NOT NULL CHECK (AssignedHeadcount >= 0),
    FloorCount          INTEGER NOT NULL CHECK (FloorCount > 0),
    MeetingRoomCount    INTEGER NOT NULL CHECK (MeetingRoomCount >= 0),
    BaseRentAnnualINR   NUMERIC(14,2) NOT NULL CHECK (BaseRentAnnualINR >= 0),
    CONSTRAINT chk_usable_le_rentable CHECK (UsableAreaSqM <= RentableAreaSqM)
);

CREATE TABLE dim_lease (
    LeaseKey                INTEGER PRIMARY KEY,
    PropertyKey             INTEGER NOT NULL REFERENCES dim_property(PropertyKey),
    LeaseContractNumber     VARCHAR(30) NOT NULL,
    LeaseStartDate          VARCHAR(20) NOT NULL,
    LeaseEndDate            VARCHAR(20) NOT NULL,
    LeaseType               VARCHAR(30) NOT NULL,
    RenewalOption           VARCHAR(50),
    NoticePeriodMonths      INTEGER NOT NULL CHECK (NoticePeriodMonths >= 0),
    AnnualRentINR           NUMERIC(14,2) NOT NULL CHECK (AnnualRentINR >= 0),
    LeaseStatus             VARCHAR(30) NOT NULL,
    ExpiryHorizonCategory   VARCHAR(30) NOT NULL
);

CREATE TABLE dim_floor (
    FloorKey        INTEGER PRIMARY KEY,
    PropertyKey     INTEGER NOT NULL REFERENCES dim_property(PropertyKey),
    FloorNumber     INTEGER NOT NULL,
    FloorCode       VARCHAR(20) NOT NULL,
    FloorName       VARCHAR(50) NOT NULL,
    UsableAreaSqM   NUMERIC(8,2) NOT NULL CHECK (UsableAreaSqM > 0),
    CapacitySeats   INTEGER NOT NULL CHECK (CapacitySeats >= 0)
);

CREATE TABLE dim_space (
    SpaceKey        INTEGER PRIMARY KEY,
    FloorKey        INTEGER NOT NULL REFERENCES dim_floor(FloorKey),
    PropertyKey     INTEGER NOT NULL REFERENCES dim_property(PropertyKey),
    SpaceCode       VARCHAR(30) NOT NULL UNIQUE,
    SpaceName       VARCHAR(100) NOT NULL,
    SpaceType       VARCHAR(50) NOT NULL,
    AreaSqM         NUMERIC(8,2) NOT NULL CHECK (AreaSqM > 0),
    Capacity        INTEGER NOT NULL CHECK (Capacity >= 0),
    IsBookable      BOOLEAN NOT NULL
);

-- --------------------------------------------------------------------
-- 2. FACT TABLES
-- --------------------------------------------------------------------

CREATE TABLE fact_daily_workplace_utilization (
    UtilizationFactKey      BIGINT PRIMARY KEY,
    DateKey                 INTEGER NOT NULL REFERENCES dim_date(DateKey),
    PropertyKey             INTEGER NOT NULL REFERENCES dim_property(PropertyKey),
    FloorKey                INTEGER NOT NULL REFERENCES dim_floor(FloorKey),
    SpaceKey                INTEGER NOT NULL REFERENCES dim_space(SpaceKey),
    Capacity                INTEGER NOT NULL CHECK (Capacity >= 0),
    AssignedCapacity        INTEGER NOT NULL CHECK (AssignedCapacity >= 0),
    ActualOccupants         INTEGER NOT NULL CHECK (ActualOccupants >= 0),
    AverageOccupancy        NUMERIC(6,2) NOT NULL CHECK (AverageOccupancy >= 0),
    PeakOccupants           INTEGER NOT NULL CHECK (PeakOccupants >= 0),
    AvailableHours          NUMERIC(8,2) NOT NULL CHECK (AvailableHours >= 0),
    OccupiedHours           NUMERIC(8,2) NOT NULL CHECK (OccupiedHours >= 0),
    UtilizationRate         NUMERIC(6,4) NOT NULL CHECK (UtilizationRate BETWEEN 0.0 AND 1.0),
    PeakUtilizationRate     NUMERIC(6,4) NOT NULL CHECK (PeakUtilizationRate BETWEEN 0.0 AND 1.0),
    ObservationSource       VARCHAR(30) NOT NULL,
    CONSTRAINT chk_util_occupants_cap CHECK (ActualOccupants <= Capacity),
    CONSTRAINT chk_util_peak_cap CHECK (PeakOccupants <= Capacity)
);

CREATE TABLE fact_room_utilization (
    RoomFactKey             BIGINT PRIMARY KEY,
    DateKey                 INTEGER NOT NULL REFERENCES dim_date(DateKey),
    PropertyKey             INTEGER NOT NULL REFERENCES dim_property(PropertyKey),
    SpaceKey                INTEGER NOT NULL REFERENCES dim_space(SpaceKey),
    RoomType                VARCHAR(30) NOT NULL,
    RoomCapacity            INTEGER NOT NULL CHECK (RoomCapacity > 0),
    BookingCount            INTEGER NOT NULL CHECK (BookingCount >= 0),
    AttendedBookingCount    INTEGER NOT NULL CHECK (AttendedBookingCount >= 0),
    BookedHours             NUMERIC(5,2) NOT NULL CHECK (BookedHours >= 0),
    OccupiedHours           NUMERIC(5,2) NOT NULL CHECK (OccupiedHours >= 0),
    AverageAttendees        NUMERIC(5,2) NOT NULL CHECK (AverageAttendees >= 0),
    PeakAttendees           INTEGER NOT NULL CHECK (PeakAttendees >= 0),
    NoShowCount             INTEGER NOT NULL CHECK (NoShowCount >= 0),
    RoomUtilizationRate     NUMERIC(6,4) NOT NULL CHECK (RoomUtilizationRate BETWEEN 0.0 AND 1.0),
    CONSTRAINT chk_room_attended_le_booked CHECK (AttendedBookingCount <= BookingCount),
    CONSTRAINT chk_room_occupied_le_booked CHECK (OccupiedHours <= BookedHours)
);

CREATE TABLE fact_monthly_property_cost (
    CostFactKey             INTEGER PRIMARY KEY,
    MonthDateKey            INTEGER NOT NULL REFERENCES dim_date(DateKey),
    PropertyKey             INTEGER NOT NULL REFERENCES dim_property(PropertyKey),
    OriginalCurrency        VARCHAR(3) NOT NULL,
    RentCost                NUMERIC(14,2) NOT NULL CHECK (RentCost >= 0),
    ServiceCharge           NUMERIC(14,2) NOT NULL CHECK (ServiceCharge >= 0),
    EnergyCost              NUMERIC(14,2) NOT NULL CHECK (EnergyCost >= 0),
    FacilitiesCost          NUMERIC(14,2) NOT NULL CHECK (FacilitiesCost >= 0),
    MaintenanceCost         NUMERIC(14,2) NOT NULL CHECK (MaintenanceCost >= 0),
    OtherOperatingCost      NUMERIC(14,2) NOT NULL CHECK (OtherOperatingCost >= 0),
    TotalOperatingCostLocal NUMERIC(14,2) NOT NULL CHECK (TotalOperatingCostLocal >= 0),
    FXRateToINR             NUMERIC(10,4) NOT NULL CHECK (FXRateToINR > 0),
    TotalOperatingCostINR   NUMERIC(14,2) NOT NULL CHECK (TotalOperatingCostINR >= 0)
);

CREATE TABLE fact_headcount (
    HeadcountFactKey        INTEGER PRIMARY KEY,
    MonthDateKey            INTEGER NOT NULL REFERENCES dim_date(DateKey),
    PropertyKey             INTEGER NOT NULL REFERENCES dim_property(PropertyKey),
    AssignedHeadcount       INTEGER NOT NULL CHECK (AssignedHeadcount >= 0),
    AverageDailyPresence    NUMERIC(8,2) NOT NULL CHECK (AverageDailyPresence >= 0),
    PeakDailyPresence       INTEGER NOT NULL CHECK (PeakDailyPresence >= 0)
);

CREATE TABLE fact_data_quality (
    DQFactKey               INTEGER PRIMARY KEY,
    IssueID                 VARCHAR(20) NOT NULL UNIQUE,
    RuleID                  VARCHAR(10) NOT NULL,
    TableName               VARCHAR(50) NOT NULL,
    RecordIdentifier        VARCHAR(50) NOT NULL,
    Severity                VARCHAR(20) NOT NULL,
    ExpectedRule            VARCHAR(150) NOT NULL,
    InjectedValue           VARCHAR(100) NOT NULL,
    CorrectedValue          VARCHAR(100) NOT NULL,
    RemediationStatus       VARCHAR(50) NOT NULL,
    DetectionDate           DATE NOT NULL
);

-- --------------------------------------------------------------------
-- 3. INDEXES FOR HIGH-PERFORMANCE ANALYTICS
-- --------------------------------------------------------------------

CREATE INDEX idx_util_prop_date ON fact_daily_workplace_utilization(PropertyKey, DateKey);
CREATE INDEX idx_util_space_date ON fact_daily_workplace_utilization(SpaceKey, DateKey);
CREATE INDEX idx_room_prop_date ON fact_room_utilization(PropertyKey, DateKey);
CREATE INDEX idx_cost_prop_month ON fact_monthly_property_cost(PropertyKey, MonthDateKey);
CREATE INDEX idx_headcount_prop_month ON fact_headcount(PropertyKey, MonthDateKey);
CREATE INDEX idx_prop_geo ON dim_property(GeographyKey);
CREATE INDEX idx_prop_facility ON dim_property(FacilityTypeKey);
