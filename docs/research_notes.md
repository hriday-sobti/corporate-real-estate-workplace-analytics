# Corporate Real Estate & Workplace Analytics: Domain Research Notes

**Project:** Corporate Real Estate Portfolio & Workplace Analytics  
**Scope:** Regional Portfolio (India & Asia-Pacific)  
**Research Date:** October 2026  
**Analyst:** Lead Corporate Real Estate Data Analyst  

---

## 1. Corporate Real-Estate Portfolio Management

- **Source:** CoreNet Global (The Global Association for Corporate Real Estate) — *The Essential Guide to Corporate Real Estate*
- **Topic:** Corporate real-estate portfolio management
- **Important Concept:** Corporate Real Estate (CRE) portfolio management balances physical asset commitments with enterprise operational requirements. CRE is typically an enterprise's second-largest operational expense after labor. Portfolios must be managed through continuous tracking of commitments (leases, capital investments, operating expenses) relative to operational business demand, avoiding either surplus drag or acute capacity bottlenecks.
- **How the Concept Affects the Project:** Establishes the governing mental model: real estate is not a speculative investment vehicle here, but an operational delivery infrastructure. Every property must be evaluated by whether it provides appropriate capacity, at sensible operational cost, aligned with current business presence.
- **URL:** https://www.corenetglobal.org
- **Access/Research Date:** 2026-10-02

---

## 2. Workplace Utilization

- **Source:** International Facility Management Association (IFMA) — *Workplace Strategy & Space Utilization Benchmark Research*
- **Topic:** Workplace utilization
- **Important Concept:** Workplace utilization measures the actual temporal and spatial usage of workplace capacity over specified operational intervals (e.g., business hours 08:00–18:00 on working days). In contrast to static headcount counts, utilization records whether physical desks, collaboration spaces, and offices are actively engaged by personnel.
- **How the Concept Affects the Project:** Directly governs `fact_daily_workplace_utilization`. Measurements must reflect time-bound presence (occupied hours vs available operating hours) rather than just a binary badge swipe at the turnstile.
- **URL:** https://www.ifma.org
- **Access/Research Date:** 2026-10-02

---

## 3. Occupancy versus Utilization

- **Source:** RICS (Royal Institution of Chartered Surveyors) Professional Standard — *Strategic Real Estate and Facilities Management*
- **Topic:** Occupancy versus utilization
- **Important Concept:** "Occupancy" refers to allocated or assigned status (e.g., 400 staff formally assigned to a 500-seat facility yields 80% assigned occupancy). "Utilization" refers to physical, temporal presence (e.g., on any given Tuesday, only 220 of those staff are in the building, yielding 44% actual utilization). Confusing these two creates severe strategic miscalculations in sizing.
- **How the Concept Affects the Project:** The data model strictly separates `AssignedCapacity` / `AssignedHeadcount` (occupancy dimension) from `ActualOccupants` / `UtilizationRate` (utilization fact). Dashboards and reports must never use these terms interchangeably.
- **URL:** https://www.rics.org/profession-standards/rics-standards-and-guidance
- **Access/Research Date:** 2026-10-02

---

## 4. Capacity Planning

- **Source:** ISO 41001:2018 (Facility Management — Management Systems — Requirements with Guidance for Use)
- **Topic:** Capacity planning
- **Important Concept:** Practical operational capacity is bounded below physical nameplate capacity. Office environments experience functional friction when utilization exceeds 80–85% ("choke point"), as finding available workstations or meeting rooms becomes difficult, causing productivity degradation and friction. Effective planning requires a buffer between average demand and maximum capacity.
- **How the Concept Affects the Project:** Establishes the `Capacity Pressure %` KPI and thresholds. Locations operating above 85% peak utilization are flagged as capacity-pressured, even if their monthly average appears modest.
- **URL:** https://www.iso.org/standard/68021.html
- **Access/Research Date:** 2026-10-02

---

## 5. Peak versus Average Utilization

