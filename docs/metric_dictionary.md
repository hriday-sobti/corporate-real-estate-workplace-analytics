# Corporate Real Estate & Workplace Analytics: Metric Dictionary

**Project:** Corporate Real Estate Portfolio & Workplace Analytics  
**Version:** 1.0  
**Baseline Reporting Date:** 2026-09-30  

---

## 1. Primary Portfolio & Spatial Metrics

### M01: Total Properties
- **Definition:** The total count of active operational real estate assets in the regional portfolio.
- **Formula:** $\text{CountDistinct}(\text{PropertyKey})$
- **Unit of Measurement:** Integer (assets)
- **Business Interpretation:** Defines the operational footprint and span of management control across countries and cities.

### M02: Rentable Area ($m^2$)
- **Definition:** Total gross commercial floor area leased or owned, including building cores, vertical service penetrations, primary lift lobbies, and public corridors.
- **Formula:** $\sum \text{RentableAreaSqM}$
- **Unit of Measurement:** Square metres ($m^2$)
- **Business Interpretation:** The primary denominator for contractual base rent liabilities in commercial lease agreements.

### M03: Usable Area ($m^2$)
- **Definition:** Net floor area dedicated to business operations, encompassing workstations, meeting rooms, offices, collaborative hubs, and internal circulation.
- **Formula:** $\sum \text{UsableAreaSqM}$
- **Unit of Measurement:** Square metres ($m^2$)
- **Business Interpretation:** The true functional working envelope. Standard denominator for operational efficiency, density, and utilization metrics.

### M04: Building Loss Factor / Core Factor (%)
- **Definition:** The percentage difference between rentable and usable area.
- **Formula:** $\frac{\text{Rentable Area} - \text{Usable Area}}{\text{Rentable Area}} \times 100\%$
- **Unit of Measurement:** Percentage (%)
- **Business Interpretation:** Measures architectural building efficiency; typical commercial office range is 12% to 22%. Higher values indicate structural inefficiency in lease contracts.

### M05: Seat Capacity
- **Definition:** The total count of primary individual physical work points (desks, ergonomic workstations, private office desks) installed and available for daily operational use.
- **Formula:** $\sum \text{CapacitySeats}$
- **Unit of Measurement:** Seats / Work points
- **Business Interpretation:** The physical capacity ceiling against which staffing and physical presence are planned.

### M06: Workplace Density ($m^2/\text{seat}$)
- **Definition:** The average usable floor area allocated per available work point.
- **Formula:** $\frac{\text{Total Usable Area } (m^2)}{\text{Total Seat Capacity}}$
- **Unit of Measurement:** $m^2$ per seat
- **Business Interpretation:** Standard benchmark for spatial planning. Benchmarks: $<7.5 \, m^2$ is hyper-dense; $8.5–11.0 \, m^2$ represents modern agile standards; $>14.0 \, m^2$ indicates low-density or legacy private office configuration.

---

## 2. Occupancy vs. Utilization Metrics

### M07: Assigned Headcount
- **Definition:** The total number of active employees and regular contractors formally registered to an asset in the HR administrative system.
- **Formula:** $\sum \text{AssignedHeadcount}$
- **Unit of Measurement:** People / Headcount
- **Business Interpretation:** Measures the administrative allocation of organizational headcount to an office location.

### M08: Assigned Occupancy Rate (%)
- **Definition:** The ratio of administratively assigned headcount relative to available seat capacity.
- **Formula:** $\frac{\text{Assigned Headcount}}{\text{Total Seat Capacity}} \times 100\%$
- **Unit of Measurement:** Percentage (%)
- **Business Interpretation:** Indicates sharing policy and allocation depth. A ratio of 100% means 1:1 dedicated seating. Ratios of 120%–150% represent modern agile sharing ratios (desk sharing).

### M09: Average Daily Presence
- **Definition:** The average number of distinct personnel physically present in the facility during standard business days over the observation window.
- **Formula:** $\frac{1}{N_{\text{days}}} \sum_{d=1}^{N_{\text{days}}} \text{ActualDailyOccupants}_d$
- **Unit of Measurement:** People / Average occupants per business day
- **Business Interpretation:** The empirical reality of facility usage, directly contrasting against administrative assigned headcount.

### M10: Average Workplace Utilization Rate (%)
- **Definition:** The percentage of available workplace seat-hours that were actively occupied during standard operating hours (08:00 to 18:00, Monday through Friday).
- **Formula:** $\frac{\sum \text{Occupied Hours}}{\sum \text{Available Hours}} \times 100\% \equiv \frac{\text{Average Daily Presence}}{\text{Total Seat Capacity}} \times 100\%$
- **Unit of Measurement:** Percentage (%)
- **Business Interpretation:** Primary indicator of space usage efficiency over time. Identifies sustained underutilization or high baseline commitment.

