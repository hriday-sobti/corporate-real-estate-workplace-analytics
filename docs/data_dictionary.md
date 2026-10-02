# Corporate Real Estate & Workplace Analytics: Data Dictionary

**Project:** Corporate Real Estate Portfolio & Workplace Analytics  
**Schema Architecture:** Relational Dimensional Star Schema  
**Target Environments:** PostgreSQL 16+ / SQLite 3.40+ / Power BI Semantic Model  

---

## 1. Dimensional Tables

### 1.1 `dim_date`
Provides a uniform temporal dimension for all daily and monthly aggregations.

| Column Name | Data Type | Constraint | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DateKey` | `INTEGER` | `PRIMARY KEY` | No | Surrogate key in YYYYMMDD format | `20251015` |
| `FullDate` | `DATE` | `UNIQUE` | No | Calendar date | `2025-10-15` |
| `Year` | `INTEGER` | | No | 4-digit calendar year | `2025` |
| `Quarter` | `INTEGER` | | No | Calendar quarter (1 to 4) | `4` |
| `QuarterName` | `VARCHAR(10)` | | No | Formatted quarter label | `Q4 2025` |
| `Month` | `INTEGER` | | No | Calendar month (1 to 12) | `10` |
| `MonthName` | `VARCHAR(20)` | | No | Full name of month | `October` |
| `MonthYear` | `VARCHAR(10)` | | No | Short month-year label | `Oct 2025` |
| `WeekOfYear` | `INTEGER` | | No | ISO calendar week number (1 to 53) | `42` |
| `DayOfWeek` | `INTEGER` | | No | Day of week index (1=Monday, 7=Sunday) | `3` |
| `DayName` | `VARCHAR(15)` | | No | Full day name | `Wednesday` |
| `IsWeekday` | `BOOLEAN` | | No | True if Monday through Friday | `TRUE` |
| `IsWorkingDay` | `BOOLEAN` | | No | True if non-holiday business day | `TRUE` |
| `HolidayName` | `VARCHAR(50)` | | Yes | Name of regional public holiday if applicable | `Diwali (Regional)` |

---

### 1.2 `dim_geography`
Standardizes the regional and market hierarchy across India and Asia-Pacific.

| Column Name | Data Type | Constraint | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GeographyKey` | `INTEGER` | `PRIMARY KEY` | No | Surrogate key for geographical entity | `101` |
| `Region` | `VARCHAR(20)` | | No | High-level macro region | `India` or `Asia-Pacific` |
| `Country` | `VARCHAR(50)` | | No | Sovereign state name | `India`, `Singapore`, `Australia` |
| `CountryCode` | `VARCHAR(3)` | | No | ISO 3-letter country code | `IND`, `SGP`, `AUS` |
| `City` | `VARCHAR(50)` | | No | Urban metro center | `Bengaluru`, `Sydney`, `Mumbai` |
| `MarketClassification`| `VARCHAR(30)` | | No | Market scale archetype | `Tier-1 Metro`, `Regional Hub` |
| `LocalCurrency` | `VARCHAR(3)` | | No | ISO local currency code | `INR`, `SGD`, `AUD`, `MYR` |
| `FixedFXToINR` | `NUMERIC(10,4)`| | No | Project reference exchange rate to INR | `63.5000` |

---

### 1.3 `dim_facility_type`
Categorizes the business purpose and operational function of real estate assets.

| Column Name | Data Type | Constraint | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `FacilityTypeKey` | `INTEGER` | `PRIMARY KEY` | No | Surrogate key for facility archetype | `1` |
| `FacilityTypeCode`| `VARCHAR(10)` | `UNIQUE` | No | Standard code | `TECH_HUB`, `REG_HQ` |
| `FacilityTypeName`| `VARCHAR(50)` | | No | Operational classification label | `Technology & Engineering Campus` |
| `PrimaryPurpose` | `VARCHAR(100)`| | No | Core operational activity hosted | `Software R&D and Technology Services` |
| `TargetDensitySqM`| `NUMERIC(4,1)`| | No | Standard design density target ($m^2$/desk)| `9.0` |