- **Source:** Cushman & Wakefield & CoreNet Global — *Occupier Survey & Global Office Utilization Trends*
- **Topic:** Peak versus average utilization
- **Important Concept:** Hybrid work models exhibit marked variation across weekdays: Tuesdays through Thursdays frequently experience peak occupancies of 70–85%, while Mondays and Fridays drop to 35–50%. Managing solely to the monthly average (e.g., 55%) masks acute mid-week overcrowding and shortages.
- **How the Concept Affects the Project:** `fact_daily_workplace_utilization` captures both `AverageOccupancy` and `PeakOccupants` daily, enabling the construction of the project's signature **Workplace Pressure Matrix** (X-axis: Average Utilization, Y-axis: Peak Utilization).
- **URL:** https://ir.cushmanwakefield.com/news/press-release-details/2025/Cushman--Wakefield-and-CoreNet-Global-Release-New-Survey-Results-on-What-Occupiers-Want/default.aspx
- **Access/Research Date:** 2026-10-02

---

## 6. Space Efficiency

- **Source:** BOMA International (Building Owners and Managers Association) — *ANSI/BOMA Z65.1 Office Standard: Methods of Measurement*
- **Topic:** Space efficiency
- **Important Concept:** Space efficiency evaluates the ratio between usable area (workable space allocated for occupants) and rentable area (including core services, corridors, risers, and structural columns). The "building loss factor" or "core factor" typically ranges between 12% and 22% in prime commercial real estate.
- **How the Concept Affects the Project:** `dim_property` and `dim_floor` track both `RentableAreaSqM` and `UsableAreaSqM`. All efficiency ratios (e.g., space per seat) explicitly use Usable Area as the primary denominator to maintain comparability across architectural floorplates.
- **URL:** https://www.boma.org/BOMA/Research-Resources/BOMA-Standards/Standard_Z65_1_2017.aspx
- **Access/Research Date:** 2026-10-02

---

## 7. Cost per Seat

- **Source:** JLL (Jones Lang LaSalle) — *Global Corporate Real Estate Benchmarks & Occupancy Costs*
- **Topic:** Cost per seat
- **Important Concept:** Total annual operating cost divided by the total number of physical work points/seats provisioned. This reflects the baseline carrying cost of provisioned infrastructure regardless of whether employees enter the building.
- **How the Concept Affects the Project:** Calculated as `Annualized Operating Cost / CapacitySeats`. Serves as the fixed-capacity benchmark against which actual usage costs are contrasted.
- **URL:** https://www.jll.com/en/trends-and-insights/research
- **Access/Research Date:** 2026-10-02

---

## 8. Cost per Square Metre

- **Source:** CBRE Research — *Asia Pacific & India Office Market Figures*
- **Topic:** Cost per square metre
- **Important Concept:** Total real-estate operational expenditure (gross rent, facility maintenance, property management, energy/utilities) divided by total usable or rentable floor area. Market benchmark for real-estate efficiency across regional geographies.
- **How the Concept Affects the Project:** Standardizes cross-market cost analysis across high-cost hubs (Singapore, Sydney) and high-growth operational centers (Bengaluru, Pune, Hyderabad, Delhi-NCR, Mumbai, Chennai, Bangkok, Kuala Lumpur, Jakarta).
- **URL:** https://www.cbre.co.in/insights/figures
- **Access/Research Date:** 2026-10-02

---

## 9. Cost per Occupied Seat

- **Source:** CoreNet Global Research — *Workplace Financial Metrics: Moving from Static to Dynamic Ratios*
- **Topic:** Cost per occupied seat
- **Important Concept:** Total annual operational cost divided by the actual daily average occupied headcount (`Cost / Average Daily Presence`). If a facility has 1,000 seats costing ₹100,000/seat/year, but only 400 people utilize it on average, the effective cost per occupied seat escalates to ₹250,000/occupied seat/year.
- **How the Concept Affects the Project:** This is the primary economic efficiency indicator in the dashboard and report. It exposes the hidden financial penalty of underutilized space without requiring headcount reductions.
- **URL:** https://www.corenetglobal.org/docs/default-source/default-document-library/pdf/space-utilization-metrics-team9-report.pdf
- **Access/Research Date:** 2026-10-02

---

## 10. Workplace Density

- **Source:** British Council for Offices (BCO) — *Guide to Specification: Workplace Density & Occupancy Standards*
- **Topic:** Workplace density
- **Important Concept:** Ratio of net usable floor area per seat or person. Modern agile workplaces typically target 8.0 m² to 11.5 m² (approx. 85–125 sq ft) usable area per work point. Lower density (>14 m²/seat) implies excess circulation or executive legacy layouts; higher density (<7 m²/seat) risks severe acoustic and thermal comfort degradation.
- **How the Concept Affects the Project:** Used in data validation and spatial analytics. Properties with density outside realistic bounds (e.g. <5 m² or >25 m² per seat) trigger analytical audit alerts.
- **URL:** https://www.bco.org.uk
- **Access/Research Date:** 2026-10-02

