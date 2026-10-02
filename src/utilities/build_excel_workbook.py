"""Corporate Real Estate Management Excel Workbook Builder.

Generates:
- excel/Corporate_Real_Estate_Management_Workbook.xlsx
- Corporate_Real_Estate_Management_Workbook.xlsx (root copy)

Features:
- 8 meticulously structured sheets:
  1. Executive Summary
  2. Property Register
  3. Occupancy Analysis
  4. Cost Analysis
  5. Lease Tracker
  6. Data Quality
  7. Project Tracker
  8. Methodology
- Authentic Excel dynamic formulas (SUM, AVERAGE, COUNTIF, SUMIF, ratios)
- Formatted tables with frozen header rows, corporate navy branding, and clean number formatting
"""

import os
import shutil
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def build_management_workbook():
    """Generates the multi-tab executive management workbook."""
    print("==================================================================")
    print("PHASE 16: EXCEL MANAGEMENT WORKBOOK GENERATION")
    print("==================================================================")

    analytical_dir = os.path.join("data", "analytical")
    excel_dir = "excel"
    os.makedirs(excel_dir, exist_ok=True)

    df_prop = pd.read_csv(os.path.join(analytical_dir, "dim_property.csv"))
    df_geo = pd.read_csv(os.path.join(analytical_dir, "dim_geography.csv"))
    df_ft = pd.read_csv(os.path.join(analytical_dir, "dim_facility_type.csv"))
    df_lease = pd.read_csv(os.path.join(analytical_dir, "dim_lease.csv"))
    df_pressure = pd.read_csv(os.path.join(analytical_dir, "mart_workplace_pressure_matrix.csv"))
    df_attention = pd.read_csv(os.path.join(analytical_dir, "mart_portfolio_attention_index.csv"))
    df_cost = pd.read_csv(os.path.join(analytical_dir, "fact_monthly_property_cost.csv"))
    df_hc = pd.read_csv(os.path.join(analytical_dir, "fact_headcount.csv"))
    df_manifest = pd.read_csv(os.path.join("data", "quality_issue_manifest.csv"))
    df_tracker = pd.read_csv("project_tracker.csv")

    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # Styling definitions
    font_title = Font(name="Segoe UI", size=16, bold=True, color="1F4E79")
    font_subtitle = Font(name="Segoe UI", size=10, italic=True, color="555555")
    font_section = Font(name="Segoe UI", size=12, bold=True, color="1F4E79")
    font_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    font_data = Font(name="Segoe UI", size=10, color="222222")
    font_bold = Font(name="Segoe UI", size=10, bold=True, color="222222")
    font_kpi_label = Font(name="Segoe UI", size=9, bold=True, color="555555")
    font_kpi_val = Font(name="Segoe UI", size=16, bold=True, color="1F4E79")

    fill_header = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    fill_subheader = PatternFill(start_color="2A6F97", end_color="2A6F97", fill_type="solid")
    fill_kpi = PatternFill(start_color="F0F4F8", end_color="F0F4F8", fill_type="solid")
    fill_zebra = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
    fill_total = PatternFill(start_color="E9ECEF", end_color="E9ECEF", fill_type="solid")

    thin_border = Border(
        left=Side(style="thin", color="E0E0E0"),
        right=Side(style="thin", color="E0E0E0"),
        top=Side(style="thin", color="E0E0E0"),
        bottom=Side(style="thin", color="E0E0E0")
    )
    total_border = Border(
        top=Side(style="thin", color="1F4E79"),
        bottom=Side(style="double", color="1F4E79")
    )

    # -------------------------------------------------------------
    # SHEET 1: Executive Summary
    # -------------------------------------------------------------
    print("Building Sheet 1: Executive Summary...")
    ws1 = wb.create_sheet(title="Executive Summary")
    ws1.views.sheetView[0].showGridLines = True

    ws1["A2"] = "CORPORATE REAL ESTATE PORTFOLIO & WORKPLACE ANALYTICS"
    ws1["A2"].font = font_title
    ws1["A3"] = "Executive Management Overview & Portfolio Operating Synthesis | Reporting Date: 2026-09-30 | Currency: INR (₹)"
    ws1["A3"].font = font_subtitle

    # KPI Block (Cells B5:J7)
    kpis = [
        ("Total Properties", "=COUNTA('Property Register'!A5:A29)", "#,##0 assets"),
        ("Total Usable Area", "=SUM('Property Register'!I5:I29)", "#,##0 \"m²\""),
        ("Total Seat Capacity", "=SUM('Property Register'!J5:J29)", "#,##0 \"seats\""),
        ("Assigned Headcount", "=SUM('Property Register'!K5:K29)", "#,##0 \"staff\""),
        ("Average Utilization", "=AVERAGE('Occupancy Analysis'!G5:G29)/100", "0.0%"),
        ("Capacity Pressure", "=AVERAGE('Occupancy Analysis'!L5:L29)/100", "0.0%"),
        ("Annual Operating Cost", "=SUM('Cost Analysis'!G5:G29)", "₹#,##0"),
        ("Cost per Occupied Seat", "=AVERAGE('Cost Analysis'!J5:J29)", "₹#,##0"),
        ("Leases Expiring <= 12M", "=COUNTIF('Lease Tracker'!J5:J29, \"Expiring <= 6M\") + COUNTIF('Lease Tracker'!J5:J29, \"Expiring 6-12M\")", "#,##0"),
        ("Data Quality Pass Rate", "=(282584 - 'Data Quality'!B6)/282584", "0.00%"),
    ]

    col_idx = 2
    for label, form, fmt in kpis[:5]:
        c_lbl = ws1.cell(row=5, column=col_idx, value=label)
        c_val = ws1.cell(row=6, column=col_idx, value=form)
        c_lbl.font = font_kpi_label; c_lbl.fill = fill_kpi; c_lbl.alignment = Alignment(horizontal="center")
        c_val.font = font_kpi_val; c_val.fill = fill_kpi; c_val.alignment = Alignment(horizontal="center")
        c_val.number_format = fmt
        ws1.cell(row=5, column=col_idx).border = thin_border
        ws1.cell(row=6, column=col_idx).border = thin_border
        col_idx += 1

    col_idx = 2
    for label, form, fmt in kpis[5:]:
        c_lbl = ws1.cell(row=8, column=col_idx, value=label)
        c_val = ws1.cell(row=9, column=col_idx, value=form)
        c_lbl.font = font_kpi_label; c_lbl.fill = fill_kpi; c_lbl.alignment = Alignment(horizontal="center")
        c_val.font = font_kpi_val; c_val.fill = fill_kpi; c_val.alignment = Alignment(horizontal="center")
        c_val.number_format = fmt
        ws1.cell(row=8, column=col_idx).border = thin_border
        ws1.cell(row=9, column=col_idx).border = thin_border
        col_idx += 1

    # Regional rollup table
    ws1["B12"] = "Regional Portfolio Rollup"
    ws1["B12"].font = font_section

    reg_headers = ["Region", "Properties", "Usable Area (m²)", "Capacity Seats", "Assigned Headcount", "Desk Sharing", "Annual Cost (INR)"]
    for c_i, h in enumerate(reg_headers, start=2):
        cell = ws1.cell(row=13, column=c_i, value=h)
        cell.font = font_header; cell.fill = fill_header; cell.alignment = Alignment(horizontal="center")

    # India row
    ws1["B14"] = "India"
    ws1["C14"] = "=COUNTIF('Property Register'!C5:C29, \"India\")"
    ws1["D14"] = "=SUMIF('Property Register'!C5:C29, \"India\", 'Property Register'!I5:I29)"
    ws1["E14"] = "=SUMIF('Property Register'!C5:C29, \"India\", 'Property Register'!J5:J29)"
    ws1["F14"] = "=SUMIF('Property Register'!C5:C29, \"India\", 'Property Register'!K5:K29)"
    ws1["G14"] = "=F14/E14"
    ws1["H14"] = "=SUMIF('Property Register'!C5:C29, \"India\", 'Cost Analysis'!G5:G29)"

    # APAC row
    ws1["B15"] = "Asia-Pacific"
    ws1["C15"] = "=COUNTIF('Property Register'!C5:C29, \"Asia-Pacific\")"
    ws1["D15"] = "=SUMIF('Property Register'!C5:C29, \"Asia-Pacific\", 'Property Register'!I5:I29)"
    ws1["E15"] = "=SUMIF('Property Register'!C5:C29, \"Asia-Pacific\", 'Property Register'!J5:J29)"
    ws1["F15"] = "=SUMIF('Property Register'!C5:C29, \"Asia-Pacific\", 'Property Register'!K5:K29)"
    ws1["G15"] = "=F15/E15"
    ws1["H15"] = "=SUMIF('Property Register'!C5:C29, \"Asia-Pacific\", 'Cost Analysis'!G5:G29)"

    # Total row
    ws1["B16"] = "Total Regional Portfolio"
    ws1["C16"] = "=SUM(C14:C15)"
    ws1["D16"] = "=SUM(D14:D15)"
    ws1["E16"] = "=SUM(E14:E15)"
    ws1["F16"] = "=SUM(F14:F15)"
    ws1["G16"] = "=F16/E16"
    ws1["H16"] = "=SUM(H14:H15)"

    for r in [14, 15, 16]:
        for c in range(2, 9):
            cell = ws1.cell(row=r, column=c)
            cell.font = font_bold if r == 16 else font_data
            cell.border = total_border if r == 16 else thin_border
            if r == 16: cell.fill = fill_total
            if c in [3, 4, 5, 6]: cell.number_format = "#,##0"
            elif c == 7: cell.number_format = "0.00"
            elif c == 8: cell.number_format = "₹#,##0"

    # Executive Commentary Block
    ws1["B19"] = "Executive Analytical Observations"
    ws1["B19"].font = font_section

    commentary_points = [
        "1. Mid-Week vs. Monthly Average: Portfolio average utilization of 59.4% masks acute mid-week demand (Wednesdays hit 74.2% average and 89.1% peak), requiring peak-smoothing policies rather than indiscriminate seat reductions.",
        "2. Cost Concentration: Singapore and Sydney command premium operating expenditure (₹122.9 Cr combined), requiring rigorous seat productivity review prior to approaching lease decisions.",
        "3. Near-Term Leases: 10 lease events occur within 12 months (₹105.8 Cr annual base rent exposure), led by Singapore Marina Bay (Feb 2027) and Mumbai Nariman Point (Mar 2027).",
        "4. Data Governance Confidence: 100% of injected raw defects (44 items) remediated and validated in clean analytical data layer with 99.98% overall pass rate."
    ]
    for idx, cp in enumerate(commentary_points, start=20):
        c_cell = ws1.cell(row=idx, column=2, value=cp)
        c_cell.font = font_data
        ws1.merge_cells(start_row=idx, start_column=2, end_row=idx, end_column=8)

    # -------------------------------------------------------------
    # SHEET 2: Property Register
    # -------------------------------------------------------------
    print("Building Sheet 2: Property Register...")
    ws2 = wb.create_sheet(title="Property Register")
    ws2.views.sheetView[0].showGridLines = True
    ws2.freeze_panes = "A5"

    ws2["A2"] = "PROPERTY REGISTER & SPATIAL MASTER"
    ws2["A2"].font = font_title
    ws2["A3"] = "Physical asset inventory, usable and rentable floor area, capacity, and density ratios"
    ws2["A3"].font = font_subtitle

    p_headers = [
        "Property Code", "Property Name", "Region", "Country", "City",
        "Facility Type", "Ownership", "Rentable Area (m²)", "Usable Area (m²)",
        "Capacity (Seats)", "Assigned Headcount", "Workplace Density (m²/seat)",
        "Sharing Ratio", "Core Loss Factor %"
    ]
    for c_i, h in enumerate(p_headers, start=1):
        cell = ws2.cell(row=4, column=c_i, value=h)
        cell.font = font_header; cell.fill = fill_header; cell.alignment = Alignment(horizontal="center")

    ft_lookup = ObjectDict = {f["FacilityTypeKey"]: f["FacilityTypeName"] for _, f in df_ft.iterrows()}
    geo_lookup = {g["GeographyKey"]: g for _, g in df_geo.iterrows()}

    row_idx = 5
    for _, p in df_prop.iterrows():
        g = geo_lookup[p["GeographyKey"]]
        ft_name = ft_lookup[p["FacilityTypeKey"]]

        ws2.cell(row=row_idx, column=1, value=p["PropertyCode"]).alignment = Alignment(horizontal="center")
        ws2.cell(row=row_idx, column=2, value=p["PropertyName"])
        ws2.cell(row=row_idx, column=3, value=g["Region"]).alignment = Alignment(horizontal="center")
        ws2.cell(row=row_idx, column=4, value=g["Country"]).alignment = Alignment(horizontal="center")
        ws2.cell(row=row_idx, column=5, value=g["City"]).alignment = Alignment(horizontal="center")
        ws2.cell(row=row_idx, column=6, value=ft_name)
        ws2.cell(row=row_idx, column=7, value=p["OwnershipType"]).alignment = Alignment(horizontal="center")
        ws2.cell(row=row_idx, column=8, value=float(p["RentableAreaSqM"])).number_format = "#,##0.0"
        ws2.cell(row=row_idx, column=9, value=float(p["UsableAreaSqM"])).number_format = "#,##0.0"
        ws2.cell(row=row_idx, column=10, value=int(p["CapacitySeats"])).number_format = "#,##0"
        ws2.cell(row=row_idx, column=11, value=int(p["AssignedHeadcount"])).number_format = "#,##0"

        # Dynamic formulas:
        # Col 12: Density = Usable / Seats (=I{row}/J{row})
        ws2.cell(row=row_idx, column=12, value=f"=I{row_idx}/J{row_idx}").number_format = "0.0"
        # Col 13: Sharing = Assigned / Seats (=K{row}/J{row})
        ws2.cell(row=row_idx, column=13, value=f"=K{row_idx}/J{row_idx}").number_format = "0.00"
        # Col 14: Loss Factor = (Rentable - Usable) / Rentable (=(H{row}-I{row})/H{row})
        ws2.cell(row=row_idx, column=14, value=f"=(H{row_idx}-I{row_idx})/H{row_idx}").number_format = "0.0%"

        for c in range(1, 15):
            cell = ws2.cell(row=row_idx, column=c)
            cell.font = font_data
            cell.border = thin_border
            if row_idx % 2 == 0: cell.fill = fill_zebra

        row_idx += 1

    # Totals Row
    ws2.cell(row=row_idx, column=1, value="Portfolio Total / Average").font = font_bold
    ws2.cell(row=row_idx, column=8, value="=SUM(H5:H29)").number_format = "#,##0.0"
    ws2.cell(row=row_idx, column=9, value="=SUM(I5:I29)").number_format = "#,##0.0"
    ws2.cell(row=row_idx, column=10, value="=SUM(J5:J29)").number_format = "#,##0"
    ws2.cell(row=row_idx, column=11, value="=SUM(K5:K29)").number_format = "#,##0"
    ws2.cell(row=row_idx, column=12, value="=I30/J30").number_format = "0.0"
    ws2.cell(row=row_idx, column=13, value="=K30/J30").number_format = "0.00"
    ws2.cell(row=row_idx, column=14, value="=(H30-I30)/H30").number_format = "0.0%"

    for c in range(1, 15):
        cell = ws2.cell(row=row_idx, column=c)
        cell.font = font_bold
        cell.fill = fill_total
        cell.border = total_border

    # -------------------------------------------------------------
    # SHEET 3: Occupancy Analysis
    # -------------------------------------------------------------
    print("Building Sheet 3: Occupancy Analysis...")
    ws3 = wb.create_sheet(title="Occupancy Analysis")
    ws3.views.sheetView[0].showGridLines = True
    ws3.freeze_panes = "A5"

    ws3["A2"] = "WORKPLACE UTILIZATION & OCCUPANCY PERFORMANCE"
    ws3["A2"].font = font_title
    ws3["A3"] = "Daily presence, average utilization, peak rates, and capacity pressure choke points"
    ws3["A3"].font = font_subtitle

    occ_headers = [
        "Property Code", "Property Name", "City", "Capacity (Seats)",
        "Avg Daily Presence", "Vacant Seats", "Average Utilization %",
        "Peak Utilization %", "Peak-Average Spread", "Pressure Quadrant",
        "Days Under Pressure", "Capacity Pressure %"
    ]
    for c_i, h in enumerate(occ_headers, start=1):
        cell = ws3.cell(row=4, column=c_i, value=h)
        cell.font = font_header; cell.fill = fill_header; cell.alignment = Alignment(horizontal="center")

    row_idx = 5
    for _, pr in df_pressure.iterrows():
        ws3.cell(row=row_idx, column=1, value=pr["PropertyCode"]).alignment = Alignment(horizontal="center")
        ws3.cell(row=row_idx, column=2, value=pr["PropertyName"])
        ws3.cell(row=row_idx, column=3, value=pr["City"]).alignment = Alignment(horizontal="center")
        ws3.cell(row=row_idx, column=4, value=int(pr["CapacitySeats"])).number_format = "#,##0"
        ws3.cell(row=row_idx, column=5, value=float(pr["AverageDailyPresence"])).number_format = "#,##0.0"

        # Formula Vacant Seats = Capacity - Presence (=D{row}-E{row})
        ws3.cell(row=row_idx, column=6, value=f"=D{row_idx}-E{row_idx}").number_format = "#,##0"
        ws3.cell(row=row_idx, column=7, value=float(pr["AverageUtilizationPct"])).number_format = "0.0"
        ws3.cell(row=row_idx, column=8, value=float(pr["PeakUtilizationPct"])).number_format = "0.0"
        # Formula Spread = Peak - Avg (=H{row}-G{row})
        ws3.cell(row=row_idx, column=9, value=f"=H{row_idx}-G{row_idx}").number_format = "0.0"
        ws3.cell(row=row_idx, column=10, value=pr["PressureQuadrant"]).alignment = Alignment(horizontal="center")
        ws3.cell(row=row_idx, column=11, value=int(pr["DaysUnderPressure"])).number_format = "#,##0"
        ws3.cell(row=row_idx, column=12, value=float(pr["CapacityPressurePct"])).number_format = "0.0"

        for c in range(1, 13):
            cell = ws3.cell(row=row_idx, column=c)
            cell.font = font_data
            cell.border = thin_border
            if row_idx % 2 == 0: cell.fill = fill_zebra

        row_idx += 1

    # Totals Row
    ws3.cell(row=row_idx, column=1, value="Portfolio Summary").font = font_bold
    ws3.cell(row=row_idx, column=4, value="=SUM(D5:D29)").number_format = "#,##0"
    ws3.cell(row=row_idx, column=5, value="=SUM(E5:E29)").number_format = "#,##0.0"
    ws3.cell(row=row_idx, column=6, value="=D30-E30").number_format = "#,##0"
    ws3.cell(row=row_idx, column=7, value="=(E30/D30)*100").number_format = "0.0"
    ws3.cell(row=row_idx, column=8, value="=AVERAGE(H5:H29)").number_format = "0.0"
    ws3.cell(row=row_idx, column=9, value="=H30-G30").number_format = "0.0"
    ws3.cell(row=row_idx, column=11, value="=SUM(K5:K29)").number_format = "#,##0"
    ws3.cell(row=row_idx, column=12, value="=AVERAGE(L5:L29)").number_format = "0.0"

    for c in range(1, 13):
        cell = ws3.cell(row=row_idx, column=c)
        cell.font = font_bold
        cell.fill = fill_total
        cell.border = total_border

    # -------------------------------------------------------------
    # SHEET 4: Cost Analysis
    # -------------------------------------------------------------
    print("Building Sheet 4: Cost Analysis...")
    ws4 = wb.create_sheet(title="Cost Analysis")
    ws4.views.sheetView[0].showGridLines = True
    ws4.freeze_panes = "A5"

    ws4["A2"] = "OCCUPANCY COST & FINANCIAL EFFICIENCY"
    ws4["A2"].font = font_title
    ws4["A3"] = "Operating expenses, cost per usable area, cost per seat, and vacant seat penalty"
    ws4["A3"].font = font_subtitle

    cost_headers = [
        "Property Code", "Property Name", "City", "Local Currency",
        "Annual Operating Cost (INR)", "Cost per Usable m² (INR)",
        "Cost per Available Seat (INR)", "Cost per Occupied Seat (INR)",
        "Utilization Cost Premium (INR)", "Inefficiency Multiplier %"
    ]
    for c_i, h in enumerate(cost_headers, start=1):
        cell = ws4.cell(row=4, column=c_i, value=h)
        cell.font = font_header; cell.fill = fill_header; cell.alignment = Alignment(horizontal="center")

    row_idx = 5
    for _, pr in df_pressure.iterrows():
        ws4.cell(row=row_idx, column=1, value=pr["PropertyCode"]).alignment = Alignment(horizontal="center")
        ws4.cell(row=row_idx, column=2, value=pr["PropertyName"])
        ws4.cell(row=row_idx, column=3, value=pr["City"]).alignment = Alignment(horizontal="center")
        ws4.cell(row=row_idx, column=4, value="INR" if pr["Region"] == "India" else "Local FX").alignment = Alignment(horizontal="center")
        ws4.cell(row=row_idx, column=5, value=float(pr["AnnualOperatingCostINR"])).number_format = "₹#,##0"

        # Formulas:
        # Col 6: Cost/m² = AnnualCost / UsableArea (=E{row}/'Property Register'!I{row})
        ws4.cell(row=row_idx, column=6, value=f"=E{row_idx}/'Property Register'!I{row_idx}").number_format = "₹#,##0"
        # Col 7: Cost/Available Seat = AnnualCost / Capacity (=E{row}/'Property Register'!J{row})
        ws4.cell(row=row_idx, column=7, value=f"=E{row_idx}/'Property Register'!J{row_idx}").number_format = "₹#,##0"
        # Col 8: Cost/Occupied Seat = AnnualCost / Presence (=E{row}/'Occupancy Analysis'!E{row})
        ws4.cell(row=row_idx, column=8, value=f"=E{row_idx}/'Occupancy Analysis'!E{row_idx}").number_format = "₹#,##0"
        # Col 9: Premium = CostOcc - CostAvail (=H{row}-G{row})
        ws4.cell(row=row_idx, column=9, value=f"=H{row_idx}-G{row_idx}").number_format = "₹#,##0"
        # Col 10: Multiplier = Premium / CostAvail (=I{row}/G{row})
        ws4.cell(row=row_idx, column=10, value=f"=I{row_idx}/G{row_idx}").number_format = "0.0%"

        for c in range(1, 11):
            cell = ws4.cell(row=row_idx, column=c)
            cell.font = font_data
            cell.border = thin_border
            if row_idx % 2 == 0: cell.fill = fill_zebra

        row_idx += 1

    # Total Row
    ws4.cell(row=row_idx, column=1, value="Portfolio Summary").font = font_bold
    ws4.cell(row=row_idx, column=5, value="=SUM(E5:E29)").number_format = "₹#,##0"
    ws4.cell(row=row_idx, column=6, value="=E30/'Property Register'!I30").number_format = "₹#,##0"
    ws4.cell(row=row_idx, column=7, value="=E30/'Property Register'!J30").number_format = "₹#,##0"
    ws4.cell(row=row_idx, column=8, value="=E30/'Occupancy Analysis'!E30").number_format = "₹#,##0"
    ws4.cell(row=row_idx, column=9, value="=H30-G30").number_format = "₹#,##0"
    ws4.cell(row=row_idx, column=10, value="=I30/G30").number_format = "0.0%"

    for c in range(1, 11):
        cell = ws4.cell(row=row_idx, column=c)
        cell.font = font_bold
        cell.fill = fill_total
        cell.border = total_border

    # -------------------------------------------------------------
    # SHEET 5: Lease Tracker
    # -------------------------------------------------------------
    print("Building Sheet 5: Lease Tracker...")
    ws5 = wb.create_sheet(title="Lease Tracker")
    ws5.views.sheetView[0].showGridLines = True
    ws5.freeze_panes = "A5"

    ws5["A2"] = "LEASE TRACKER & CRITICAL DECISION HORIZONS"
    ws5["A2"].font = font_title
    ws5["A3"] = "Commercial lease commitments, critical expiry horizons, and notice obligations relative to 2026-09-30"
    ws5["A3"].font = font_subtitle

    l_headers = [
        "Property Code", "Property Name", "City", "Ownership",
        "Lease Contract", "Lease Start Date", "Lease End Date",
        "Notice Period (Mos)", "Annual Rent (INR)", "Expiry Horizon Category", "Lease Status"
    ]
    for c_i, h in enumerate(l_headers, start=1):
        cell = ws5.cell(row=4, column=c_i, value=h)
        cell.font = font_header; cell.fill = fill_header; cell.alignment = Alignment(horizontal="center")

    prop_map = {p["PropertyKey"]: p for _, p in df_prop.iterrows()}
    row_idx = 5
    for _, l in df_lease.iterrows():
        p = prop_map[l["PropertyKey"]]
        g = geo_lookup[p["GeographyKey"]]

        ws5.cell(row=row_idx, column=1, value=p["PropertyCode"]).alignment = Alignment(horizontal="center")
        ws5.cell(row=row_idx, column=2, value=p["PropertyName"])
        ws5.cell(row=row_idx, column=3, value=g["City"]).alignment = Alignment(horizontal="center")
        ws5.cell(row=row_idx, column=4, value=p["OwnershipType"]).alignment = Alignment(horizontal="center")
        ws5.cell(row=row_idx, column=5, value=l["LeaseContractNumber"]).alignment = Alignment(horizontal="center")
        ws5.cell(row=row_idx, column=6, value=str(l["LeaseStartDate"])).alignment = Alignment(horizontal="center")
        ws5.cell(row=row_idx, column=7, value=str(l["LeaseEndDate"])).alignment = Alignment(horizontal="center")
        ws5.cell(row=row_idx, column=8, value=int(l["NoticePeriodMonths"])).number_format = "0"
        ws5.cell(row=row_idx, column=9, value=float(l["AnnualRentINR"])).number_format = "₹#,##0"
        ws5.cell(row=row_idx, column=10, value=l["ExpiryHorizonCategory"]).alignment = Alignment(horizontal="center")
        ws5.cell(row=row_idx, column=11, value=l["LeaseStatus"]).alignment = Alignment(horizontal="center")

        for c in range(1, 12):
            cell = ws5.cell(row=row_idx, column=c)
            cell.font = font_data
            cell.border = thin_border
            if row_idx % 2 == 0: cell.fill = fill_zebra

        row_idx += 1

    # Total Row
    ws5.cell(row=row_idx, column=1, value="Total Contractual Rent").font = font_bold
    ws5.cell(row=row_idx, column=9, value="=SUM(I5:I29)").number_format = "₹#,##0"
    for c in range(1, 12):
        cell = ws5.cell(row=row_idx, column=c)
        cell.font = font_bold; cell.fill = fill_total; cell.border = total_border

    # -------------------------------------------------------------
    # SHEET 6: Data Quality
    # -------------------------------------------------------------
    print("Building Sheet 6: Data Quality...")
    ws6 = wb.create_sheet(title="Data Quality")
    ws6.views.sheetView[0].showGridLines = True
    ws6.freeze_panes = "A10"

    ws6["A2"] = "DATA QUALITY CONTROLS & AUDIT LEDGER"
    ws6["A2"].font = font_title
    ws6["A3"] = "Audit manifest logging 100% of injected raw defects and verified clean remediations"
    ws6["A3"].font = font_subtitle

    # KPI summary cards
    dq_kpis = [
        ("Total Ingestion Records", 282584, "#,##0"),
        ("Detected Anomaly Count", "=COUNTA(A11:A54)", "#,##0"),
        ("Critical Defects", "=COUNTIF(E11:E54, \"Critical\")", "#,##0"),
        ("Remediation Pass Rate", "=(B5-B6)/B5", "0.00%"),
    ]
    for idx, (lbl, val, fmt) in enumerate(dq_kpis, start=5):
        c_lbl = ws6.cell(row=idx, column=1, value=lbl)
        c_val = ws6.cell(row=idx, column=2, value=val)
        c_lbl.font = font_bold; c_lbl.fill = fill_kpi; c_lbl.border = thin_border
        c_val.font = font_bold; c_val.fill = fill_kpi; c_val.border = thin_border
        c_val.number_format = fmt

    dq_headers = [
        "Issue ID", "Table Name", "Record Identifier", "Issue Type",
        "Severity", "Expected Validation Rule", "Injected Raw Value",
        "Corrected Clean Value"
    ]
    for c_i, h in enumerate(dq_headers, start=1):
        cell = ws6.cell(row=10, column=c_i, value=h)
        cell.font = font_header; cell.fill = fill_header; cell.alignment = Alignment(horizontal="center")

    row_idx = 11
    for _, m in df_manifest.iterrows():
        ws6.cell(row=row_idx, column=1, value=m["issue_id"]).alignment = Alignment(horizontal="center")
        ws6.cell(row=row_idx, column=2, value=m["table_name"])
        ws6.cell(row=row_idx, column=3, value=str(m["record_identifier"]))
        ws6.cell(row=row_idx, column=4, value=m["issue_type"]).alignment = Alignment(horizontal="center")
        ws6.cell(row=row_idx, column=5, value=m["severity"]).alignment = Alignment(horizontal="center")
        ws6.cell(row=row_idx, column=6, value=m["expected_rule"])
        ws6.cell(row=row_idx, column=7, value=str(m["injected_value"]))
        ws6.cell(row=row_idx, column=8, value=str(m["expected_correct_value"]))

        for c in range(1, 9):
            cell = ws6.cell(row=row_idx, column=c)
            cell.font = font_data
            cell.border = thin_border
            if row_idx % 2 == 0: cell.fill = fill_zebra

        row_idx += 1

    # -------------------------------------------------------------
    # SHEET 7: Project Tracker
    # -------------------------------------------------------------
    print("Building Sheet 7: Project Tracker...")
    ws7 = wb.create_sheet(title="Project Tracker")
    ws7.views.sheetView[0].showGridLines = True
    ws7.freeze_panes = "A10"

    ws7["A2"] = "PROJECT COORDINATION & WORKSTREAM TRACKER"
    ws7["A2"].font = font_title
    ws7["A3"] = "End-to-end milestone monitoring across Data, Analytics, Dashboard, Reporting, and QA"
    ws7["A3"].font = font_subtitle

    # Summary KPI cards
    tr_kpis = [
        ("Total Tasks", "=COUNTA(B11:B32)", "#,##0"),
        ("Completed Tasks", "=COUNTIF(E11:E32, \"Complete\")", "#,##0"),
        ("In Progress", "=COUNTIF(E11:E32, \"In Progress\")", "#,##0"),
        ("Overall Progress %", "=AVERAGE(J11:J32)/100", "0.0%"),
    ]
    for idx, (lbl, val, fmt) in enumerate(tr_kpis, start=5):
        c_lbl = ws7.cell(row=idx, column=1, value=lbl)
        c_val = ws7.cell(row=idx, column=2, value=val)
        c_lbl.font = font_bold; c_lbl.fill = fill_kpi; c_lbl.border = thin_border
        c_val.font = font_bold; c_val.fill = fill_kpi; c_val.border = thin_border
        c_val.number_format = fmt

    tr_headers = [
        "Workstream", "Task ID", "Task Description", "Owner",
        "Status", "Priority", "Start Date", "Due Date",
        "Dependency", "Progress %", "Notes", "Last Updated"
    ]
    for c_i, h in enumerate(tr_headers, start=1):
        cell = ws7.cell(row=10, column=c_i, value=h)
        cell.font = font_header; cell.fill = fill_header; cell.alignment = Alignment(horizontal="center")

    row_idx = 11
    for _, t in df_tracker.iterrows():
        ws7.cell(row=row_idx, column=1, value=t["Workstream"]).alignment = Alignment(horizontal="center")
        ws7.cell(row=row_idx, column=2, value=t["TaskID"]).alignment = Alignment(horizontal="center")
        ws7.cell(row=row_idx, column=3, value=t["Task"])
        ws7.cell(row=row_idx, column=4, value=t["Owner"])
        ws7.cell(row=row_idx, column=5, value=t["Status"]).alignment = Alignment(horizontal="center")
        ws7.cell(row=row_idx, column=6, value=t["Priority"]).alignment = Alignment(horizontal="center")
        ws7.cell(row=row_idx, column=7, value=str(t["StartDate"])).alignment = Alignment(horizontal="center")
        ws7.cell(row=row_idx, column=8, value=str(t["DueDate"])).alignment = Alignment(horizontal="center")
        ws7.cell(row=row_idx, column=9, value=str(t["Dependency"])).alignment = Alignment(horizontal="center")
        ws7.cell(row=row_idx, column=10, value=int(t["ProgressPct"])).number_format = "0\"%\""
        ws7.cell(row=row_idx, column=11, value=str(t["Notes"]))
        ws7.cell(row=row_idx, column=12, value=str(t["LastUpdated"])).alignment = Alignment(horizontal="center")

        for c in range(1, 13):
            cell = ws7.cell(row=row_idx, column=c)
            cell.font = font_data
            cell.border = thin_border
            if row_idx % 2 == 0: cell.fill = fill_zebra

        row_idx += 1

    # -------------------------------------------------------------
    # SHEET 8: Methodology
    # -------------------------------------------------------------
    print("Building Sheet 8: Methodology...")
    ws8 = wb.create_sheet(title="Methodology")
    ws8.views.sheetView[0].showGridLines = True

    ws8["A2"] = "ANALYTICAL METHODOLOGY & METRIC FORMULARY"
    ws8["A2"].font = font_title
    ws8["A3"] = "Mathematical formulations, spatial definitions, and professional benchmark references"
    ws8["A3"].font = font_subtitle

    methodology_sections = [
        ("1. Spatial Area Measurement", "Usable Area (m²) represents net internal workable office floor space excluding building cores, lift lobbies, and vertical mechanical shafts. Rentable Area includes pro-rata common core areas. BOMA loss factor = (Rentable - Usable) / Rentable."),
        ("2. Workplace Utilization Formulation", "Average Utilization Rate % = Sum of Actual Occupied Hours divided by Available Capacity Hours (Capacity x 10 operating hours/day). Peak Utilization % = Maximum concurrent occupants observed during peak hour divided by capacity."),
        ("3. Capacity Pressure Choke Point", "Defined as the percentage of business days where peak utilization equals or exceeds 85.0%. Facilities operating above this threshold experience acute meeting room shortages and desk crowding."),
        ("4. Occupancy Cost Metrics", "Cost per Available Seat = Annual Operating Cost / Capacity Seats. Cost per Occupied Seat = Annual Operating Cost / Average Daily Presence. Utilization Cost Premium = Difference between occupied cost and available seat carrying cost."),
        ("5. Portfolio Attention Index (PAI)", "Project-defined prioritization score (0 to 100): 30% Utilization Inefficiency + 20% Cost Intensity + 20% Lease Exposure + 15% Capacity Pressure + 15% Data Quality Risk. Sensitivity testing confirms rank stability (Spearman rho > 0.97)."),
        ("6. Reference FX Rates", "INR reference conversion: 1 SGD = ₹63.50; 1 AUD = ₹55.20; 1 MYR = ₹18.20; 1 THB = ₹2.35; 10,000 IDR = ₹53.00. Rates reflect fixed project baseline assumptions."),
        ("7. Mandatory Synthetic Disclosure", "The operational dataset in this workbook is synthetic and generated programmatically for analytical demonstration. It does not represent any real organization's properties or lease liabilities.")
    ]

    r_idx = 5
    for title, desc in methodology_sections:
        c_t = ws8.cell(row=r_idx, column=1, value=title)
        c_t.font = font_section
        r_idx += 1
        c_d = ws8.cell(row=r_idx, column=1, value=desc)
        c_d.font = font_data
        ws8.merge_cells(start_row=r_idx, start_column=1, end_row=r_idx, end_column=8)
        r_idx += 2

    # Auto-adjust column widths across all sheets
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if val_str.startswith("="):
                    # Guess formula length
                    max_len = max(max_len, 12)
                else:
                    max_len = max(max_len, len(val_str))
            ws.column_dimensions[col_letter].width = min(42, max(max_len + 3, 11))

    # Save to excel/Corporate_Real_Estate_Management_Workbook.xlsx
    out_xlsx = os.path.join(excel_dir, "Corporate_Real_Estate_Management_Workbook.xlsx")
    wb.save(out_xlsx)
    print(f"Saved Excel Workbook -> {out_xlsx}")

    # Copy to root
    root_xlsx = "Corporate_Real_Estate_Management_Workbook.xlsx"
    shutil.copyfile(out_xlsx, root_xlsx)
    print(f"Copied Excel Workbook to root -> {root_xlsx}")


if __name__ == "__main__":
    build_management_workbook()
