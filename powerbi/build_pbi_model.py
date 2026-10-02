"""Power BI Tabular Model (Model.bim) and Report Specification Builder.

Generates:
- powerbi/Model.bim: Complete Microsoft Tabular Model JSON schema with star schema relationships,
  data types, explicit DAX measures, display folders, and formatting strings.
- powerbi/power_query_scripts.m: Power Query M expressions for loading analytical datasets.
- powerbi/report_layout_spec.json: Visual layout specifications for the 6 core report pages
  and the Property Detail drill-through page.
"""

import os
import json
import pandas as pd


def build_tabular_model_bim():
    """Constructs Model.bim following Microsoft Tabular Object Model (TOM) specification."""
    print("Building Tabular Model Schema (powerbi/Model.bim)...")

    # Load column headers from analytical layer to ensure exact parity
    analytical_dir = os.path.join("data", "analytical")
    table_files = {
        "dim_date": "dim_date.csv",
        "dim_geography": "dim_geography.csv",
        "dim_facility_type": "dim_facility_type.csv",
        "dim_property": "dim_property.csv",
        "dim_floor": "dim_floor.csv",
        "dim_space": "dim_space.csv",
        "dim_lease": "dim_lease.csv",
        "fact_daily_workplace_utilization": "fact_daily_workplace_utilization.csv",
        "fact_room_utilization": "fact_room_utilization.csv",
        "fact_monthly_property_cost": "fact_monthly_property_cost.csv",
        "fact_headcount": "fact_headcount.csv",
        "fact_data_quality": "fact_data_quality.csv",
        "mart_workplace_pressure_matrix": "mart_workplace_pressure_matrix.csv",
        "mart_portfolio_attention_index": "mart_portfolio_attention_index.csv",
    }

    tables_def = []

    for tbl_name, fname in table_files.items():
        fpath = os.path.join(analytical_dir, fname)
        df_sample = pd.read_csv(fpath, nrows=5)

        columns = []
        for col in df_sample.columns:
            dtype = df_sample[col].dtype
            if "int" in str(dtype):
                col_type = "int64"
            elif "float" in str(dtype):
                col_type = "double"
            elif "bool" in str(dtype):
                col_type = "boolean"
            else:
                col_type = "string"

            col_obj = {
                "name": col,
                "dataType": col_type,
                "sourceColumn": col,
            }
            columns.append(col_obj)

        tables_def.append({
            "name": tbl_name,
            "columns": columns,
            "partitions": [
                {
                    "name": f"Partition_{tbl_name}",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": f'let\n    Source = Csv.Document(File.Contents("data/analytical/{fname}"),[Delimiter=",", Encoding=65001]),\n    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\nin\n    #"Promoted Headers"'
                    }
                }
            ]
        })

    # Add dedicated Measure Table
    measures_def = [
        # Scale
        {"name": "Total Properties", "folder": "01 Portfolio Scale", "format": "#,##0", "exp": "DISTINCTCOUNT('dim_property'[PropertyKey])"},
        {"name": "Total Usable Area", "folder": "01 Portfolio Scale", "format": "#,##0 sqm", "exp": "SUM('dim_property'[UsableAreaSqM])"},
        {"name": "Total Rentable Area", "folder": "01 Portfolio Scale", "format": "#,##0 sqm", "exp": "SUM('dim_property'[RentableAreaSqM])"},
        {"name": "Total Seat Capacity", "folder": "01 Portfolio Scale", "format": "#,##0", "exp": "SUM('dim_property'[CapacitySeats])"},
        {"name": "Assigned Headcount", "folder": "01 Portfolio Scale", "format": "#,##0", "exp": "SUM('dim_property'[AssignedHeadcount])"},
        {"name": "Desk Sharing Ratio", "folder": "01 Portfolio Scale", "format": "0.00", "exp": "DIVIDE([Assigned Headcount], [Total Seat Capacity], 0)"},
        {"name": "Average Density SqM", "folder": "01 Portfolio Scale", "format": "0.0 sqm/seat", "exp": "DIVIDE([Total Usable Area], [Total Seat Capacity], 0)"},
        # Utilization
        {"name": "Average Daily Presence", "folder": "02 Utilization & Presence", "format": "#,##0", "exp": "AVERAGE('fact_headcount'[AverageDailyPresence])"},
        {"name": "Total Vacant Capacity", "folder": "02 Utilization & Presence", "format": "#,##0 seats", "exp": "[Total Seat Capacity] - [Average Daily Presence]"},
        {"name": "Average Utilization %", "folder": "02 Utilization & Presence", "format": "0.0%", "exp": "DIVIDE(SUM('fact_daily_workplace_utilization'[OccupiedHours]), SUM('fact_daily_workplace_utilization'[AvailableHours]), 0)"},
        {"name": "Peak Utilization %", "folder": "02 Utilization & Presence", "format": "0.0%", "exp": "AVERAGE('fact_daily_workplace_utilization'[PeakUtilizationRate])"},
        {"name": "Max Peak Utilization %", "folder": "02 Utilization & Presence", "format": "0.0%", "exp": "MAX('fact_daily_workplace_utilization'[PeakUtilizationRate])"},
        {"name": "Capacity Pressure %", "folder": "02 Utilization & Presence", "format": "0.0%", "exp": "DIVIDE(CALCULATE(COUNTROWS('fact_daily_workplace_utilization'), 'fact_daily_workplace_utilization'[PeakUtilizationRate] >= 0.85), COUNTROWS('fact_daily_workplace_utilization'), 0)"},
        # Financial
        {"name": "Total Operating Cost INR", "folder": "03 Financial Efficiency", "format": "₹#,##0", "exp": "SUM('fact_monthly_property_cost'[TotalOperatingCostINR])"},
        {"name": "Annual Operating Cost INR", "folder": "03 Financial Efficiency", "format": "₹#,##0", "exp": "DIVIDE([Total Operating Cost INR], 2.0, 0)"},
        {"name": "Cost per SqM", "folder": "03 Financial Efficiency", "format": "₹#,##0/sqm", "exp": "DIVIDE([Annual Operating Cost INR], [Total Usable Area], 0)"},
        {"name": "Cost per Seat", "folder": "03 Financial Efficiency", "format": "₹#,##0", "exp": "DIVIDE([Annual Operating Cost INR], [Total Seat Capacity], 0)"},
        {"name": "Cost per Occupied Seat", "folder": "03 Financial Efficiency", "format": "₹#,##0", "exp": "DIVIDE([Annual Operating Cost INR], [Average Daily Presence], 0)"},
        {"name": "Utilization Cost Premium", "folder": "03 Financial Efficiency", "format": "₹#,##0", "exp": "[Cost per Occupied Seat] - [Cost per Seat]"},
        # Rooms
        {"name": "Total Room Bookings", "folder": "04 Room Dynamics", "format": "#,##0", "exp": "SUM('fact_room_utilization'[BookingCount])"},
        {"name": "Room No-Show Rate %", "folder": "04 Room Dynamics", "format": "0.0%", "exp": "DIVIDE(SUM('fact_room_utilization'[NoShowCount]), SUM('fact_room_utilization'[BookingCount]), 0)"},
        {"name": "Average Room Utilization %", "folder": "04 Room Dynamics", "format": "0.0%", "exp": "AVERAGE('fact_room_utilization'[RoomUtilizationRate])"},
        {"name": "Average Meeting Attendees", "folder": "04 Room Dynamics", "format": "0.0", "exp": "AVERAGE('fact_room_utilization'[AverageAttendees])"},
        # Lease
        {"name": "Lease Expiring Within 6 Months", "folder": "05 Lease & Governance", "format": "#,##0", "exp": "CALCULATE(COUNTROWS('dim_lease'), 'dim_lease'[ExpiryHorizonCategory] = \"Expiring <= 6M\")"},
        {"name": "Lease Expiring Within 12 Months", "folder": "05 Lease & Governance", "format": "#,##0", "exp": "CALCULATE(COUNTROWS('dim_lease'), 'dim_lease'[ExpiryHorizonCategory] IN {\"Expiring <= 6M\", \"Expiring 6-12M\"})"},
        {"name": "Lease Expiring Within 24 Months", "folder": "05 Lease & Governance", "format": "#,##0", "exp": "CALCULATE(COUNTROWS('dim_lease'), 'dim_lease'[ExpiryHorizonCategory] IN {\"Expiring <= 6M\", \"Expiring 6-12M\", \"Expiring 12-24M\"})"},
        {"name": "Expiring Rent Exposure INR", "folder": "05 Lease & Governance", "format": "₹#,##0", "exp": "CALCULATE(SUM('dim_lease'[AnnualRentINR]), 'dim_lease'[ExpiryHorizonCategory] IN {\"Expiring <= 6M\", \"Expiring 6-12M\"})"},
        # DQ
        {"name": "Data Quality Exception Count", "folder": "06 Data Quality & Risk", "format": "#,##0", "exp": "COUNTROWS('fact_data_quality')"},
        {"name": "Data Quality Pass Rate %", "folder": "06 Data Quality & Risk", "format": "0.00%", "exp": "DIVIDE(282584 - [Data Quality Exception Count], 282584, 1.0)"},
        {"name": "Critical Exceptions Count", "folder": "06 Data Quality & Risk", "format": "#,##0", "exp": "CALCULATE(COUNTROWS('fact_data_quality'), 'fact_data_quality'[Severity] = \"Critical\")"},
        {"name": "Portfolio Attention Count", "folder": "06 Data Quality & Risk", "format": "#,##0", "exp": "CALCULATE(COUNTROWS('dim_property'), RELATED('mart_portfolio_attention_index'[AttentionTier]) = \"Immediate Attention\")"},
    ]

    measures_table = {
        "name": "_Measures",
        "columns": [
            {"name": "MeasureId", "dataType": "int64", "isHidden": True, "sourceColumn": "MeasureId"}
        ],
        "measures": [
            {
                "name": m["name"],
                "expression": m["exp"],
                "formatString": m["format"],
                "displayFolder": m["folder"]
            }
            for m in measures_def
        ],
        "partitions": [
            {
                "name": "Partition__Measures",
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": "let Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText(\"i44FAA==\", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [MeasureId = _t]) in Source"
                }
            }
        ]
    }
    tables_def.append(measures_table)

    # Define star-schema relationships
    relationships = [
        {"fromTable": "fact_daily_workplace_utilization", "fromColumn": "DateKey", "toTable": "dim_date", "toColumn": "DateKey"},
        {"fromTable": "fact_daily_workplace_utilization", "fromColumn": "PropertyKey", "toTable": "dim_property", "toColumn": "PropertyKey"},
        {"fromTable": "fact_daily_workplace_utilization", "fromColumn": "FloorKey", "toTable": "dim_floor", "toColumn": "FloorKey"},
        {"fromTable": "fact_daily_workplace_utilization", "fromColumn": "SpaceKey", "toTable": "dim_space", "toColumn": "SpaceKey"},
        {"fromTable": "fact_room_utilization", "fromColumn": "DateKey", "toTable": "dim_date", "toColumn": "DateKey"},
        {"fromTable": "fact_room_utilization", "fromColumn": "PropertyKey", "toTable": "dim_property", "toColumn": "PropertyKey"},
        {"fromTable": "fact_room_utilization", "fromColumn": "SpaceKey", "toTable": "dim_space", "toColumn": "SpaceKey"},
        {"fromTable": "fact_monthly_property_cost", "fromColumn": "MonthDateKey", "toTable": "dim_date", "toColumn": "DateKey"},
        {"fromTable": "fact_monthly_property_cost", "fromColumn": "PropertyKey", "toTable": "dim_property", "toColumn": "PropertyKey"},
        {"fromTable": "fact_headcount", "fromColumn": "MonthDateKey", "toTable": "dim_date", "toColumn": "DateKey"},
        {"fromTable": "fact_headcount", "fromColumn": "PropertyKey", "toTable": "dim_property", "toColumn": "PropertyKey"},
        {"fromTable": "dim_property", "fromColumn": "GeographyKey", "toTable": "dim_geography", "toColumn": "GeographyKey"},
        {"fromTable": "dim_property", "fromColumn": "FacilityTypeKey", "toTable": "dim_facility_type", "toColumn": "FacilityTypeKey"},
        {"fromTable": "dim_floor", "fromColumn": "PropertyKey", "toTable": "dim_property", "toColumn": "PropertyKey"},
        {"fromTable": "dim_space", "fromColumn": "FloorKey", "toTable": "dim_floor", "toColumn": "FloorKey"},
        {"fromTable": "dim_space", "fromColumn": "PropertyKey", "toTable": "dim_property", "toColumn": "PropertyKey"},
        {"fromTable": "dim_lease", "fromColumn": "PropertyKey", "toTable": "dim_property", "toColumn": "PropertyKey"},
        {"fromTable": "mart_workplace_pressure_matrix", "fromColumn": "PropertyKey", "toTable": "dim_property", "toColumn": "PropertyKey"},
        {"fromTable": "mart_portfolio_attention_index", "fromColumn": "PropertyKey", "toTable": "dim_property", "toColumn": "PropertyKey"},
    ]

    model_bim = {
        "name": "CorporateRealEstateAnalytics",
        "compatibilityLevel": 1567,
        "model": {
            "culture": "en-US",
            "dataAccessOptions": {"legacyRedirectsEnabled": False, "returnErrorValuesAsNull": False},
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "en-US",
            "tables": tables_def,
            "relationships": [
                {
                    "name": f"Rel_{r['fromTable']}_{r['toTable']}_{r['fromColumn']}",
                    "fromTable": r["fromTable"],
                    "fromColumn": r["fromColumn"],
                    "toTable": r["toTable"],
                    "toColumn": r["toColumn"],
                    "crossFilteringBehavior": "singleDirection"
                }
                for r in relationships
            ],
            "annotations": [
                {"name": "ClientCompatibilityLevel", "value": "700"}
            ]
        }
    }

    bim_path = os.path.join("powerbi", "Model.bim")
    with open(bim_path, "w", encoding="utf-8") as f:
        json.dump(model_bim, f, indent=2)
    print(f"Saved Tabular Model schema -> {bim_path}")

    # Write Power Query M scripts
    m_path = os.path.join("powerbi", "power_query_scripts.m")
    with open(m_path, "w", encoding="utf-8") as f:
        f.write("// Power Query M Data Extraction & Loading Scripts\n\n")
        for tbl_name, fname in table_files.items():
            f.write(f"// Table: {tbl_name}\n")
            f.write(f'shared {tbl_name} = let\n')
            f.write(f'    Source = Csv.Document(File.Contents("data/analytical/{fname}"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n')
            f.write('    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n')
            f.write('in\n    #"Promoted Headers";\n\n')
    print(f"Saved Power Query scripts -> {m_path}")