---

## 11. Lease Dates and Lease-Expiry Exposure

- **Source:** RICS Guidance Note — *Commercial Real Estate Lease Management and Critical Dates*
- **Topic:** Lease dates and lease-expiry exposure
- **Important Concept:** Lease event management centers on "critical dates": expiration dates, break options, renewal notice windows, and rent review dates. Missing a notice window (typically 6–12 months prior to expiry) forfeits renegotiation leverage or locks the tenant into unfavorable rollover terms.
- **How the Concept Affects the Project:** `dim_lease` classifies properties into explicit management decision horizons: Expired, Expiring ≤6 months, Expiring 6–12 months, Expiring 12–24 months, and Horizon >24 months. Cross-referencing approaching lease dates with underutilization isolates immediate commercial opportunities.
- **URL:** https://www.rics.org
- **Access/Research Date:** 2026-10-02

---

## 12. Property Ownership versus Lease Structures

- **Source:** Corporate Real Estate Handbook (Springer) — *Strategic Facility Portfolio Structuring*
- **Topic:** Property ownership versus lease structures
- **Important Concept:** Portfolios combine Owned (freehold), Leased (operating leases), and occasionally Subleased spaces. Owned properties incur depreciation and direct facility management but offer capital stability; leased assets entail contractual recurring lease liabilities with periodic exit or renegotiation milestones.
- **How the Concept Affects the Project:** Dimension attribute `OwnershipType` (Leased vs Owned). Owned assets cannot be "expired" or surrendered at lease end, requiring capital repurposing or sublease strategies rather than simple lease non-renewal.
- **URL:** https://link.springer.com/book/10.1007/978-3-642-32694-3
- **Access/Research Date:** 2026-10-02

---

## 13. Office / Workplace Facility Types

- **Source:** IFMA Space Planning Standard & CoreNet Workplace Classification
- **Topic:** Office / workplace facility types
- **Important Concept:** Enterprise facilities serve differentiated strategic functions: Regional Headquarters (flagship amenities, executive suites, client hosting), Technology & Engineering Hubs (high workstation density, lab spaces, robust infrastructure), Business Operations Centers (shared services, high headcount efficiency), and Regional Sales & Client Offices (agile touchdown desks, heavy meeting spaces).
- **How the Concept Affects the Project:** `dim_facility_type` classifies each property into these four core operational archetypes, ensuring analytics compare like-with-like rather than comparing a client-facing headquarters directly against a 24/7 engineering campus.
- **URL:** https://www.ifma.org
- **Access/Research Date:** 2026-10-02

---

## 14. Meeting-Room Utilization

- **Source:** Leesman Workplace Index & CoreNet Space Utilization Research
- **Topic:** Meeting-room utilization
- **Important Concept:** Meeting room dynamics exhibit two severe operational dysfunctions: (a) "Ghost bookings" / no-shows (rooms booked on calendar systems but never physically occupied, typically 20–35% of bookings), and (b) Capacity mismatch (2–3 people occupying a 10-to-16-person board room because small 4-person huddle rooms are unavailable).
- **How the Concept Affects the Project:** Governs `fact_room_utilization`. Tracks `RoomCapacity`, `BookedHours`, `OccupiedHours`, `AverageAttendees`, `NoShowCount`, and `RoomUtilizationRate` to highlight spatial misallocation.
- **URL:** https://www.leesmanindex.com/research-insights
- **Access/Research Date:** 2026-10-02

---

## 15. Data Quality in Real-Estate Databases

- **Source:** DAMA International (Data Management Body of Knowledge - DAMA-DMBOK2) & Real Estate Information Standards (REIS)
- **Topic:** Data quality in real-estate databases
- **Important Concept:** Real estate portfolios suffer chronic data hygiene issues caused by siloed departmental databases (HR headcount files, CAFM badge systems, lease administration systems, ERP accounts payable). Common errors include inconsistent city/country labels, area unit confusions (sq ft vs sq m), impossible occupancies > capacity, and inverted lease dates.
- **How the Concept Affects the Project:** Rather than assuming pristine input, the project implements a rigorous data-quality architecture: controlled synthetic errors injected into `RAW`, logged in `quality_issue_manifest.csv`, detected via automated validation rules (DQ001–DQ012), cleaned into `CLEAN`, and surfaced transparently on Page 6 of the Power BI dashboard.
- **URL:** https://www.dama.org
- **Access/Research Date:** 2026-10-02

