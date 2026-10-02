# Corporate Real Estate Data Quality Framework & Controls

**Project:** Corporate Real Estate Portfolio & Workplace Analytics  
**Framework Version:** 1.0  
**Audit Standard:** DAMA-DMBOK2 / ISO 8000 Data Quality Dimensions  
**Enforcement Engine:** Automated Python & SQL Validation Suite  

---

## 1. Principles of Data Quality Assurance

Corporate real estate management decisions—whether negotiating multi-year lease extensions, surrendering floors, or investing in tenant amenities—require absolute trust in baseline metrics. Siloed legacy systems (HR, CAFM, IoT sensors, ERP accounting) routinely generate conflicting or corrupt entries.

This framework enforces six core dimensions of quality across the ingestion lifecycle:
1. **Uniqueness:** No duplicated property keys, spatial zones, or observation timestamps.
2. **Completeness:** Mandatory fields (geography, capacity, area, lease milestones) must not contain unmapped null values.
3. **Validity:** Numeric observations, ratios, and area metrics must fall strictly within mathematically and physically feasible bounds.
4. **Consistency:** Geospatial and corporate organizational hierarchies must align (e.g., Mumbai strictly maps to India; Pune to India; Sydney to Australia).
5. **Referential Integrity:** Every foreign key in a fact table must resolve to a valid primary key in its parent dimension.
6. **Temporal Validity:** Lease and transaction chronological sequences must follow causality (e.g. `LeaseEndDate >= LeaseStartDate`).

---

## 2. Data Quality Rules Catalog

The following twelve data-quality rules are codified and evaluated automatically before data advances to the CLEAN or ANALYTICAL layers.

| Rule ID | Quality Dimension | Source Table | Target Column(s) | Severity | Expected Business Condition | Pass / Fail Evaluation Logic | Remediation Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DQ001** | Uniqueness | `raw_properties` | `PropertyCode` | Critical | Each property code must uniquely identify an asset. | `COUNT(PropertyCode) = COUNT(DISTINCT PropertyCode)` | Flag duplicate rows; retain the most recent authoritative master record. |
| **DQ002** | Validity | `raw_utilization` | `ActualOccupants`, `Capacity` | Critical | Physical occupants cannot exceed structural capacity after cleaning. | `ActualOccupants <= Capacity` | Cap `ActualOccupants` at structural `Capacity`; log anomaly in manifest. |
| **DQ003** | Validity | `raw_utilization` | `UtilizationRate` | Critical | Daily utilization rate must fall strictly between 0.0 and 1.0 (0%–100%). | `0.0 <= UtilizationRate <= 1.0` | Recompute `UtilizationRate = OccupiedHours / AvailableHours`; clamp at 1.0. |
| **DQ004** | Temporal Validity | `raw_leases` | `LeaseStartDate`, `LeaseEndDate` | Critical | Lease expiration date cannot precede lease commencement date. | `LeaseEndDate >= LeaseStartDate` | Reconstruct contractual term from lease metadata; swap inverted dates. |
| **DQ005** | Consistency | `raw_properties` | `City`, `Country` | High | City must map unambiguously to its valid sovereign country. | `City IN (ValidCitiesForCountry)` | Standardize city spelling and correct misassigned country references. |
| **DQ006** | Spatial Validity | `raw_properties` | `UsableAreaSqM`, `RentableAreaSqM` | High | Usable office area cannot exceed gross rentable area. | `UsableAreaSqM <= RentableAreaSqM` | Reconcile architectural blueprints; apply standard building loss factor (15%). |
| **DQ007** | Referential Integrity| `raw_utilization` | `PropertyKey`, `SpaceKey` | Critical | All foreign keys must exist in parent dimension tables. | `FK IN (SELECT PK FROM Parent)` | Isolate orphaned records; resolve to correct space/property master. |
| **DQ008** | Financial Validity| `raw_property_costs` | `RentCost`, `EnergyCost`, `FacilitiesCost` | High | Operating expenditure entries must not be negative. | `CostComponent >= 0` | Rectify erroneous negative debit/credit sign errors; convert to positive expense. |
| **DQ009** | Completeness | `raw_properties` | `City`, `Region`, `OwnershipType` | Medium | Geographic and contractual attributes must not be null or blank. | `Column IS NOT NULL AND TRIM(Column) != ''` | Impute missing values from verified property master lookup tables. |
| **DQ010** | Uniqueness | `raw_utilization` | `DateKey`, `SpaceKey` | High | Only one consolidated utilization record per space per business day. | `COUNT(*) = 1 GROUP BY DateKey, SpaceKey` | Deduplicate identical timestamp observations by taking daily average. |
| **DQ011** | Range Validity | `raw_room_utilization`| `AttendedBookingCount`, `BookingCount` | Medium | Attended meeting reservations cannot exceed total scheduled reservations. | `AttendedBookingCount <= BookingCount` | Align attended count with verified sensor presence; cap at `BookingCount`. |
| **DQ012** | Density Plausibility| `raw_properties` | `UsableAreaSqM`, `CapacitySeats` | Warning | Workplace density must fall within plausible limits (5.0 to 25.0 $m^2$/desk). | `5.0 <= (UsableAreaSqM / CapacitySeats) <= 25.0` | Flag extreme outliers for facility engineering audit. |

---

## 3. Severity Classification & Escalation Matrix

- **Critical:** Prevents analytical consumption. Data cannot be loaded into the analytical layer until remediated. (e.g., duplicated primary keys, impossible utilization >100%, orphaned foreign keys).
- **High:** Distorts financial, legal, or regional aggregations. Must be systematically standardized or corrected via audited transformations. (e.g., inverted lease dates, negative operating costs, country-city mismatches).
- **Medium / Warning:** Spatial or operational anomalies requiring logging and investigation, but safe for analytical processing under documented caveats. (e.g., room booking no-show discrepancies, extreme density ratios).

---

## 4. The Quality Issue Manifest Standard

Every injected or discovered raw anomaly is recorded in `data/quality_issue_manifest.csv` with the following contract:

```csv
issue_id,table_name,record_identifier,issue_type,expected_rule,injected_value,expected_correct_value,severity
```

- `issue_id`: Unique identifier (e.g., `DQ-MAN-001`).
- `table_name`: Name of the raw CSV file where defect resides.
- `record_identifier`: Primary/business key of the defective row.
- `issue_type`: Category identifier matching rules `DQ001` through `DQ012`.
- `expected_rule`: Explicit rule description.
- `injected_value`: The uncleaned erroneous value in the RAW layer.
- `expected_correct_value`: The verified clean value produced in the CLEAN layer.
- `severity`: `Critical`, `High`, or `Medium`.

This manifest is ingested into `fact_data_quality` and displayed directly on **Page 6 of the Power BI dashboard**, providing auditability and transparency.
