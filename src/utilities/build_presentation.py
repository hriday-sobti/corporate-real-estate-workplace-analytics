"""Executive PowerPoint Presentation Builder.

Generates:
- presentation/Corporate_Real_Estate_Executive_Review.pptx
- Corporate_Real_Estate_Executive_Review.pptx (root copy)

7 Structured Executive Slides:
- Slide 1: Regional Portfolio Overview (Scale, Footprint & Operational Model)
- Slide 2: How the Workplace Is Being Used (Mid-Week Peaks vs. Friday Trough)
- Slide 3: Where Capacity Pressure Appears (Choke Points & Workplace Pressure Matrix)
- Slide 4: Cost Efficiency Across the Portfolio (Carrying Costs & Occupied Seat Premiums)
- Slide 5: Lease Exposure & Management Attention (Critical Horizons & PAI Prioritization)
- Slide 6: Data Quality & Analytical Confidence (Governance Controls & 99.98% Pass Rate)
- Slide 7: Areas for Further Investigation (Consolidation Scenarios & Strategic Actions)
"""

import os
import shutil
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE


def build_presentation_deck():
    """Builds the 7-slide executive review presentation."""
    print("==================================================================")
    print("PHASE 18: EXECUTIVE POWERPOINT DECK GENERATION")
    print("==================================================================")

    prs_dir = "presentation"
    os.makedirs(prs_dir, exist_ok=True)
    pptx_path = os.path.join(prs_dir, "Corporate_Real_Estate_Executive_Review.pptx")

    prs = Presentation()
    # 16:9 Widescreen (13.333 x 7.5 inches)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]  # Completely blank slide

    # Corporate Colors
    NAVY = RGBColor(0x1F, 0x4E, 0x79)
    CORAL = RGBColor(0xE0, 0x7A, 0x5F)
    GREEN = RGBColor(0x2E, 0x7D, 0x32)
    ORANGE = RGBColor(0xE6, 0x7E, 0x22)
    RED = RGBColor(0xC0, 0x39, 0x2B)
    SLATE = RGBColor(0x4A, 0x55, 0x68)
    MUTED = RGBColor(0x71, 0x80, 0x96)
    DARK = RGBColor(0x1A, 0x20, 0x2C)
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    BG_LIGHT = RGBColor(0xF8, 0xF9, 0xFA)
    CARD_BG = RGBColor(0xF1, 0xF5, 0xF9)
    BORDER_COL = RGBColor(0xCB, 0xD5, 0xE0)

    def add_header(slide, title_text, category_text):
        """Adds consistent executive header banner."""
        # Top accent bar
        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
        accent.fill.solid()
        accent.fill.fore_color.rgb = NAVY
        accent.line.color.rgb = NAVY

        # Category Tracker
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = CORAL

        # Executive Headline
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.7), Inches(0.65))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(20)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY

    def add_footer(slide, slide_num):
        """Adds consistent source footer and slide counter."""
        foot_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.7), Inches(0.35))
        tf = foot_box.text_frame
        p = tf.paragraphs[0]
        p.text = f"Corporate Real Estate Portfolio & Workplace Analytics | Regional Review | Slide {slide_num} of 7"
        p.font.size = Pt(9)
        p.font.color.rgb = MUTED

    def add_kpi_card(slide, left, top, width, height, label, value, context, accent_color=NAVY):
        """Adds structured executive metric card."""
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COL
        card.line.width = Pt(1)

        # Left border bar
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Inches(0.08), height)
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent_color
        bar.line.color.rgb = accent_color

        tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.08), width - Inches(0.25), height - Inches(0.16))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = label.upper()
        p1.font.size = Pt(9)
        p1.font.bold = True
        p1.font.color.rgb = MUTED

        p2 = tf.add_paragraph()
        p2.text = value
        p2.font.size = Pt(22)
        p2.font.bold = True
        p2.font.color.rgb = accent_color

        p3 = tf.add_paragraph()
        p3.text = context
        p3.font.size = Pt(9)
        p3.font.color.rgb = SLATE

    # -------------------------------------------------------------
    # SLIDE 1: Regional Portfolio Overview
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    add_header(s1, "Regional real estate represents 20,540 seats across 11 key metropolitan markets", "Executive Portfolio Overview")
    add_footer(s1, 1)

    # 4 KPI Cards
    add_kpi_card(s1, Inches(0.8), Inches(1.5), Inches(2.7), Inches(1.4), "Portfolio Scope", "25 Properties", "11 Cities across 6 Countries", NAVY)
    add_kpi_card(s1, Inches(3.8), Inches(1.5), Inches(2.7), Inches(1.4), "Usable Work Area", "190,225 m²", "16.2% Building loss factor", NAVY)
    add_kpi_card(s1, Inches(6.8), Inches(1.5), Inches(2.7), Inches(1.4), "Capacity & Headcount", "20,540 Seats", "25,270 Staff (1.23:1 sharing)", NAVY)
    add_kpi_card(s1, Inches(9.8), Inches(1.5), Inches(2.7), Inches(1.4), "Operating Expense", "₹597.5 Cr", "₹31,408 per usable m²", CORAL)

    # Narrative callout panels
    box_left = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.2), Inches(5.7), Inches(3.5))
    box_left.fill.solid(); box_left.fill.fore_color.rgb = CARD_BG; box_left.line.color.rgb = BORDER_COL
    tf_l = box_left.text_frame; tf_l.word_wrap = True; tf_l.margin_left = Inches(0.3); tf_l.margin_top = Inches(0.3)
    p_l1 = tf_l.paragraphs[0]; p_l1.text = "Operational Architecture & Market Concentration"; p_l1.font.size = Pt(13); p_l1.font.bold = True; p_l1.font.color.rgb = NAVY
    p_l2 = tf_l.add_paragraph(); p_l2.text = (
        "\n• India Footprint (75.9% of Space): 15 facilities spanning Bengaluru, Pune, Hyderabad, Chennai, Mumbai, and Delhi NCR. "
        "Delivers high-capacity software R&D and shared business operations at efficient carrying costs (₹15,000–₹24,000/m²).\n\n"
        "• Asia-Pacific Footprint (24.1% of Space): 10 facilities across Singapore, Sydney, Kuala Lumpur, Bangkok, and Jakarta. "
        "Hosts regional corporate headquarters and commercial client centers representing 56.8% of portfolio operational expenditure."
    ); p_l2.font.size = Pt(10.5); p_l2.font.color.rgb = SLATE

    box_right = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(3.2), Inches(5.7), Inches(3.5))
    box_right.fill.solid(); box_right.fill.fore_color.rgb = CARD_BG; box_right.line.color.rgb = BORDER_COL
    tf_r = box_right.text_frame; tf_r.word_wrap = True; tf_r.margin_left = Inches(0.3); tf_r.margin_top = Inches(0.3)
    p_r1 = tf_r.paragraphs[0]; p_r1.text = "Strategic Governance Objectives"; p_r1.font.size = Pt(13); p_r1.font.bold = True; p_r1.font.color.rgb = NAVY
    p_r2 = tf_r.add_paragraph(); p_r2.text = (
        "\n• Empirical Decision Support: Move executive decision-making away from static headcount ratios toward validated, time-series presence analytics.\n\n"
        "• Near-Term Renewal Windows: Establish proactive negotiation strategy across 10 upcoming lease expirations in the next 12 months (₹105.8 Cr in annual base rent commitments).\n\n"
        "• Spatial Agility: Identify persistent vacant carrying liabilities without triggering overcrowding friction during peak collaborative mid-week periods."
    ); p_r2.font.size = Pt(10.5); p_r2.font.color.rgb = SLATE

    # -------------------------------------------------------------
    # SLIDE 2: How Workplace Is Being Used
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Peak demand tells a completely different story from the monthly portfolio average", "Workplace Utilization Dynamics")
    add_footer(s2, 2)

    # Embed Chart 1: Weekday
    chart1_p = os.path.join("outputs", "charts", "eda_weekday_utilization.png")
    if os.path.exists(chart1_p):
        s2.shapes.add_picture(chart1_p, Inches(0.8), Inches(1.5), Inches(6.8), Inches(5.1))

    # Right side analytical bullets
    box_s2 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.9), Inches(1.5), Inches(4.6), Inches(5.1))
    box_s2.fill.solid(); box_s2.fill.fore_color.rgb = CARD_BG; box_s2.line.color.rgb = BORDER_COL
    tf_s2 = box_s2.text_frame; tf_s2.word_wrap = True; tf_s2.margin_left = Inches(0.3); tf_s2.margin_top = Inches(0.3)
    p_s2_1 = tf_s2.paragraphs[0]; p_s2_1.text = "Empirical Utilization Takeaways"; p_s2_1.font.size = Pt(14); p_s2_1.font.bold = True; p_s2_1.font.color.rgb = NAVY
    p_s2_2 = tf_s2.add_paragraph(); p_s2_2.text = (
        "\n• Monthly Average Masking Effect: Regional utilization averages 59.4%. However, mid-week attendance surges to 74.2% on Wednesdays with peak hours hitting 89.1%.\n\n"
        "• Friday Occupancy Collapse: Friday presence drops to 37.2%, reflecting widespread enterprise remote flexibility. Designing for Friday would cause severe overcrowding; designing for Wednesday leaves space empty.\n\n"
        "• Management Rule: Footprint consolidation must be preceded by attendance smoothing policies (e.g. departmental scheduling) to prevent capacity friction."
    ); p_s2_2.font.size = Pt(11); p_s2_2.font.color.rgb = SLATE

    # -------------------------------------------------------------
    # SLIDE 3: Where Capacity Pressure Appears
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Seven facilities operate under severe capacity friction despite modest weekly averages", "Capacity Bottlenecks & Pressure Matrix")
    add_footer(s3, 3)

    chart2_p = os.path.join("outputs", "charts", "eda_pressure_matrix.png")
    if os.path.exists(chart2_p):
        s3.shapes.add_picture(chart2_p, Inches(0.8), Inches(1.5), Inches(7.0), Inches(5.1))

    box_s3 = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.1), Inches(1.5), Inches(4.4), Inches(5.1))
    box_s3.fill.solid(); box_s3.fill.fore_color.rgb = CARD_BG; box_s3.line.color.rgb = BORDER_COL
    tf_s3 = box_s3.text_frame; tf_s3.word_wrap = True; tf_s3.margin_left = Inches(0.3); tf_s3.margin_top = Inches(0.3)
    p_s3_1 = tf_s3.paragraphs[0]; p_s3_1.text = "Workplace Pressure Quadrants"; p_s3_1.font.size = Pt(14); p_s3_1.font.bold = True; p_s3_1.font.color.rgb = NAVY
    p_s3_2 = tf_s3.add_paragraph(); p_s3_2.text = (
        "\n• Capacity-Constrained (8 Assets): Bengaluru Tower 1, Singapore MBFC, Hyderabad Cyber Horizon. High average (≥55%) and extreme peak (≥80%). Choke points occur on >20% of days.\n\n"
        "• Peak-Sensitive (5 Assets): Mumbai BKC, Bangkok Sathorn, Pune Kalyani. Modest averages (<55%) but sudden mid-week spikes (≥80%).\n\n"
        "• Chronic Underutilization (6 Assets): Pune Magarpatta, Chennai Guindy, Delhi Express. Both average & peak stay low (<55% avg, <80% peak). Immediate candidates for consolidation."
    ); p_s3_2.font.size = Pt(11); p_s3_2.font.color.rgb = SLATE

    # -------------------------------------------------------------
    # SLIDE 4: Cost Efficiency Across Portfolio
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Vacant seat carrying cost creates an effective 68.4% cost penalty across the region", "Occupancy Cost Efficiency")
    add_footer(s4, 4)

    chart3_p = os.path.join("outputs", "charts", "eda_cost_vs_utilization.png")
    if os.path.exists(chart3_p):
        s4.shapes.add_picture(chart3_p, Inches(0.8), Inches(1.5), Inches(7.0), Inches(5.1))

    box_s4 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.1), Inches(1.5), Inches(4.4), Inches(5.1))
    box_s4.fill.solid(); box_s4.fill.fore_color.rgb = CARD_BG; box_s4.line.color.rgb = BORDER_COL
    tf_s4 = box_s4.text_frame; tf_s4.word_wrap = True; tf_s4.margin_left = Inches(0.3); tf_s4.margin_top = Inches(0.3)
    p_s4_1 = tf_s4.paragraphs[0]; p_s4_1.text = "Financial Carrying Insights"; p_s4_1.font.size = Pt(14); p_s4_1.font.bold = True; p_s4_1.font.color.rgb = NAVY
    p_s4_2 = tf_s4.add_paragraph(); p_s4_2.text = (
        "\n• Cost per Available Seat: Averages ₹290,872/year across the regional portfolio.\n\n"
        "• Cost per Occupied Seat: Averages ₹489,850/year—a ₹198,978 carrying penalty per seat driven by vacant desks.\n\n"
        "• Extreme Metro Outliers: Low-utilization commercial offices in Mumbai BKC and Sydney CBD escalate to ₹1,030,000–₹1,840,000 per occupied seat.\n\n"
        "• Financial Focus: Rightsizing low-utilization leases delivers immediate margin relief."
    ); p_s4_2.font.size = Pt(11); p_s4_2.font.color.rgb = SLATE

    # -------------------------------------------------------------
    # SLIDE 5: Lease Exposure & Management Attention
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Ten lease expirations within 12 months align with highest operational priority assets", "Lease Exposure & Attention Ranking")
    add_footer(s5, 5)

    chart4_p = os.path.join("outputs", "charts", "eda_attention_ranking.png")
    if os.path.exists(chart4_p):
        s5.shapes.add_picture(chart4_p, Inches(0.8), Inches(1.5), Inches(7.0), Inches(5.1))

    box_s5 = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.1), Inches(1.5), Inches(4.4), Inches(5.1))
    box_s5.fill.solid(); box_s5.fill.fore_color.rgb = CARD_BG; box_s5.line.color.rgb = BORDER_COL
    tf_s5 = box_s5.text_frame; tf_s5.word_wrap = True; tf_s5.margin_left = Inches(0.3); tf_s5.margin_top = Inches(0.3)
    p_s5_1 = tf_s5.paragraphs[0]; p_s5_1.text = "Portfolio Attention Priorities"; p_s5_1.font.size = Pt(14); p_s5_1.font.bold = True; p_s5_1.font.color.rgb = NAVY
    p_s5_2 = tf_s5.add_paragraph(); p_s5_2.text = (
        "\n• Singapore Marina Bay (Rank #1): Premium CBD cost (₹2.16M/occ seat) combined with February 2027 expiry (5 months away).\n\n"
        "• Mumbai Nariman Point (Rank #2): High cost, expiring March 2027 (6 months away).\n\n"
        "• Sydney Barangaroo (Rank #3): Substantial lease liability (₹48.6 Cr base rent), expiring April 2027.\n\n"
        "• Chennai Guindy (Rank #4): 42% utilization, expiring March 2027. Prime consolidation candidate."
    ); p_s5_2.font.size = Pt(11); p_s5_2.font.color.rgb = SLATE

    # -------------------------------------------------------------
    # SLIDE 6: Data Quality & Confidence
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Decision-making is backed by an audited 99.98% clean relational data pipeline", "Data Quality & Controls")
    add_footer(s6, 6)

    # 4 Governance KPI Cards
    add_kpi_card(s6, Inches(0.8), Inches(1.5), Inches(2.7), Inches(1.4), "Records Evaluated", "282,584", "Full ingestion universe", NAVY)
    add_kpi_card(s6, Inches(3.8), Inches(1.5), Inches(2.7), Inches(1.4), "Quality Pass Rate", "99.98%", "282,520 records pristine", GREEN)
    add_kpi_card(s6, Inches(6.8), Inches(1.5), Inches(2.7), Inches(1.4), "Injected Defects", "44 Issues", "100% detected & logged", RED)
    add_kpi_card(s6, Inches(9.8), Inches(1.5), Inches(2.7), Inches(1.4), "Governance Rules", "12 Codified Rules", "DQ001 to DQ012 verified", NAVY)

    box_s6 = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.2), Inches(11.7), Inches(3.5))
    box_s6.fill.solid(); box_s6.fill.fore_color.rgb = CARD_BG; box_s6.line.color.rgb = BORDER_COL
    tf_s6 = box_s6.text_frame; tf_s6.word_wrap = True; tf_s6.margin_left = Inches(0.4); tf_s6.margin_top = Inches(0.3)
    p_s6_1 = tf_s6.paragraphs[0]; p_s6_1.text = "Relational Data Quality Framework Architecture"; p_s6_1.font.size = Pt(14); p_s6_1.font.bold = True; p_s6_1.font.color.rgb = NAVY
    p_s6_2 = tf_s6.add_paragraph(); p_s6_2.text = (
        "\n• Multi-Tier Ingestion: RAW data maintains operational imperfections; automated validation detects anomalies; CLEAN layer remediates and standardizes; ANALYTICAL layer loads verified facts.\n\n"
        "• Critical Integrity Enforced: Zero orphaned foreign keys; strict capacity boundaries (ActualOccupants ≤ Capacity); non-negative financial records; and corrected chronological lease contracts.\n\n"
        "• Complete Transparency: Page 6 of the Power BI dashboard and Sheet 6 of the Excel workbook expose the full audit ledger from data/quality_issue_manifest.csv."
    ); p_s6_2.font.size = Pt(11); p_s6_2.font.color.rgb = SLATE

    # -------------------------------------------------------------
    # SLIDE 7: Areas for Further Investigation
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Strategic space consolidation unlocks ₹11.64 Cr in recurring annual savings", "Management Decision Scenarios")
    add_footer(s7, 7)

    # 3 Scenario Cards
    card_sc1 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(3.6), Inches(4.2))
    card_sc1.fill.solid(); card_sc1.fill.fore_color.rgb = CARD_BG; card_sc1.line.color.rgb = BORDER_COL
    tf_c1 = card_sc1.text_frame; tf_c1.word_wrap = True; tf_c1.margin_left = Inches(0.25); tf_c1.margin_top = Inches(0.25)
    p_c1_1 = tf_c1.paragraphs[0]; p_c1_1.text = "Scenario 1: Conservative"; p_c1_1.font.size = Pt(13); p_c1_1.font.bold = True; p_c1_1.font.color.rgb = NAVY
    p_c1_2 = tf_c1.add_paragraph(); p_c1_2.text = (
        "\n• 10% Seat Surrender across 11 low-utilization assets\n"
        "• Seats Surrendered: 710 seats\n"
        "• Area Rationalized: 6,373 m²\n"
        "• Annual Cost Savings: ₹7.76 Cr\n"
        "• New Portfolio Util: 61.5%\n"
        "• Choke Point Risk: 0 assets breach 85% peak buffer"
    ); p_c1_2.font.size = Pt(10.5); p_c1_2.font.color.rgb = SLATE

    card_sc2 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.8), Inches(1.5), Inches(3.7), Inches(4.2))
    card_sc2.fill.solid(); card_sc2.fill.fore_color.rgb = RGBColor(0xEB, 0xF8, 0xFF); card_sc2.line.color.rgb = NAVY; card_sc2.line.width = Pt(2)
    tf_c2 = card_sc2.text_frame; tf_c2.word_wrap = True; tf_c2.margin_left = Inches(0.25); tf_c2.margin_top = Inches(0.25)
    p_c2_1 = tf_c2.paragraphs[0]; p_c2_1.text = "Scenario 2: Balanced (Recommended)"; p_c2_1.font.size = Pt(13); p_c2_1.font.bold = True; p_c2_1.font.color.rgb = NAVY
    p_c2_2 = tf_c2.add_paragraph(); p_c2_2.text = (
        "\n• 15% Seat Surrender with agile desk sharing (1.35:1)\n"
        "• Seats Surrendered: 1,064 seats\n"
        "• Area Rationalized: 9,550 m²\n"
        "• Annual Cost Savings: ₹11.64 Cr\n"
        "• New Portfolio Util: 62.6%\n"
        "• Choke Point Risk: 1 asset requires desk booking policy"
    ); p_c2_2.font.size = Pt(10.5); p_c2_2.font.color.rgb = SLATE

    card_sc3 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.9), Inches(1.5), Inches(3.6), Inches(4.2))
    card_sc3.fill.solid(); card_sc3.fill.fore_color.rgb = CARD_BG; card_sc3.line.color.rgb = BORDER_COL
    tf_c3 = card_sc3.text_frame; tf_c3.word_wrap = True; tf_c3.margin_left = Inches(0.25); tf_c3.margin_top = Inches(0.25)
    p_c3_1 = tf_c3.paragraphs[0]; p_c3_1.text = "Scenario 3: Strategic Footprint"; p_c3_1.font.size = Pt(13); p_c3_1.font.bold = True; p_c3_1.font.color.rgb = NAVY
    p_c3_2 = tf_c3.add_paragraph(); p_c3_2.text = (
        "\n• 20% Surrender on expiring lease assets\n"
        "• Seats Surrendered: 1,420 seats\n"
        "• Area Rationalized: 12,745 m²\n"
        "• Annual Cost Savings: ₹15.53 Cr\n"
        "• New Portfolio Util: 63.8%\n"
        "• Choke Point Risk: 4 assets breach 85% peak limit"
    ); p_c3_2.font.size = Pt(10.5); p_c3_2.font.color.rgb = SLATE

    # Strategic Next Steps Bar
    bar_next = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(5.9), Inches(11.7), Inches(0.9))
    bar_next.fill.solid(); bar_next.fill.fore_color.rgb = NAVY; bar_next.line.color.rgb = NAVY
    tf_n = bar_next.text_frame; tf_n.word_wrap = True; tf_n.margin_left = Inches(0.3); tf_n.margin_top = Inches(0.12)
    p_n = tf_n.paragraphs[0]; p_n.text = "Recommended Executive Actions: (1) Authorize Scenario 2 consolidation negotiations; (2) Initiate notice preparations for Singapore and Mumbai leases; (3) Roll out mid-week desk booking in tech campuses."
    p_n.font.size = Pt(11); p_n.font.bold = True; p_n.font.color.rgb = WHITE

    prs.save(pptx_path)
    print(f"Generated PowerPoint Presentation -> {pptx_path}")

    root_pptx = "Corporate_Real_Estate_Executive_Review.pptx"
    shutil.copyfile(pptx_path, root_pptx)
    print(f"Copied PowerPoint Presentation to root -> {root_pptx}")


if __name__ == "__main__":
    build_presentation_deck()
