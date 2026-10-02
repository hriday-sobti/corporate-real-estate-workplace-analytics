# Operational & Analytical Assumptions

**Project:** Corporate Real Estate Portfolio & Workplace Analytics  
**Reporting Horizon:** October 2024 through September 2026 (24-Month Analytical Window)  
**Reporting Baseline Date:** 2026-09-30  

---

## 1. Temporal & Calendar Assumptions

1. **Analytical Observation Period:**
   - The analysis covers a 24-month historical observation window from **October 1, 2024 to September 30, 2026** (inclusive).
   - All month-by-month and rolling analyses are anchored to the baseline reporting date of **September 30, 2026**.

2. **Working Days & Business Hours:**
   - Standard business working days are defined as **Monday through Friday** (excluding regional official public holidays).
   - Core operational workplace capacity is calculated on a standard **10-hour business day** (08:00 to 18:00).
   - Weekend facility activity (Saturday and Sunday) is tracked separately for critical data validation but excluded from core corporate workplace utilization averages to avoid artificial dilution.

3. **Time Zones:**
   - While facilities operate across local time zones (IST UTC+5:30, SGT/MYT UTC+8, ICT UTC+7, WIB UTC+7, AEST UTC+10), all daily utilization aggregations are normalized to the local business day of the respective asset.

---

## 2. Spatial & Capacity Assumptions

1. **Area Measurement Denominators:**
   - **Rentable Area ($m^2$):** Total floor area as defined in the commercial lease agreement, including building service cores, common lift lobbies, shared vertical penetrations, and mechanical shafts.
   - **Usable Area ($m^2$):** Net internal workable area dedicated to tenant business operations (workstations, meeting spaces, private offices, collaboration zones, and reception).
   - **Analytical Rule:** Unless specifically stated as rentable area (for base rent comparisons), **all density, space efficiency, and cost per area metrics use Usable Area ($m^2$) as the official denominator**.

2. **Capacity Definition:**
   - **Seat Capacity (`CapacitySeats`):** Total count of physical, ergonomically fitted work points designated for primary individual work (open workstations, agile desks, and private office desks).
   - Collaborative seating (informal lounge chairs, cafeteria seating, pantry booths) is excluded from primary seat capacity to maintain strict comparability.

3. **Occupancy vs. Utilization Definitions:**
   - **Assigned Headcount / Occupancy:** The number of personnel administrative records assigned to a facility by Human Resources.
   - **Utilization:** The empirical measurement of physical seats or rooms actively occupied during available operating hours.
   - **Occupancy Rate:** $\frac{\text{Assigned Headcount}}{\text{Seat Capacity}}$ (Static administrative metric).
   - **Average Utilization Rate:** $\frac{\text{Sum of Actual Occupied Hours}}{\text{Sum of Total Available Seat Hours}}$ (Dynamic operational metric).
   - **Peak Utilization Rate:** The maximum concurrent seat occupancy observed on a given day divided by available seat capacity.
   - **Capacity Pressure:** Operational threshold reached when daily peak utilization equals or exceeds **85.0%** of available capacity.

---

## 3. Financial & Currency Assumptions

1. **Reporting Currency:**
   - The primary reporting currency across all regional rollups and dashboard comparisons is the **Indian Rupee (INR - ₹)**.
   - Local asset operational transactions are recorded in local legal tender and converted to INR using fixed project reference exchange rates.

2. **Reference Foreign Exchange Rates (to INR):**
   - **INR:** 1.000
   - **SGD (Singapore Dollar):** 63.500
   - **MYR (Malaysian Ringgit):** 18.200
   - **THB (Thai Baht):** 2.350
   - **IDR (Indonesian Rupiah):** 0.00530 (10,000 IDR = ₹53.00)
   - **AUD (Australian Dollar):** 55.200
   - *Note:* These rates are project-defined reference assumptions reflecting long-term purchasing parity and do not represent live treasury hedging rates.

3. **Cost Aggregation & Denominators:**
   - **Total Operating Cost:** Computed as $\text{Rent Cost} + \text{Service Charges} + \text{Energy \& Utilities} + \text{Facilities Management} + \text{Maintenance} + \text{Other Operating Costs}$.
   - **Cost per Usable Square Metre ($₹/m^2$):** $\frac{\text{Annual Total Operating Cost}}{\text{Usable Area } (m^2)}$
   - **Cost per Available Seat ($₹/\text{seat}$):** $\frac{\text{Annual Total Operating Cost}}{\text{Seat Capacity}}$
   - **Cost per Occupied Seat ($₹/\text{occupied seat}$):** $\frac{\text{Annual Total Operating Cost}}{\text{Average Daily Presence}}$
     *(Where Average Daily Presence is the average number of distinct personnel physically utilizing the facility daily).*

---

## 4. Lease Management Assumptions

1. **Lease Milestone Categorization:**
   - All lease evaluation categories are calculated relative to the reporting date (**2026-09-30**):
     - **Expired:** Lease end date < 2026-09-30.
     - **Expiring within 6 Months:** 2026-09-30 $\le$ Lease end date $\le$ 2027-03-31.
     - **Expiring within 12 Months:** 2027-03-31 < Lease end date $\le$ 2027-09-30.
     - **Expiring within 24 Months:** 2027-09-30 < Lease end date $\le$ 2028-09-30.
     - **Longer Horizon:** Lease end date > 2028-09-30.
   - **Owned Assets:** Classified as "Owned / Freehold", with no contractual lease expiry date.

---

## 5. Synthetic Generation & Data Quality Ingestion

1. **Deterministic Reproducibility:**
   - Generation algorithms run with a fixed seed (`seed = 42`) across Python `numpy.random` and `random` packages, guaranteeing bit-for-bit repeatability across test runs.

2. **Controlled Imperfections (Data Quality Layer):**
   - The raw ingestion data intentionally contains a controlled error rate (~1.5% to 3.0% of records across specific tables) mimicking legacy CAFM, HRIS, and ERP synchronization errors.
   - Every injected error is strictly indexed in `data/quality_issue_manifest.csv` with expected rule, injected value, and ground-truth correction.
   - No data in `data/raw/` is silently repaired; all corrections occur through the auditable validation and cleaning pipeline in `src/cleaning/`.
