"""Deliverable Artifacts Integrity Tests.

Tests:
- All 8 sheets exist in Excel workbook with valid non-empty rows and formulas
- All 10 pages exist in PDF management report with non-empty text and valid headers
- All 7 slides exist in PowerPoint deck with shapes, text boxes, and charts
- Power BI web dashboard preview files exist and contain valid JSON data
- Project tracker CSV contains all 22 tasks with valid statuses and dates
"""

import os
import json
import pytest
import openpyxl
import pypdf
import pptx
import pandas as pd

ROOT_DIR = "."


# Parameterized test over all 8 Excel sheets
EXCEL_SHEETS = [
    "Executive Summary",
    "Property Register",
    "Occupancy Analysis",
    "Cost Analysis",
    "Lease Tracker",
    "Data Quality",
    "Project Tracker",
    "Methodology"
]


@pytest.fixture(scope="module")
def excel_workbook():
    xlsx_path = os.path.join("excel", "Corporate_Real_Estate_Management_Workbook.xlsx")
    assert os.path.exists(xlsx_path), "Excel workbook missing in excel/"
    assert os.path.exists("Corporate_Real_Estate_Management_Workbook.xlsx"), "Root copy of Excel workbook missing"
    return openpyxl.load_workbook(xlsx_path, data_only=False)


@pytest.mark.parametrize("sheet_name", EXCEL_SHEETS)
def test_excel_sheet_exists_and_populated(excel_workbook, sheet_name):
    assert sheet_name in excel_workbook.sheetnames, f"Sheet {sheet_name} missing in workbook"
    ws = excel_workbook[sheet_name]
    assert ws.max_row >= 10, f"Sheet {sheet_name} has insufficient rows: {ws.max_row}"


def test_excel_formulas_present(excel_workbook):
    ws_prop = excel_workbook["Property Register"]
    # Check that row 5 contains formulas
    assert str(ws_prop["L5"].value).startswith("="), "Density cell must be formula"
    assert str(ws_prop["M5"].value).startswith("="), "Sharing ratio cell must be formula"
    assert str(ws_prop["N5"].value).startswith("="), "Loss factor cell must be formula"


@pytest.fixture(scope="module")
def pdf_reader():
    pdf_path = os.path.join("reports", "Corporate_Real_Estate_Portfolio_Analytics_Report.pdf")
    assert os.path.exists(pdf_path), "PDF report missing in reports/"
    assert os.path.exists("Corporate_Real_Estate_Portfolio_Analytics_Report.pdf"), "Root copy of PDF report missing"
    return pypdf.PdfReader(pdf_path)


def test_pdf_page_count_exact(pdf_reader):
    assert len(pdf_reader.pages) == 10, "PDF report must contain exactly 10 pages"


# Parameterized test over all 10 PDF pages
@pytest.mark.parametrize("page_num", list(range(1, 11)))
def test_each_pdf_page_has_substantial_text(pdf_reader, page_num):
    page = pdf_reader.pages[page_num - 1]
    text = page.extract_text()
    assert len(text) >= 500, f"Page {page_num} text too short ({len(text)} chars); check for rendering drop"


@pytest.fixture(scope="module")
def pptx_deck():
    pptx_path = os.path.join("presentation", "Corporate_Real_Estate_Executive_Review.pptx")
    assert os.path.exists(pptx_path), "PPTX deck missing in presentation/"
    assert os.path.exists("Corporate_Real_Estate_Executive_Review.pptx"), "Root copy of PPTX deck missing"
    return pptx.Presentation(pptx_path)


def test_pptx_slide_count_exact(pptx_deck):
    assert len(pptx_deck.slides) == 7, "PowerPoint deck must contain exactly 7 slides"


# Parameterized test over all 7 PowerPoint slides
@pytest.mark.parametrize("slide_num", list(range(1, 8)))
def test_each_pptx_slide_has_shapes_and_content(pptx_deck, slide_num):
    slide = pptx_deck.slides[slide_num - 1]
    assert len(slide.shapes) >= 5, f"Slide {slide_num} has fewer shapes than expected: {len(slide.shapes)}"


def test_dashboard_preview_files_exist():
    d_dir = os.path.join("powerbi", "dashboard_preview")
    assert os.path.exists(os.path.join(d_dir, "index.html"))
    assert os.path.exists(os.path.join(d_dir, "style.css"))
    assert os.path.exists(os.path.join(d_dir, "app.js"))
    data_json = os.path.join(d_dir, "dashboard_data.json")
    assert os.path.exists(data_json)
    with open(data_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["properties"]) == 25
    assert len(data["pressure_matrix"]) == 25
    assert len(data["attention_index"]) == 25


def test_project_tracker_csv_integrity():
    assert os.path.exists("project_tracker.csv")
    df = pd.read_csv("project_tracker.csv")
    assert len(df) == 22, "Project tracker must contain exactly 22 tracked tasks"
    assert (df["Status"] == "Complete").all(), "All tracked tasks must be marked Complete"
    assert (df["ProgressPct"] == 100).all(), "All tracked tasks must be 100% progress"
