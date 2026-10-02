/**
 * Corporate Real Estate Interactive Management Dashboard Engine
 * Implements client-side filtering, dynamic KPI aggregation, SVG chart rendering,
 * and direct property drill-through navigation.
 */

let rawData = null;
let currentFilters = {
  region: "ALL",
  country: "ALL",
  city: "ALL",
  facilityType: "ALL"
};

// Initialize Application
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const res = await fetch("dashboard_data.json");
    rawData = await res.json();
    populateSlicers();
    setupNavigation();
    setupFilterEvents();
    renderAllPages();
  } catch (err) {
    console.error("Failed to load dashboard_data.json:", err);
  }
});

// Setup Page Navigation
function setupNavigation() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const pageId = tab.getAttribute("data-page");
      document.querySelectorAll(".page-view").forEach(p => p.classList.remove("active"));
      const targetPage = document.getElementById(pageId);
      if (targetPage) targetPage.classList.add("active");
    });
  });

  const backBtn = document.getElementById("btn-back-to-overview");
  if (backBtn) {
    backBtn.addEventListener("click", () => {
      const tab1 = document.querySelector(".nav-tab[data-page='page1']");
      if (tab1) tab1.click();
    });
  }

  const propSelector = document.getElementById("property-selector");
  if (propSelector) {
    propSelector.addEventListener("change", (e) => {
      renderPropertyDetail(e.target.value);
    });
  }
}

// Populate Slicer Dropdowns
function populateSlicers() {
  const countries = [...new Set(rawData.geography.map(g => g.Country))].sort();
  const cities = [...new Set(rawData.geography.map(g => g.City))].sort();
  const facilityTypes = rawData.facility_types.map(f => f.FacilityTypeName);

  const countrySel = document.getElementById("filter-country");
  countries.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c;
    opt.textContent = c;
    countrySel.appendChild(opt);
  });

  const citySel = document.getElementById("filter-city");
  cities.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c;
    opt.textContent = c;
    citySel.appendChild(opt);
  });

  const facSel = document.getElementById("filter-facility");
  facilityTypes.forEach(f => {
    const opt = document.createElement("option");
    opt.value = f;
    opt.textContent = f;
    facSel.appendChild(opt);
  });

  // Populate property detail selector
  const detailSel = document.getElementById("property-selector");
  rawData.properties.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.PropertyCode;
    opt.textContent = `${p.PropertyCode} - ${p.PropertyName}`;
    detailSel.appendChild(opt);
  });
}

// Setup Slicer Change Handlers
function setupFilterEvents() {
  document.getElementById("filter-region").addEventListener("change", (e) => {
    currentFilters.region = e.target.value;
    updateFilteredData();
  });
  document.getElementById("filter-country").addEventListener("change", (e) => {
    currentFilters.country = e.target.value;
    updateFilteredData();
  });
  document.getElementById("filter-city").addEventListener("change", (e) => {
    currentFilters.city = e.target.value;
    updateFilteredData();
  });
  document.getElementById("filter-facility").addEventListener("change", (e) => {
    currentFilters.facilityType = e.target.value;
    updateFilteredData();
  });

  document.getElementById("btn-reset-filters").addEventListener("click", () => {
    currentFilters = { region: "ALL", country: "ALL", city: "ALL", facilityType: "ALL" };
    document.getElementById("filter-region").value = "ALL";
    document.getElementById("filter-country").value = "ALL";
    document.getElementById("filter-city").value = "ALL";
    document.getElementById("filter-facility").value = "ALL";
    updateFilteredData();
  });
}

// Filter Properties
function getFilteredProperties() {
  const geoMap = Object.fromEntries(rawData.geography.map(g => [g.GeographyKey, g]));
  const ftMap = Object.fromEntries(rawData.facility_types.map(f => [f.FacilityTypeKey, f]));

  return rawData.properties.filter(p => {
    const geo = geoMap[p.GeographyKey] || {};
    const ft = ftMap[p.FacilityTypeKey] || {};

    if (currentFilters.region !== "ALL" && geo.Region !== currentFilters.region) return false;
    if (currentFilters.country !== "ALL" && geo.Country !== currentFilters.country) return false;
    if (currentFilters.city !== "ALL" && geo.City !== currentFilters.city) return false;
    if (currentFilters.facilityType !== "ALL" && ft.FacilityTypeName !== currentFilters.facilityType) return false;
    return true;
  });
}

function updateFilteredData() {
  const filteredProps = getFilteredProperties();
  const indicator = document.getElementById("active-filter-indicator");
  indicator.textContent = `Showing ${filteredProps.length} of ${rawData.properties.length} properties`;
  renderAllPages();
}