---

### 1.4 `dim_property`
The core property master record storing building attributes, locations, and capacities.

| Column Name | Data Type | Constraint | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PropertyKey` | `INTEGER` | `PRIMARY KEY` | No | Surrogate key for property | `1` |
| `PropertyCode` | `VARCHAR(20)` | `UNIQUE` | No | Business identifier (e.g. `PROP-BLR-01`) | `PROP-BLR-01` |
| `PropertyName` | `VARCHAR(100)`| | No | Human-readable building title | `Bengaluru Tech Park Tower A` |
| `GeographyKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_geography` | `101` |
| `FacilityTypeKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_facility_type` | `1` |
| `OwnershipType` | `VARCHAR(20)` | | No | Ownership status: `Leased` or `Owned` | `Leased` |
| `PropertyStatus` | `VARCHAR(20)` | | No | Operating status: `Operational` | `Operational` |
| `OpeningYear` | `INTEGER` | | No | Year property was commissioned | `2019` |
| `RentableAreaSqM` | `NUMERIC(10,2)`| | No | Total gross rentable floor area ($m^2$) | `14500.00` |
| `UsableAreaSqM` | `NUMERIC(10,2)`| | No | Net usable functional office area ($m^2$) | `12200.00` |
| `CapacitySeats` | `INTEGER` | | No | Total physical work points installed | `1250` |
| `AssignedHeadcount`| `INTEGER` | | No | Registered personnel assigned to asset | `1550` |
| `FloorCount` | `INTEGER` | | No | Number of active operational floors | `6` |
| `MeetingRoomCount`| `INTEGER` | | No | Total count of enclosed meeting spaces | `38` |
| `BaseRentAnnualINR`| `NUMERIC(14,2)`| | No | Contractual annual base rent in ₹ | `125000000.00` |

---

### 1.5 `dim_floor`
Stores floor-level physical zoning and capacity attributes.

| Column Name | Data Type | Constraint | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `FloorKey` | `INTEGER` | `PRIMARY KEY` | No | Surrogate key for floor entity | `1001` |
| `PropertyKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_property` | `1` |
| `FloorNumber` | `INTEGER` | | No | Numerical floor designation (e.g. 1 to 12) | `3` |
| `FloorCode` | `VARCHAR(20)` | | No | Unique floor code | `BLR-01-FL03` |
| `FloorName` | `VARCHAR(50)` | | No | Display name | `Floor 3 - Engineering Zone` |
| `UsableAreaSqM` | `NUMERIC(8,2)` | | No | Net usable area on this floor ($m^2$) | `2050.00` |
| `CapacitySeats` | `INTEGER` | | No | Workstations provisioned on this floor | `210` |

---

### 1.6 `dim_space`
Individual workplace zones, rooms, and specific spaces.

| Column Name | Data Type | Constraint | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SpaceKey` | `INTEGER` | `PRIMARY KEY` | No | Surrogate key for space | `5001` |
| `FloorKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_floor` | `1001` |
| `PropertyKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_property` | `1` |
| `SpaceCode` | `VARCHAR(30)` | `UNIQUE` | No | Unique space identifier | `BLR01-F3-SP012` |
| `SpaceName` | `VARCHAR(100)`| | No | Detailed space title | `Engineering Bay A - Open Desks` |
| `SpaceType` | `VARCHAR(50)` | | No | Architectural category | `Open Workstation`, `Meeting Room` |
| `AreaSqM` | `NUMERIC(8,2)` | | No | Measured space area ($m^2$) | `420.00` |
| `Capacity` | `INTEGER` | | No | Seating capacity of space | `45` |
| `IsBookable` | `BOOLEAN` | | No | True if reserveable in booking system | `FALSE` |

---

### 1.7 `dim_lease`
Commercial lease contractual details, milestones, and financial terms.