---

## 16. Portfolio Exception Management

- **Source:** Gartner IT & Business Analytics Best Practices — *Exception Reporting and Operational Triaging*
- **Topic:** Portfolio exception management
- **Important Concept:** Operational leaders cannot review thousands of raw rows; management requires systematic filtering that flags outliers breaching defined operational tolerances (e.g. utilization <30%, peak utilization >90%, cost/seat >1.5x regional median, lease expiry <9 months with unresolved strategy).
- **How the Concept Affects the Project:** Underpins the **Portfolio Attention Index** and the **Management Attention Table**, isolating the top 5–10 portfolio anomalies demanding executive review.
- **URL:** https://www.gartner.com
- **Access/Research Date:** 2026-10-02

---

## 17. Regional Reporting

- **Source:** CBRE APAC & India Real Estate Market Perspectives
- **Topic:** Regional reporting
- **Important Concept:** Multilateral regional portfolios require hierarchical geographic reporting: Region → Country → Market/Metro → Property → Floor → Space. Currency standardization is mandatory: operational local payments (INR, SGD, MYR, THB, IDR, AUD) must be translated into a consistent presentation currency (INR) using disciplined reference exchange rates to permit fair rollups.
- **How the Concept Affects the Project:** Implements a strict star-schema hierarchy with `dim_geography` and currency translation fields (`OriginalCurrency`, `OriginalAmount`, `FXRateToINR`, `ReportingAmountINR`).
- **URL:** https://www.cbre.com/insights/figures/asia-pacific-figures-q3-2024
- **Access/Research Date:** 2026-10-02

---

## 18. Management Reporting

- **Source:** Harvard Business Review / McKinsey & Company — *Structure and Synthesis in Executive Briefings (The Minto Pyramid Principle)*
- **Topic:** Management reporting
- **Important Concept:** Executive reporting must lead with the conclusion and operational implication, supported by structured evidence, rather than narrating analytical mechanics chronologically. Every visual must answer a business question, with concise analyst commentary explaining why the variance matters.
- **How the Concept Affects the Project:** Governs the architecture of the 8–12 page PDF report and the 7-slide PowerPoint deck. Every major finding follows: Observation → Evidence → Interpretation → Business Implication → Area for Management Investigation.
- **URL:** https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights
- **Access/Research Date:** 2026-10-02

---

## 19. Workplace Strategy

- **Source:** Gensler Research Institute — *Workplace Survey & Strategy Frameworks*
- **Topic:** Workplace strategy
- **Important Concept:** Workplace strategy aligns the physical work environment with business goals, technology, and people. Rather than treating real estate merely as an expense to be slashed, effective strategy evaluates space as an enabler of collaboration, innovation, and culture, utilizing sharing ratios (assigned headcount to seats: 1.2:1 to 1.5:1) and diversified space typologies (open workstations, focus booths, collaborative lounges, multi-tier meeting rooms).
- **How the Concept Affects the Project:** Guides the scenario modeling module (Phase 4): analyzing space consolidation and sharing ratios to demonstrate realistic operational savings while safeguarding peak buffer capacity.
- **URL:** https://www.gensler.com/gri/us-workplace-survey-2024
- **Access/Research Date:** 2026-10-02

---

## 20. Project Coordination

- **Source:** Project Management Institute (PMI) — *A Guide to the Project Management Body of Knowledge (PMBOK Guide Seventh Edition)*
- **Topic:** Project coordination
- **Important Concept:** Complex analytical initiatives require multi-workstream tracking across Data, Data Quality, Analytics, Dashboard, Reporting, Presentation, QA, and Documentation. Tracking requires explicit owners, dependencies, milestones, and deliverable reconciliation to ensure technical outputs align with reporting deliverables.
- **How the Concept Affects the Project:** Governs `project_tracker.csv` and the corresponding Excel Project Tracker sheet, providing end-to-end transparency into milestone completion and dependencies across all project deliverables.
- **URL:** https://www.pmi.org/pmbok-guide-standards
- **Access/Research Date:** 2026-10-02