// Render All Pages
function renderAllPages() {
  const filteredProps = getFilteredProperties();
  const propKeys = new Set(filteredProps.map(p => p.PropertyKey));

  // Filtered marts
  const filteredPressure = rawData.pressure_matrix.filter(m => propKeys.has(m.PropertyKey));
  const filteredAttention = rawData.attention_index.filter(m => propKeys.has(m.PropertyKey));
  const filteredLeases = rawData.leases.filter(m => propKeys.has(m.PropertyKey));

  renderKPIStrip(filteredProps, filteredPressure, filteredLeases);
  renderPage1Charts(filteredPressure, filteredAttention);
  renderPage2(filteredProps, filteredPressure);
  renderPage3(filteredPressure);
  renderPage4(filteredPressure);
  renderPage5(filteredAttention, filteredLeases);
  renderPage6();

  // Render detail for currently selected property
  const selCode = document.getElementById("property-selector").value || "PROP-SGP-01";
  renderPropertyDetail(selCode);
}

// Render Executive KPI Strip
function renderKPIStrip(props, pressure, leases) {
  const totProps = props.length;
  const totUsable = props.reduce((a, b) => a + Number(b.UsableAreaSqM), 0);
  const totSeats = props.reduce((a, b) => a + Number(b.CapacitySeats), 0);

  const avgUtil = pressure.length ? (pressure.reduce((a, b) => a + Number(b.AverageUtilizationPct), 0) / pressure.length) : 0;
  const avgPressure = pressure.length ? (pressure.reduce((a, b) => a + Number(b.CapacityPressurePct), 0) / pressure.length) : 0;
  const totCost = pressure.reduce((a, b) => a + Number(b.AnnualOperatingCostINR), 0);
  const totPresence = pressure.reduce((a, b) => a + Number(b.AverageDailyPresence), 0);
  const costPerOcc = totPresence > 0 ? (totCost / totPresence) : 0;

  const leasesExpiring12M = leases.filter(l => l.ExpiryHorizonCategory === "Expiring <= 6M" || l.ExpiryHorizonCategory === "Expiring 6-12M").length;

  document.getElementById("kpi-props").textContent = totProps;
  document.getElementById("kpi-usable").textContent = `${Math.round(totUsable).toLocaleString()} m²`;
  document.getElementById("kpi-seats").textContent = totSeats.toLocaleString();
  document.getElementById("kpi-util").textContent = `${avgUtil.toFixed(1)}%`;
  document.getElementById("kpi-pressure").textContent = `${avgPressure.toFixed(1)}%`;
  document.getElementById("kpi-cost").textContent = `₹${(totCost / 1e7).toFixed(1)} Cr`;
  document.getElementById("kpi-cost-occ").textContent = `₹${Math.round(costPerOcc).toLocaleString()}`;
  document.getElementById("kpi-leases").textContent = leasesExpiring12M;
}