### M11: Peak Workplace Utilization Rate (%)
- **Definition:** The maximum observed concurrent utilization rate achieved across standard working days within the observation period.
- **Formula:** $\max_{d} \left( \frac{\text{PeakOccupants}_d}{\text{Total Seat Capacity}} \right) \times 100\%$
- **Unit of Measurement:** Percentage (%)
- **Business Interpretation:** Highlights the operational bottleneck. Even if average utilization is 55%, a peak of 92% on Wednesdays means the building experiences severe capacity strain during mid-week collaborative peaks.

### M12: Vacant Seat Capacity
- **Definition:** The volume of provisioned seat infrastructure not actively utilized on an average operational day.
- **Formula:** $\text{Total Seat Capacity} - \text{Average Daily Presence}$
- **Unit of Measurement:** Seats
- **Business Interpretation:** Quantifies unutilized physical capacity that carries recurring lease, energy, and maintenance costs without providing day-to-day operational benefit.

### M13: Capacity Pressure Rate (%)
- **Definition:** The proportion of business days where peak workplace utilization reached or exceeded the critical friction threshold of 85.0%.
- **Formula:** $\frac{\text{Count of Business Days where Peak Utilization} \ge 85\%}{\text{Total Business Days}} \times 100\%$
- **Unit of Measurement:** Percentage (%)
- **Business Interpretation:** Measures operational crowding risk. High capacity pressure generates employee dissatisfaction, conference room shortages, and productivity drag.

---

## 3. Financial & Cost Efficiency Metrics

### M14: Total Operating Cost
- **Definition:** The aggregate annual cost of occupying and operating real estate assets, translated to Indian Rupees (INR - ₹).
- **Formula:** $\sum (\text{RentCost} + \text{ServiceCharge} + \text{EnergyCost} + \text{FacilitiesCost} + \text{MaintenanceCost} + \text{OtherOperatingCost}) \times \text{FXRateToINR}$
- **Unit of Measurement:** Currency (₹ / INR)
- **Business Interpretation:** Total financial operational commitment of the regional portfolio.

### M15: Annual Cost per Usable Square Metre ($₹/m^2$)
- **Definition:** The total annual operating expense divided by the usable area of the asset.
- **Formula:** $\frac{\text{Annual Operating Cost (INR)}}{\text{Total Usable Area } (m^2)}$
- **Unit of Measurement:** ₹ per $m^2$ per year
- **Business Interpretation:** Normalizes real estate expense across differing city price levels and building quality grades.

### M16: Annual Cost per Available Seat ($₹/\text{seat}$)
- **Definition:** The fixed financial carrying cost incurred per installed work point per year.
- **Formula:** $\frac{\text{Annual Operating Cost (INR)}}{\text{Total Seat Capacity}}$
- **Unit of Measurement:** ₹ per seat per year
- **Business Interpretation:** Reflects the baseline infrastructure cost of providing an ergonomic desk position, regardless of usage.

### M17: Annual Cost per Occupied Seat ($₹/\text{occupied seat}$)
- **Definition:** The effective financial cost incurred for each physical occupant actually utilizing the workplace on an average day.
- **Formula:** $\frac{\text{Annual Operating Cost (INR)}}{\text{Average Daily Presence}}$
- **Unit of Measurement:** ₹ per occupied seat per year
- **Business Interpretation:** The ultimate measure of workplace economic efficiency. In low-utilization buildings, this number surges, highlighting severe financial drag.

---

## 4. Room & Collaboration Metrics

### M18: Room Utilization Rate (%)
- **Definition:** The percentage of bookable room hours actively occupied by meetings.
- **Formula:** $\frac{\sum \text{Occupied Room Hours}}{\sum \text{Available Room Hours}} \times 100\%$
- **Unit of Measurement:** Percentage (%)
- **Business Interpretation:** Determines whether meeting rooms are bottlenecked or sitting empty throughout the business day.

### M19: Room No-Show Rate (%)
- **Definition:** The proportion of scheduled room booking reservations where attendees failed to physically occupy the room ("ghost bookings").
- **Formula:** $\frac{\text{Booked Reservations} - \text{Attended Reservations}}{\text{Total Booked Reservations}} \times 100\%$
- **Unit of Measurement:** Percentage (%)
- **Business Interpretation:** Identifies behavioral friction where calendar hoarding artificially inflates perceived room scarcity.