def build_report_layout_spec():
    """Generates the visual layout specifications for the 6 core pages + drill-through page."""
    print("Building Power BI Report Layout Specification (powerbi/report_layout_spec.json)...")

    pages = [
        {
            "pageNumber": 1,
            "pageTitle": "Executive Portfolio Overview",
            "purpose": "Provide management an immediate portfolio view of scale, utilization, cost, capacity, and issues.",
            "answeredQuestion": "What is happening across the regional portfolio?",
            "visuals": [
                {"visualType": "kpi_card_strip", "title": "Portfolio scale & efficiency KPIs", "metrics": ["[Total Properties]", "[Total Usable Area]", "[Total Seat Capacity]", "[Average Utilization %]", "[Peak Utilization %]", "[Annual Operating Cost INR]", "[Cost per Occupied Seat]", "[Lease Expiring Within 12 Months]", "[Data Quality Pass Rate %]"]},
                {"visualType": "bar_chart", "title": "Operating cost and average utilization by country", "xAxis": "Country", "yAxis": ["[Annual Operating Cost INR]", "[Average Utilization %]"], "subtitle": "Comparison of financial commitment against physical utilization across 6 markets"},
                {"visualType": "line_chart", "title": "Portfolio workplace utilization monthly trend", "xAxis": "MonthYear", "yAxis": ["[Average Utilization %]", "[Peak Utilization %]"], "subtitle": "24-month historical trend showing seasonal dips and mid-week peak pressure"},
                {"visualType": "donut_or_bar", "title": "Usable area distribution by facility type", "dimension": "FacilityTypeName", "metric": "[Total Usable Area]"},
                {"visualType": "table", "title": "Top locations requiring management review", "columns": ["PropertyCode", "PropertyName", "City", "Country", "AverageUtilizationPct", "AnnualCostPerOccupiedSeatINR", "ExpiryHorizonCategory", "PortfolioAttentionIndex", "PrimaryAttentionDriver"], "source": "mart_portfolio_attention_index", "limit": 5},
                {"visualType": "insight_card", "title": "Analyst portfolio observation", "text": "Mid-week collaborative peak demand averages 78.4% across key hubs, creating operational friction that monthly averages (59.4%) mask. Three properties represent 26.8% of vacant capacity and ₹42.8 Cr in expiring lease liability."}
            ]
        },
        {
            "pageNumber": 2,
            "pageTitle": "Portfolio & Geography",
            "purpose": "Evaluate physical scale, geographic concentration, and area-to-capacity distributions across countries and metros.",
            "answeredQuestion": "Where is space concentrated and how is capacity provisioned geographically?",
            "slicers": ["Region", "Country", "City", "FacilityTypeName"],
            "drillDownHierarchy": ["Region", "Country", "City", "PropertyName"],
            "visuals": [
                {"visualType": "bar_chart", "title": "Usable area and seat capacity by country", "xAxis": "Country", "yAxis": ["[Total Usable Area]", "[Total Seat Capacity]"]},
                {"visualType": "bar_chart", "title": "Average utilization and density by city", "xAxis": "City", "yAxis": ["[Average Utilization %]", "[Average Density SqM]"]},
                {"visualType": "scatter_plot", "title": "Usable area versus seat capacity relationship", "xAxis": "[Total Seat Capacity]", "yAxis": ["[Total Usable Area]"], "legend": "Country", "subtitle": "Evaluates architectural density consistency; diagonal represents ~9.2 m²/seat"},
                {"visualType": "matrix_table", "title": "Geographical portfolio hierarchy breakdown", "rows": ["Country", "City", "PropertyName"], "values": ["[Total Usable Area]", "[Total Seat Capacity]", "[Assigned Headcount]", "[Desk Sharing Ratio]", "[Average Utilization %]"]}
            ]
        },
        {
            "pageNumber": 3,
            "pageTitle": "Workplace Utilization",
            "purpose": "Analyze daily presence dynamics, weekday seasonality, and operational capacity pressure.",
            "answeredQuestion": "How is workplace capacity actively utilized and where do choke points appear?",
            "signatureVisual": "Workplace Pressure Matrix",
            "visuals": [
                {"visualType": "scatter_quadrant", "title": "Workplace Pressure Matrix", "xAxis": "Average Utilization % (Benchmark 55%)", "yAxis": "Peak Utilization % (Benchmark 80%)", "bubbleSize": "UsableAreaSqM", "category": "PressureQuadrant", "subtitle": "Classifies properties into Underutilized, Peak-sensitive, Consistently active, or Capacity-constrained"},
                {"visualType": "clustered_bar", "title": "Utilization and peak rates by day of week", "xAxis": "DayName", "yAxis": ["Average Utilization %", "Peak Utilization %"], "subtitle": "Exposes the Tuesday-Thursday surge and Friday occupancy drop"},
                {"visualType": "heatmap_matrix", "title": "Floor-level workplace utilization intensity", "rows": ["PropertyName"], "columns": ["FloorNumber"], "values": "DailyUtilizationRatePct"},
                {"visualType": "bar_chart", "title": "Proportion of business days experiencing peak capacity pressure (>=85%)", "xAxis": "PropertyName", "yAxis": "CapacityPressurePct"}
            ]
        },
        {
            "pageNumber": 4,
            "pageTitle": "Cost & Efficiency",
            "purpose": "Identify spatial cost concentrations and isolate assets where cost intensity diverges from utilization.",
            "answeredQuestion": "Where are real estate operating costs concentrated and where is carrying cost inefficient?",
            "signatureVisual": "Cost vs Utilization Scatter Plot",
            "visuals": [
                {"visualType": "scatter_plot", "title": "Cost versus utilization: Cost per occupied seat vs. Average utilization", "xAxis": "Average Utilization %", "yAxis": "Cost per Occupied Seat (INR)", "bubbleSize": "UsableAreaSqM", "legend": "Region", "subtitle": "Exposes assets with severe economic carrying penalty due to empty workstations"},
                {"visualType": "treemap", "title": "Operating cost contribution by country and property", "grouping": ["Country", "PropertyName"], "values": "TotalOperatingCostINR"},
                {"visualType": "bar_chart", "title": "Cost per usable square metre across property portfolio", "xAxis": "PropertyName", "yAxis": "Cost per SqM", "referenceLine": "Regional Median Cost/SqM"},
                {"visualType": "table", "title": "Occupied seat cost premium analysis", "columns": ["PropertyCode", "PropertyName", "City", "Cost per Seat", "Cost per Occupied Seat", "Utilization Cost Premium", "Cost Inefficiency Multiplier %"]}
            ]
        },
        {
            "pageNumber": 5,
            "pageTitle": "Lease & Management Attention",
            "purpose": "Highlight critical lease milestones, notice periods, and multi-factor management prioritization.",
            "answeredQuestion": "Which lease contracts require immediate strategy and which assets rank highest for management review?",
            "signatureVisual": "Management Attention Table",
            "visuals": [
                {"visualType": "bar_chart", "title": "Lease expiration profile by decision horizon", "xAxis": "ExpiryHorizonCategory", "yAxis": ["ContractCount", "TotalAnnualBaseRentINR"]},
                {"visualType": "timeline_gantt", "title": "Lease critical milestone schedule", "items": ["PropertyName", "LeaseStartDate", "LeaseEndDate", "NoticePeriodMonths", "ExpiryHorizonCategory"]},
                {"visualType": "table", "title": "Management Attention Table", "subtitle": "Comprehensive multi-factor prioritization matrix sorted by Portfolio Attention Index", "columns": ["AttentionRank", "PropertyCode", "PropertyName", "City", "Country", "AverageUtilizationPct", "PeakUtilizationPct", "CostPerOccupiedSeatINR", "ExpiryHorizonCategory", "DataQualityStatus", "PortfolioAttentionIndex", "PrimaryAttentionDriver", "AttentionTier"]},
                {"visualType": "donut_chart", "title": "Primary attention drivers across regional portfolio", "category": "PrimaryAttentionDriver", "values": "PropertyCount"}
            ]
        },
        {
            "pageNumber": 6,
            "pageTitle": "Data Quality & Controls",
            "purpose": "Provide complete auditability of source data validation, rule evaluations, and remediation.",
            "answeredQuestion": "How clean and reliable is the operational data feeding the management dashboard?",
            "visuals": [
                {"visualType": "kpi_card_strip", "title": "Data quality governance KPIs", "metrics": ["[Data Quality Pass Rate %]", "[Data Quality Exception Count]", "[Critical Exceptions Count]", "Total Evaluated Records: 282,584"]},
                {"visualType": "donut_chart", "title": "Exceptions by severity tier", "category": "Severity", "values": "ExceptionCount", "colors": {"Critical": "#C0392B", "High": "#E67E22", "Medium": "#F1C40F"}},
                {"visualType": "bar_chart", "title": "Exceptions detected by data quality rule", "xAxis": "RuleID", "yAxis": "ExceptionCount", "subtitle": "Evaluates uniqueness, validity, chronology, and consistency rules"},
                {"visualType": "bar_chart", "title": "Exceptions by source table", "xAxis": "TableName", "yAxis": "ExceptionCount"},
                {"visualType": "table", "title": "Audited data quality exception ledger", "columns": ["IssueID", "RuleID", "TableName", "RecordIdentifier", "Severity", "ExpectedRule", "InjectedValue", "CorrectedValue", "RemediationStatus"]}
            ]
        },
        {
            "pageNumber": 7,
            "pageTitle": "Property Detail (Drill-Through)",
            "purpose": "Dedicated single-property deep dive triggered via drill-through from any dashboard visual.",
            "answeredQuestion": "What are the granular operational, spatial, financial, and lease dynamics of this specific asset?",
            "drillThroughTarget": "dim_property[PropertyCode]",
            "visuals": [
                {"visualType": "property_header_card", "title": "Asset Overview & Metadata", "fields": ["PropertyName", "PropertyCode", "City", "Country", "FacilityTypeName", "OwnershipType", "OpeningYear"]},
                {"visualType": "kpi_card_row", "title": "Asset Key Metrics", "metrics": ["UsableAreaSqM", "CapacitySeats", "AssignedHeadcount", "AverageUtilizationPct", "PeakUtilizationPct", "AnnualOperatingCostINR", "CostPerOccupiedSeatINR"]},
                {"visualType": "line_chart", "title": "24-Month workplace utilization & presence trajectory", "xAxis": "MonthYear", "yAxis": ["AverageUtilizationRate", "PeakDailyUtilization"]},
                {"visualType": "table", "title": "Floor-level capacity and zoning breakdown", "columns": ["FloorNumber", "FloorName", "UsableAreaSqM", "CapacitySeats"]},
                {"visualType": "bar_chart", "title": "Meeting room demand and attendee distribution", "xAxis": "RoomType", "yAxis": ["AvgRoomCapacity", "AvgAttendeesPerMeeting", "NoShowRatePct"]},
                {"visualType": "lease_card", "title": "Contractual lease terms & critical milestones", "fields": ["LeaseContractNumber", "LeaseStartDate", "LeaseEndDate", "NoticePeriodMonths", "AnnualRentINR", "ExpiryHorizonCategory"]},
                {"visualType": "table", "title": "Logged data quality items for this asset", "columns": ["IssueID", "RuleID", "Severity", "ExpectedRule", "InjectedValue", "CorrectedValue", "RemediationStatus"]}
            ]
        }
    ]

    report_spec = {
        "reportTitle": "Corporate Real Estate Portfolio & Workplace Analytics",
        "author": "Lead Corporate Real Estate Data Analyst",
        "baselineReportingDate": "2026-09-30",
        "theme": "Corporate Real Estate Executive Theme",
        "pageCount": len(pages),
        "pages": pages
    }

    spec_path = os.path.join("powerbi", "report_layout_spec.json")
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(report_spec, f, indent=2)
    print(f"Saved Report Layout Specification -> {spec_path}")


if __name__ == "__main__":
    build_tabular_model_bim()
    build_report_layout_spec()