| Column Name | Data Type | Constraint | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LeaseKey` | `INTEGER` | `PRIMARY KEY` | No | Surrogate key for lease contract | `201` |
| `PropertyKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_property` | `1` |
| `LeaseContractNumber`| `VARCHAR(30)`| | No | Contract tracking code | `LSE-BLR-2021-08` |
| `LeaseStartDate` | `DATE` | | No | Commencement date of current term | `2021-08-01` |
| `LeaseEndDate` | `DATE` | | No | Expiration date of current term | `2027-07-31` |
| `LeaseType` | `VARCHAR(30)` | | No | Structure: `Triple Net (NNN)`, `Gross Lease`| `Triple Net (NNN)` |
| `RenewalOption` | `VARCHAR(50)` | | No | Contractual renewal term terms | `5-Year Extension at Market` |
| `NoticePeriodMonths`| `INTEGER` | | No | Advance written notice required (months) | `6` |
| `AnnualRentINR` | `NUMERIC(14,2)`| | No | Annual base lease commitment in ₹ | `125000000.00` |
| `LeaseStatus` | `VARCHAR(20)` | | No | Status relative to reporting date | `Active` |
| `ExpiryHorizonCategory`| `VARCHAR(30)`| | No | Analytical decision window bucket | `Expiring 6-12M` |

---

## 2. Fact Tables

### 2.1 `fact_daily_workplace_utilization`
Daily time-series records of workplace space utilization and presence.

| Column Name | Data Type | Constraint | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `UtilizationFactKey`| `BIGINT` | `PRIMARY KEY` | No | Unique surrogate key | `1000001` |
| `DateKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_date` | `20251015` |
| `PropertyKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_property` | `1` |
| `FloorKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_floor` | `1001` |
| `SpaceKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_space` | `5001` |
| `Capacity` | `INTEGER` | | No | Installed capacity seats | `45` |
| `AssignedCapacity`| `INTEGER` | | No | Administratively allocated seats | `54` |
| `ActualOccupants` | `INTEGER` | | No | Distinct daily attendees | `32` |
| `AverageOccupancy`| `NUMERIC(6,2)` | | No | Time-weighted occupant count | `28.50` |
| `PeakOccupants` | `INTEGER` | | No | Maximum concurrent occupants observed | `41` |
| `AvailableHours` | `NUMERIC(8,2)` | | No | Operating hours $\times$ Capacity | `450.00` |
| `OccupiedHours` | `NUMERIC(8,2)` | | No | Integrated seat-hours occupied | `285.00` |
| `UtilizationRate` | `NUMERIC(6,4)` | | No | Ratio of OccupiedHours / AvailableHours | `0.6333` |
| `PeakUtilizationRate`| `NUMERIC(6,4)`| | No | Ratio of PeakOccupants / Capacity | `0.9111` |
| `ObservationSource`| `VARCHAR(30)`| | No | Data origin: `IoT Sensor`, `Wi-Fi Access` | `IoT Sensor` |

---

### 2.2 `fact_monthly_property_cost`
Monthly financial expenditures incurred at the asset level.

| Column Name | Data Type | Constraint | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CostFactKey` | `INTEGER` | `PRIMARY KEY` | No | Unique surrogate key | `3001` |
| `MonthDateKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_date` (1st of month) | `20251001` |
| `PropertyKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_property` | `1` |
| `OriginalCurrency`| `VARCHAR(3)` | | No | Currency in which expense was billed | `INR` |
| `RentCost` | `NUMERIC(14,2)`| | No | Monthly base lease payment | `10416666.67` |
| `ServiceCharge` | `NUMERIC(14,2)`| | No | Common area maintenance (CAM) fee | `1850000.00` |
| `EnergyCost` | `NUMERIC(14,2)`| | No | Electricity, HVAC, utility costs | `1420000.00` |
| `FacilitiesCost` | `NUMERIC(14,2)`| | No | Janitorial, security, front-desk staffing | `1100000.00` |
| `MaintenanceCost`| `NUMERIC(14,2)`| | No | Mechanical, electrical, repairs | `650000.00` |
| `OtherOperatingCost`| `NUMERIC(14,2)`| | No | Insurance, local rates, waste | `380000.00` |
| `TotalOperatingCostLocal`| `NUMERIC(14,2)`| | No | Sum of monthly operating costs (Local) | `15816666.67` |
| `FXRateToINR` | `NUMERIC(10,4)`| | No | Applied currency conversion factor | `1.0000` |
| `TotalOperatingCostINR`| `NUMERIC(14,2)`| | No | Sum of monthly operating costs in ₹ | `15816666.67` |