### M20: Room Capacity Mismatch Ratio
- **Definition:** The ratio of average attendees to physical room seat capacity during attended meetings.
- **Formula:** $\frac{\text{Average Attendees}}{\text{Room Capacity}}$
- **Unit of Measurement:** Ratio (0.0 to 1.0)
- **Business Interpretation:** Discovers spatial misallocation (e.g., 2–3 attendees routinely monopolizing 12-person board rooms due to inadequate 4-person huddle rooms).

---

## 5. Lease & Governance Metrics

### M21: Lease Expiry Horizon
- **Definition:** Contractual time remaining until the scheduled lease termination date, evaluated from the baseline reporting date (2026-09-30).
- **Categories:**
  - `Expired`: End Date < 2026-09-30
  - `Expiring <= 6M`: 2026-09-30 to 2027-03-31
  - `Expiring 6-12M`: 2027-04-01 to 2027-09-30
  - `Expiring 12-24M`: 2027-10-01 to 2028-09-30
  - `Horizon > 24M`: End Date > 2028-09-30
  - `Owned`: Freehold asset
- **Business Interpretation:** Prioritizes lease renegotiation windows. Real estate notices must be given 6–12 months in advance to avoid automatic renewal or penalty fees.

### M22: Data Quality Exception Count & Pass Rate (%)
- **Definition:** The total number of validation check failures logged across raw source files, and the corresponding percentage of clean records.
- **Formula:**
  - $\text{Exception Count} = \text{Count}(\text{QualityIssueManifest records})$
  - $\text{Pass Rate \%} = \frac{\text{Total Records Evaluated} - \text{Total Exceptions}}{\text{Total Records Evaluated}} \times 100\%$
- **Unit of Measurement:** Integer (count) / Percentage (%)
- **Business Interpretation:** Quantifies trust in source system feeds and isolates operational data governance debt.

---

## 6. Project-Specific Strategic Prioritization Models

### M23: Portfolio Attention Index (PAI)
- **Official Label:** *Portfolio Attention Index — Project-defined analytical prioritization score*
- **Nature:** Non-industry analytical composite score ($0.0–100.0$) designed to objectively rank facilities warranting management review.
- **Component Weights:**
  1. **Utilization Inefficiency (30%):** Scaled inverse of average utilization: $(100 - \text{Average Utilization \%})$.
  2. **Cost Intensity (20%):** Scaled relative to regional median cost per occupied seat: $\min\left(100, \frac{\text{CostPerOccupiedSeat}}{\text{PortfolioMedianCostPerOccupiedSeat}} \times 50\right)$.
  3. **Lease Exposure (20%):** Urgency score based on lease horizon (Expiring $\le$ 6M = 100; 6–12M = 75; 12–24M = 40; >24M = 10; Owned = 0).
  4. **Capacity Pressure (15%):** Proportion of days with peak $\ge 85\%$: $\text{CapacityPressure \%} \times 1.0$.
  5. **Data Quality Risk (15%):** Density of logged data quality exceptions per property: $\min(100, \text{DQ Exception Count} \times 10)$.
- **Calculation:**
  $$\text{PAI} = 0.30 \cdot S_{\text{util}} + 0.20 \cdot S_{\text{cost}} + 0.20 \cdot S_{\text{lease}} + 0.15 \cdot S_{\text{cap}} + 0.15 \cdot S_{\text{dq}}$$
- **Business Interpretation:** Higher scores highlight properties combining multiple operational red flags (e.g., low utilization, high cost per attendee, upcoming lease expiry, or poor source data quality).

### M24: Workplace Pressure Matrix Quadrants
- **Visual Design:** Scatter/quadrant plot where:
  - **X-Axis:** Average Utilization Rate (%) [Mid-point benchmark: 55.0%]
  - **Y-Axis:** Peak Utilization Rate (%) [Critical benchmark: 80.0%]
- **Quadrant Definitions:**
  1. **Underutilized (Low Average <55%, Low Peak <80%):** Chronic excess capacity throughout the entire working week. Candidates for consolidation, subleasing, or floor surrender.
  2. **Peak-Sensitive (Low Average <55%, High Peak $\ge$80%):** Severe mid-week crowding (Tue–Thu) despite modest monthly averages. Requires behavioral smoothing, desk hoteling, or remote policy adjustments rather than footprint cuts.
  3. **Consistently Active (High Average $\ge$55%, Low Peak <80%):** Balanced, predictable daily occupancy. Highly stable workplace with minimal friction.
  4. **Capacity-Constrained (High Average $\ge$55%, High Peak $\ge$80%):** Operating near maximum physical thresholds. Urgent need for space expansion, overflow hubs, or aggressive agile sharing policies.