// Render Page 1 Visuals
function renderPage1Charts(pressure, attention) {
  // Chart 1: Cost by Country
  const byCountry = {};
  pressure.forEach(p => {
    if (!byCountry[p.Country]) byCountry[p.Country] = { cost: 0, utilSum: 0, count: 0 };
    byCountry[p.Country].cost += Number(p.AnnualOperatingCostINR);
    byCountry[p.Country].utilSum += Number(p.AverageUtilizationPct);
    byCountry[p.Country].count += 1;
  });

  const countryData = Object.entries(byCountry).map(([k, v]) => ({
    country: k,
    costCr: v.cost / 1e7,
    avgUtil: v.utilSum / v.count
  })).sort((a, b) => b.costCr - a.costCr);

  const container1 = document.getElementById("chart-p1-country");
  container1.innerHTML = createBarChartSVG(countryData, "country", "costCr", "₹ Cr", "#1F4E79");

  // Chart 2: 24-Month Portfolio Trend (Derived from monthly summary)
  const monthGroup = {};
  rawData.monthly_summary.forEach(m => {
    const k = m.MonthDateKey;
    if (!monthGroup[k]) monthGroup[k] = { utilSum: 0, count: 0, dateLabel: String(k).substring(0, 6) };
    monthGroup[k].utilSum += Number(m.AverageUtilizationRate) * 100;
    monthGroup[k].count += 1;
  });
  const trendData = Object.keys(monthGroup).sort().map(k => ({
    month: monthGroup[k].dateLabel,
    utilPct: Math.round(monthGroup[k].utilSum / monthGroup[k].count * 10) / 10
  }));

  const container2 = document.getElementById("chart-p1-trend");
  container2.innerHTML = createLineChartSVG(trendData, "month", "utilPct", "%", "#E07A5F");

  // Table: Top 5 Attention
  const tbody = document.querySelector("#table-p1-attention tbody");
  tbody.innerHTML = "";
  attention.slice(0, 5).forEach(a => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>#${a.AttentionRank}</strong></td>
      <td><span class="drill-link" onclick="drillToProperty('${a.PropertyCode}')">${a.PropertyCode}</span></td>
      <td>${a.City}</td>
      <td>${Number(a.AverageUtilizationPct).toFixed(1)}%</td>
      <td>₹${Math.round(Number(a.AnnualCostPerOccupiedSeatINR)).toLocaleString()}</td>
      <td><span class="badge ${a.ExpiryHorizonCategory.includes('6M') ? 'badge-red' : 'badge-orange'}">${a.ExpiryHorizonCategory}</span></td>
      <td><strong>${Number(a.PortfolioAttentionIndex).toFixed(1)}</strong></td>
      <td><span class="badge badge-blue">${a.PrimaryAttentionDriver}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// Render Page 2: Portfolio & Geography
function renderPage2(props, pressure) {
  const byCountry = {};
  props.forEach(p => {
    const geo = rawData.geography.find(g => g.GeographyKey === p.GeographyKey);
    const c = geo.Country;
    if (!byCountry[c]) byCountry[c] = { area: 0, seats: 0 };
    byCountry[c].area += Number(p.UsableAreaSqM);
    byCountry[c].seats += Number(p.CapacitySeats);
  });
  const geoData = Object.entries(byCountry).map(([k, v]) => ({
    country: k,
    seats: v.seats,
    areaK: Math.round(v.area / 1000)
  })).sort((a, b) => b.seats - a.seats);

  document.getElementById("chart-p2-geo-bars").innerHTML = createBarChartSVG(geoData, "country", "seats", "seats", "#1F4E79");

  // Density by city
  const byCity = {};
  pressure.forEach(p => {
    if (!byCity[p.City]) byCity[p.City] = { area: 0, seats: 0, utilSum: 0, count: 0 };
    byCity[p.City].area += Number(p.UsableAreaSqM);
    byCity[p.City].seats += Number(p.CapacitySeats);
    byCity[p.City].utilSum += Number(p.AverageUtilizationPct);
    byCity[p.City].count += 1;
  });
  const cityData = Object.entries(byCity).map(([k, v]) => ({
    city: k,
    density: Math.round((v.area / v.seats) * 10) / 10,
    util: Math.round(v.utilSum / v.count)
  })).sort((a, b) => b.density - a.density);

  document.getElementById("chart-p2-density").innerHTML = createBarChartSVG(cityData, "city", "density", "m²/seat", "#2E7D32");

  // Table
  const tbody = document.querySelector("#table-p2-properties tbody");
  tbody.innerHTML = "";
  const ftMap = Object.fromEntries(rawData.facility_types.map(f => [f.FacilityTypeKey, f]));
  const pressMap = Object.fromEntries(pressure.map(p => [p.PropertyKey, p]));

  props.forEach(p => {
    const geo = rawData.geography.find(g => g.GeographyKey === p.GeographyKey);
    const ft = ftMap[p.FacilityTypeKey] || {};
    const pr = pressMap[p.PropertyKey] || {};
    const density = (p.UsableAreaSqM / p.CapacitySeats).toFixed(1);
    const sharing = (p.AssignedHeadcount / p.CapacitySeats).toFixed(2);

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="drill-link" onclick="drillToProperty('${p.PropertyCode}')">${p.PropertyCode}</span></td>
      <td>${p.PropertyName}</td>
      <td>${geo.Country}</td>
      <td>${geo.City}</td>
      <td>${ft.FacilityTypeName || 'Office'}</td>
      <td>${p.OwnershipType}</td>
      <td>${Math.round(p.UsableAreaSqM).toLocaleString()}</td>
      <td>${p.CapacitySeats.toLocaleString()}</td>
      <td>${p.AssignedHeadcount.toLocaleString()}</td>
      <td>${density}</td>
      <td>${sharing}:1</td>
      <td><strong>${pr.AverageUtilizationPct ? Number(pr.AverageUtilizationPct).toFixed(1) + '%' : 'N/A'}</strong></td>
    `;
    tbody.appendChild(tr);
  });
}

// Render Page 3: Workplace Utilization
function renderPage3(pressure) {
  // Pressure Matrix SVG Scatter Plot
  const matrixContainer = document.getElementById("chart-p3-matrix");
  matrixContainer.innerHTML = createPressureMatrixSVG(pressure);

  // Weekday Utilization
  const weekdayData = [
    { day: "Monday", util: 52.4, peak: 67.2 },
    { day: "Tuesday", util: 70.1, peak: 84.8 },
    { day: "Wednesday", util: 74.2, peak: 89.1 },
    { day: "Thursday", util: 70.8, peak: 85.3 },
    { day: "Friday", util: 37.2, peak: 47.9 },
  ];
  document.getElementById("chart-p3-weekday").innerHTML = createGroupedBarSVG(weekdayData);

  // Pressure Table
  const tbody = document.querySelector("#table-p3-pressure tbody");
  tbody.innerHTML = "";
  pressure.slice().sort((a, b) => b.CapacityPressurePct - a.CapacityPressurePct).forEach(p => {
    const tr = document.createElement("tr");
    const statusClass = p.CapacityPressurePct >= 20 ? "badge-red" : (p.CapacityPressurePct >= 10 ? "badge-orange" : "badge-green");
    const statusText = p.CapacityPressurePct >= 20 ? "Acute Strain" : (p.CapacityPressurePct >= 10 ? "Peak Sensitive" : "Comfortable Buffer");

    tr.innerHTML = `
      <td><span class="drill-link" onclick="drillToProperty('${p.PropertyCode}')">${p.PropertyCode}</span></td>
      <td>${p.PropertyName}</td>
      <td>${p.City}</td>
      <td>${p.FacilityTypeName || 'Office'}</td>
      <td>${p.CapacitySeats}</td>
      <td>${Number(p.AverageUtilizationPct).toFixed(1)}%</td>
      <td><strong>${Number(p.PeakUtilizationPct).toFixed(1)}%</strong></td>
      <td>${Math.round(p.DaysUnderPressure || 0)} days</td>
      <td>${Number(p.CapacityPressurePct).toFixed(1)}%</td>
      <td><span class="badge ${statusClass}">${statusText}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// Render Page 4: Cost & Efficiency
function renderPage4(pressure) {
  // Cost vs Util Scatter Plot
  document.getElementById("chart-p4-scatter").innerHTML = createCostScatterSVG(pressure);

  // Cost breakdown
  const countryCosts = {};
  pressure.forEach(p => {
    if (!countryCosts[p.Country]) countryCosts[p.Country] = 0;
    countryCosts[p.Country] += Number(p.AnnualOperatingCostINR);
  });
  const dataCosts = Object.entries(countryCosts).map(([k, v]) => ({
    country: k,
    costCr: Math.round(v / 1e7)
  })).sort((a, b) => b.costCr - a.costCr);

  document.getElementById("chart-p4-cost-breakdown").innerHTML = createBarChartSVG(dataCosts, "country", "costCr", "₹ Cr", "#E07A5F");

  // Cost efficiency table
  const tbody = document.querySelector("#table-p4-cost-table tbody");
  tbody.innerHTML = "";
  pressure.slice().sort((a, b) => b.AnnualCostPerOccupiedSeatINR - a.AnnualCostPerOccupiedSeatINR).forEach(p => {
    const costSeat = Number(p.AnnualCostPerSeatINR);
    const costOcc = Number(p.AnnualCostPerOccupiedSeatINR);
    const premium = costOcc - costSeat;
    const mult = ((premium / costSeat) * 100).toFixed(0);

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="drill-link" onclick="drillToProperty('${p.PropertyCode}')">${p.PropertyCode}</span></td>
      <td>${p.PropertyName}</td>
      <td>${p.City}</td>
      <td>₹${(Number(p.AnnualOperatingCostINR) / 1e7).toFixed(1)} Cr</td>
      <td>₹${Math.round(Number(p.AnnualCostPerSqMINR)).toLocaleString()}</td>
      <td>₹${Math.round(costSeat).toLocaleString()}</td>
      <td><strong>₹${Math.round(costOcc).toLocaleString()}</strong></td>
      <td>₹${Math.round(premium).toLocaleString()}</td>
      <td><span class="badge ${mult > 100 ? 'badge-red' : 'badge-orange'}">+${mult}%</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// Render Page 5: Lease & Management Attention
function renderPage5(attention, leases) {
  // Lease Horizon Bars
  const byHorizon = {};
  leases.forEach(l => {
    const h = l.ExpiryHorizonCategory;
    if (!byHorizon[h]) byHorizon[h] = 0;
    byHorizon[h] += 1;
  });
  const horizonOrder = ["Expiring <= 6M", "Expiring 6-12M", "Expiring 12-24M", "Horizon > 24M", "Owned"];
  const hData = horizonOrder.map(h => ({
    horizon: h,
    count: byHorizon[h] || 0
  }));

  document.getElementById("chart-p5-lease-bars").innerHTML = createBarChartSVG(hData, "horizon", "count", "leases", "#C0392B");

  // Driver breakdown
  const byDriver = {};
  attention.forEach(a => {
    const d = a.PrimaryAttentionDriver;
    if (!byDriver[d]) byDriver[d] = 0;
    byDriver[d] += 1;
  });
  const driverData = Object.entries(byDriver).map(([k, v]) => ({
    driver: k,
    count: v
  })).sort((a, b) => b.count - a.count);

  document.getElementById("chart-p5-drivers").innerHTML = createBarChartSVG(driverData, "driver", "count", "assets", "#1F4E79");

  // Full Management Attention Table
  const tbody = document.querySelector("#table-p5-attention tbody");
  tbody.innerHTML = "";
  attention.forEach(a => {
    const tr = document.createElement("tr");
    const tierBadge = a.AttentionTier === "Immediate Attention" ? "badge-red" : (a.AttentionTier === "Elevated Priority" ? "badge-orange" : "badge-green");

    tr.innerHTML = `
      <td><strong>#${a.AttentionRank}</strong></td>
      <td><span class="drill-link" onclick="drillToProperty('${a.PropertyCode}')">${a.PropertyCode}</span></td>
      <td>${a.PropertyName}</td>
      <td>${a.City}</td>
      <td>${Number(a.AverageUtilizationPct).toFixed(1)}%</td>
      <td>${Number(a.PeakUtilizationPct).toFixed(1)}%</td>
      <td>₹${Math.round(Number(a.AnnualCostPerOccupiedSeatINR)).toLocaleString()}</td>
      <td>${a.ExpiryHorizonCategory}</td>
      <td><strong>${Number(a.PortfolioAttentionIndex).toFixed(1)}</strong></td>
      <td>${a.PrimaryAttentionDriver}</td>
      <td><span class="badge ${tierBadge}">${a.AttentionTier}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// Render Page 6: Data Quality & Controls
function renderPage6() {
  const dq = rawData.data_quality;

  // Rules breakdown
  const byRule = {};
  const bySev = {};
  dq.forEach(item => {
    byRule[item.RuleID] = (byRule[item.RuleID] || 0) + 1;
    bySev[item.Severity] = (bySev[item.Severity] || 0) + 1;
  });

  const ruleData = Object.entries(byRule).map(([k, v]) => ({ rule: k, count: v })).sort((a, b) => b.count - a.count);
  const sevData = Object.entries(bySev).map(([k, v]) => ({ severity: k, count: v }));

  document.getElementById("chart-p6-rules").innerHTML = createBarChartSVG(ruleData, "rule", "count", "issues", "#E67E22");
  document.getElementById("chart-p6-severity").innerHTML = createBarChartSVG(sevData, "severity", "count", "issues", "#C0392B");

  // Ledger Table
  const tbody = document.querySelector("#table-p6-ledger tbody");
  tbody.innerHTML = "";
  dq.forEach(d => {
    const tr = document.createElement("tr");
    const sevBadge = d.Severity === "Critical" ? "badge-red" : (d.Severity === "High" ? "badge-orange" : "badge-blue");

    tr.innerHTML = `
      <td><strong>${d.IssueID}</strong></td>
      <td>${d.RuleID}</td>
      <td><code>${d.TableName}</code></td>
      <td>${d.RecordIdentifier}</td>
      <td><span class="badge ${sevBadge}">${d.Severity}</span></td>
      <td>${d.ExpectedRule}</td>
      <td><span style="color:#C0392B; text-decoration: line-through;">${d.InjectedValue || 'NULL'}</span></td>
      <td><span style="color:#2E7D32; font-weight:600;">${d.CorrectedValue}</span></td>
      <td><span class="badge badge-green">${d.RemediationStatus}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// Drill-Through to Property Detail Page
window.drillToProperty = function(propertyCode) {
  document.getElementById("property-selector").value = propertyCode;
  renderPropertyDetail(propertyCode);
  const detailTab = document.getElementById("tab-property-detail");
  if (detailTab) detailTab.click();
};

function renderPropertyDetail(propertyCode) {
  const prop = rawData.properties.find(p => p.PropertyCode === propertyCode) || rawData.properties[0];
  const geo = rawData.geography.find(g => g.GeographyKey === prop.GeographyKey) || {};
  const ft = rawData.facility_types.find(f => f.FacilityTypeKey === prop.FacilityTypeKey) || {};
  const lease = rawData.leases.find(l => l.PropertyKey === prop.PropertyKey) || {};
  const pressure = rawData.pressure_matrix.find(p => p.PropertyKey === prop.PropertyKey) || {};
  const attention = rawData.attention_index.find(a => a.PropertyKey === prop.PropertyKey) || {};

  document.getElementById("prop-banner-name").textContent = prop.PropertyName;
  document.getElementById("prop-banner-meta").textContent =
    `${prop.PropertyCode} | ${geo.City}, ${geo.Country} | ${ft.FacilityTypeName} | ${prop.OwnershipType} | Opened ${prop.OpeningYear}`;
  document.getElementById("prop-banner-rank").textContent = `#${attention.AttentionRank || 1}`;
  document.getElementById("prop-banner-tier").textContent = attention.AttentionTier || "Review";

  document.getElementById("detail-usable").textContent = `${Math.round(prop.UsableAreaSqM).toLocaleString()} m²`;
  document.getElementById("detail-rentable").textContent = `Rentable: ${Math.round(prop.RentableAreaSqM).toLocaleString()} m²`;
  document.getElementById("detail-seats").textContent = `${prop.CapacitySeats.toLocaleString()} seats`;
  document.getElementById("detail-density").textContent = `${(prop.UsableAreaSqM / prop.CapacitySeats).toFixed(1)} m²/seat`;
  document.getElementById("detail-hc").textContent = `${prop.AssignedHeadcount.toLocaleString()} staff`;
  document.getElementById("detail-sharing").textContent = `Sharing: ${(prop.AssignedHeadcount / prop.CapacitySeats).toFixed(2)}:1`;

  document.getElementById("detail-util").textContent = `${Number(pressure.AverageUtilizationPct || 60).toFixed(1)}%`;
  document.getElementById("detail-presence").textContent = `Avg Presence: ${Math.round(pressure.AverageDailyPresence || 0)}/day`;
  document.getElementById("detail-peak").textContent = `${Number(pressure.PeakUtilizationPct || 80).toFixed(1)}%`;

  const annCost = Number(pressure.AnnualOperatingCostINR || 0);
  document.getElementById("detail-cost").textContent = `₹${(annCost / 1e7).toFixed(1)} Cr`;
  document.getElementById("detail-cost-occ").textContent = `₹${Math.round(Number(pressure.AnnualCostPerOccupiedSeatINR || 0)).toLocaleString()}`;

  document.getElementById("detail-lease-date").textContent = lease.LeaseEndDate || 'Freehold (Owned)';
  document.getElementById("detail-lease-horizon").textContent = lease.ExpiryHorizonCategory || 'Active';

  // Floor breakdown
  const propFloors = rawData.floors.filter(f => f.PropertyKey === prop.PropertyKey);
  const tbodyFloors = document.querySelector("#table-detail-floors tbody");
  tbodyFloors.innerHTML = "";
  propFloors.forEach(fl => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>L${fl.FloorNumber}</strong></td>
      <td>${fl.FloorName}</td>
      <td>${Math.round(fl.UsableAreaSqM).toLocaleString()}</td>
      <td>${fl.CapacitySeats}</td>
      <td>${(fl.UsableAreaSqM / fl.CapacitySeats).toFixed(1)} m²/seat</td>
    `;
    tbodyFloors.appendChild(tr);
  });

  // History trend SVG
  const propMonthly = rawData.monthly_summary.filter(m => m.PropertyKey === prop.PropertyKey);
  const histData = propMonthly.map(m => ({
    month: String(m.MonthDateKey).substring(0, 6),
    utilPct: Math.round(Number(m.AverageUtilizationRate) * 1000) / 10
  })).sort((a, b) => a.month.localeCompare(b.month));

  document.getElementById("chart-detail-history").innerHTML = createLineChartSVG(histData, "month", "utilPct", "%", "#1F4E79");
}

// -------------------------------------------------------------
// SVG Visualization Generators
// -------------------------------------------------------------

function createBarChartSVG(data, keyField, valField, unit, color) {
  if (!data || !data.length) return "<p style='color:#888; font-size:12px;'>No records in current selection.</p>";

  const width = 600;
  const height = 230;
  const padding = { top: 20, right: 30, bottom: 40, left: 60 };
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;

  const maxVal = Math.max(...data.map(d => d[valField]), 1);
  const barWidth = Math.min(42, Math.max(16, innerW / data.length - 8));

  let bars = "";
  data.forEach((d, idx) => {
    const h = (d[valField] / maxVal) * innerH;
    const x = padding.left + idx * (innerW / data.length) + ((innerW / data.length) - barWidth) / 2;
    const y = padding.top + innerH - h;
    const label = d[keyField].length > 12 ? d[keyField].substring(0, 10) + ".." : d[keyField];

    bars += `
      <rect class="svg-bar" x="${x}" y="${y}" width="${barWidth}" height="${h}" fill="${color}" rx="3">
        <title>${d[keyField]}: ${d[valField]} ${unit}</title>
      </rect>
      <text x="${x + barWidth/2}" y="${y - 4}" font-size="10" font-weight="600" fill="#333" text-anchor="middle">${d[valField]}</text>
      <text x="${x + barWidth/2}" y="${height - 12}" font-size="10" fill="#666" text-anchor="middle">${label}</text>
    `;
  });

  return `
    <svg viewBox="0 0 ${width} ${height}" style="width:100%; height:auto;">
      <line x1="${padding.left}" y1="${padding.top + innerH}" x2="${width - padding.right}" y2="${padding.top + innerH}" stroke="#CBD5E0" stroke-width="1"/>
      ${bars}
    </svg>
  `;
}

function createLineChartSVG(data, keyField, valField, unit, color) {
  if (!data || !data.length) return "<p style='color:#888; font-size:12px;'>No records.</p>";

  const width = 600;
  const height = 230;
  const padding = { top: 20, right: 30, bottom: 40, left: 50 };
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;

  const maxVal = Math.max(...data.map(d => d[valField]), 100);
  const minVal = Math.min(...data.map(d => d[valField]), 0);

  const points = data.map((d, idx) => {
    const x = padding.left + (idx / (data.length - 1)) * innerW;
    const y = padding.top + innerH - ((d[valField] - minVal) / (maxVal - minVal)) * innerH;
    return { x, y, val: d[valField], label: d[keyField] };
  });

  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(" ");

  let circles = "";
  points.forEach((p, idx) => {
    if (idx % 3 === 0 || idx === points.length - 1) {
      circles += `
        <circle cx="${p.x}" cy="${p.y}" r="3.5" fill="${color}">
          <title>${p.label}: ${p.val}${unit}</title>
        </circle>
        <text x="${p.x}" y="${height - 12}" font-size="9" fill="#718096" text-anchor="middle">${p.label}</text>
      `;
    }
  });

  return `
    <svg viewBox="0 0 ${width} ${height}" style="width:100%; height:auto;">
      <line x1="${padding.left}" y1="${padding.top + innerH}" x2="${width - padding.right}" y2="${padding.top + innerH}" stroke="#CBD5E0" stroke-width="1"/>
      <path d="${pathD}" fill="none" stroke="${color}" stroke-width="2.5"/>
      ${circles}
    </svg>
  `;
}

function createPressureMatrixSVG(pressure) {
  const width = 600;
  const height = 300;
  const padding = { top: 25, right: 30, bottom: 45, left: 50 };
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;

  // X-scale: 20 to 80% (Midpoint 55%)
  // Y-scale: 50 to 100% (Midpoint 80%)
  const xMid = padding.left + ((55 - 20) / (80 - 20)) * innerW;
  const yMid = padding.top + innerH - ((80 - 50) / (100 - 50)) * innerH;

  let points = "";
  const quadColors = {
    "Underutilized": "#4A90E2",
    "Peak-sensitive": "#E67E22",
    "Consistently active": "#2E7D32",
    "Capacity-constrained": "#C0392B"
  };

  pressure.forEach(p => {
    const x = padding.left + ((p.AverageUtilizationPct - 20) / 60) * innerW;
    const y = padding.top + innerH - ((p.PeakUtilizationPct - 50) / 50) * innerH;
    const col = quadColors[p.PressureQuadrant] || "#1F4E79";

    points += `
      <circle class="svg-scatter-point" cx="${x}" cy="${y}" r="6" fill="${col}" opacity="0.85" stroke="#222" stroke-width="0.8">
        <title>${p.PropertyCode} (${p.City}): Avg ${Number(p.AverageUtilizationPct).toFixed(1)}%, Peak ${Number(p.PeakUtilizationPct).toFixed(1)}% - ${p.PressureQuadrant}</title>
      </circle>
      <text x="${x + 7}" y="${y + 3}" font-size="9" font-weight="600" fill="#333">${p.PropertyCode.replace('PROP-','')}</text>
    `;
  });

  return `
    <svg viewBox="0 0 ${width} ${height}" style="width:100%; height:auto;">
      <!-- Quadrant Lines -->
      <line x1="${xMid}" y1="${padding.top}" x2="${xMid}" y2="${padding.top + innerH}" stroke="#A0AEC0" stroke-dasharray="3,3" stroke-width="1.2"/>
      <line x1="${padding.left}" y1="${yMid}" x2="${width - padding.right}" y2="${yMid}" stroke="#A0AEC0" stroke-dasharray="3,3" stroke-width="1.2"/>
      
      <!-- Quadrant Labels -->
      <text x="${padding.left + 15}" y="${padding.top + 20}" font-size="9" fill="#E67E22" font-weight="bold">PEAK-SENSITIVE</text>
      <text x="${width - padding.right - 15}" y="${padding.top + 20}" font-size="9" fill="#C0392B" font-weight="bold" text-anchor="end">CAPACITY-CONSTRAINED</text>
      <text x="${padding.left + 15}" y="${padding.top + innerH - 15}" font-size="9" fill="#4A90E2" font-weight="bold">UNDERUTILIZED</text>
      <text x="${width - padding.right - 15}" y="${padding.top + innerH - 15}" font-size="9" fill="#2E7D32" font-weight="bold" text-anchor="end">CONSISTENTLY ACTIVE</text>
      
      <!-- Axis Lines -->
      <line x1="${padding.left}" y1="${padding.top + innerH}" x2="${width - padding.right}" y2="${padding.top + innerH}" stroke="#718096" stroke-width="1.5"/>
      <line x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${padding.top + innerH}" stroke="#718096" stroke-width="1.5"/>
      
      <text x="${width / 2}" y="${height - 10}" font-size="10" font-weight="600" fill="#4A5568" text-anchor="middle">Average Daily Workplace Utilization (%)</text>
      <text x="18" y="${height / 2}" font-size="10" font-weight="600" fill="#4A5568" text-anchor="middle" transform="rotate(-90 18 ${height / 2})">Peak Workplace Utilization (%)</text>
      
      ${points}
    </svg>
  `;
}

function createGroupedBarSVG(data) {
  const width = 600;
  const height = 220;
  const padding = { top: 20, right: 30, bottom: 35, left: 45 };
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;

  let bars = "";
  const groupW = innerW / data.length;
  const bW = 18;

  data.forEach((d, idx) => {
    const xGroup = padding.left + idx * groupW + (groupW - bW * 2 - 4) / 2;
    const h1 = (d.util / 100) * innerH;
    const h2 = (d.peak / 100) * innerH;
    const y1 = padding.top + innerH - h1;
    const y2 = padding.top + innerH - h2;

    bars += `
      <rect x="${xGroup}" y="${y1}" width="${bW}" height="${h1}" fill="#1F4E79" rx="2">
        <title>${d.day} Avg: ${d.util}%</title>
      </rect>
      <rect x="${xGroup + bW + 4}" y="${y2}" width="${bW}" height="${h2}" fill="#E07A5F" rx="2">
        <title>${d.day} Peak: ${d.peak}%</title>
      </rect>
      <text x="${xGroup + bW}" y="${height - 10}" font-size="10" fill="#4A5568" text-anchor="middle">${d.day.substring(0,3)}</text>
    `;
  });

  return `
    <svg viewBox="0 0 ${width} ${height}" style="width:100%; height:auto;">
      <line x1="${padding.left}" y1="${padding.top + innerH}" x2="${width - padding.right}" y2="${padding.top + innerH}" stroke="#CBD5E0" stroke-width="1"/>
      <line x1="${padding.left}" y1="${padding.top + innerH - (0.85 * innerH)}" x2="${width - padding.right}" y2="${padding.top + innerH - (0.85 * innerH)}" stroke="#C0392B" stroke-dasharray="3,3" stroke-width="1"/>
      ${bars}
    </svg>
  `;
}

function createCostScatterSVG(pressure) {
  const width = 600;
  const height = 250;
  const padding = { top: 20, right: 30, bottom: 40, left: 60 };
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;

  let points = "";
  const maxCost = 2500000; // 2.5M INR

  pressure.forEach(p => {
    const x = padding.left + ((p.AverageUtilizationPct - 30) / 50) * innerW;
    const costOcc = Number(p.AnnualCostPerOccupiedSeatINR);
    const y = padding.top + innerH - (costOcc / maxCost) * innerH;
    const col = p.Region === "India" ? "#1F4E79" : "#E07A5F";

    points += `
      <circle class="svg-scatter-point" cx="${x}" cy="${y}" r="6" fill="${col}" opacity="0.85" stroke="#222" stroke-width="0.8">
        <title>${p.PropertyName} (${p.City}): ₹${Math.round(costOcc).toLocaleString()} / seat, Util: ${Number(p.AverageUtilizationPct).toFixed(1)}%</title>
      </circle>
    `;
  });

  return `
    <svg viewBox="0 0 ${width} ${height}" style="width:100%; height:auto;">
      <line x1="${padding.left}" y1="${padding.top + innerH}" x2="${width - padding.right}" y2="${padding.top + innerH}" stroke="#718096" stroke-width="1"/>
      <line x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${padding.top + innerH}" stroke="#718096" stroke-width="1"/>
      <text x="${width / 2}" y="${height - 8}" font-size="10" fill="#4A5568" text-anchor="middle">Average Workplace Utilization (%)</text>
      <text x="18" y="${height / 2}" font-size="10" fill="#4A5568" text-anchor="middle" transform="rotate(-90 18 ${height / 2})">Cost per Occupied Seat (₹)</text>
      ${points}
    </svg>
  `;
}