---

### 2.3 `fact_room_utilization`
Daily room scheduling and physical attendance facts for enclosed meeting facilities.

| Column Name | Data Type | Constraint | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `RoomFactKey` | `BIGINT` | `PRIMARY KEY` | No | Unique surrogate key | `70001` |
| `DateKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_date` | `20251015` |
| `PropertyKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_property` | `1` |
| `SpaceKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_space` | `5020` |
| `RoomType` | `VARCHAR(30)` | | No | `Small Meeting Room`, `Boardroom` | `Large Meeting Room` |
| `RoomCapacity` | `INTEGER` | | No | Rated seating capacity of room | `12` |
| `BookingCount` | `INTEGER` | | No | Total scheduled reservations | `6` |
| `AttendedBookingCount`| `INTEGER`| | No | Reservations verified with attendees | `4` |
| `BookedHours` | `NUMERIC(5,2)` | | No | Total hours reserved on calendar | `5.50` |
| `OccupiedHours` | `NUMERIC(5,2)` | | No | Total hours physically occupied | `3.75` |
| `AverageAttendees`| `NUMERIC(5,2)` | | No | Average physical attendee count | `4.20` |
| `PeakAttendees` | `INTEGER` | | No | Maximum attendees observed in session | `7` |
| `NoShowCount` | `INTEGER` | | No | Number of unattended bookings | `2` |
| `RoomUtilizationRate`| `NUMERIC(6,4)`| | No | Ratio of OccupiedHours / 10 available hrs| `0.3750` |

---

### 2.4 `fact_headcount`
Monthly administrative and badge presence statistics per asset.

| Column Name | Data Type | Constraint | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `HeadcountFactKey`| `INTEGER` | `PRIMARY KEY` | No | Unique surrogate key | `4001` |
| `MonthDateKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_date` (1st of month) | `20251001` |
| `PropertyKey` | `INTEGER` | `FOREIGN KEY` | No | FK to `dim_property` | `1` |
| `AssignedHeadcount`| `INTEGER` | | No | Headcount administratively assigned | `1550` |
| `AverageDailyPresence`| `NUMERIC(8,2)`| | No | Mean daily physical badge entrances | `812.40` |
| `PeakDailyPresence`| `INTEGER` | | No | Maximum daily distinct attendees in month| `1095` |

---

### 2.5 `fact_data_quality`
Audited quality exception events captured from source data validation.

| Column Name | Data Type | Constraint | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DQFactKey` | `INTEGER` | `PRIMARY KEY` | No | Unique surrogate key | `901` |
| `IssueID` | `VARCHAR(20)` | `UNIQUE` | No | Quality manifest identifier (e.g. `ISS-042`)| `ISS-042` |
| `RuleID` | `VARCHAR(10)` | | No | Rule code (e.g. `DQ003`) | `DQ003` |
| `TableName` | `VARCHAR(50)` | | No | Source entity where defect was caught | `raw_utilization` |
| `RecordIdentifier`| `VARCHAR(50)` | | No | Business key of erroneous record | `UTIL-20251015-5001` |
| `Severity` | `VARCHAR(20)` | | No | Classification: `Critical`, `Warning` | `Critical` |
| `ExpectedRule` | `VARCHAR(150)`| | No | Plain-text validation requirement | `Utilization rate must be between 0 and 1`|
| `InjectedValue` | `VARCHAR(100)`| | No | Defective value present in RAW layer | `1.4500` |
| `CorrectedValue` | `VARCHAR(100)`| | No | Remedied value applied in CLEAN layer | `0.9200` |
| `RemediationStatus`| `VARCHAR(20)`| | No | Status: `Corrected` or `Excluded` | `Corrected` |
| `DetectionDate` | `DATE` | | No | Date rule validation was executed | `2026-09-30` |
