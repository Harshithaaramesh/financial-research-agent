"""
pdf_generator.py
----------------
Converts the markdown investment memo into a clean, professional PDF
using ReportLab's Platypus layout engine.

Usage:
    from src.utils.pdf_generator import generate_pdf
    pdf_bytes = generate_pdf(markdown_text, company="JPMorgan Chase", ticker="JPM")
"""

import re
import io
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


# Color palette 
NAVY      = colors.HexColor("#0f2044")
BLUE      = colors.HexColor("#1a56db")
LIGHT_BLUE= colors.HexColor("#e8f0fe")
GRAY      = colors.HexColor("#64748b")
DARK      = colors.HexColor("#1e293b")
WHITE     = colors.white
RULE      = colors.HexColor("#cbd5e1")
GREEN     = colors.HexColor("#16a34a")
RED       = colors.HexColor("#dc2626")


def _build_styles() -> dict:
    """Returns a dict of custom paragraph styles."""
    base = getSampleStyleSheet()

    styles = {
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=WHITE,
            leading=28,
            spaceAfter=6,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#93c5fd"),
            leading=14,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta",
            fontName="Helvetica",
            fontSize=9,
            textColor=colors.HexColor("#94a3b8"),
            leading=13,
        ),
        "section_header": ParagraphStyle(
            "section_header",
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=NAVY,
            leading=16,
            spaceBefore=18,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=DARK,
            leading=15,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=DARK,
            leading=14,
            leftIndent=16,
            spaceAfter=3,
            bulletIndent=6,
        ),
        "bold_label": ParagraphStyle(
            "bold_label",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            textColor=DARK,
            leading=14,
            spaceAfter=2,
        ),
        "footer_text": ParagraphStyle(
            "footer_text",
            fontName="Helvetica",
            fontSize=7.5,
            textColor=GRAY,
            alignment=TA_CENTER,
        ),
    }
    return styles


def _parse_markdown(text: str) -> list[dict]:
    """
    Parses the markdown report into a list of typed segments.
    Returns list of {"type": ..., "content": ...} dicts.
    Types: h1, h2, bullet, bold_inline, body
    """
    segments = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            segments.append({"type": "space"})
        elif stripped.startswith("# "):
            segments.append({"type": "h1", "content": stripped[2:]})
        elif stripped.startswith("## "):
            segments.append({"type": "h2", "content": stripped[3:]})
        elif stripped.startswith("### "):
            segments.append({"type": "h2", "content": stripped[4:]})
        elif stripped.startswith("- ") or stripped.startswith("* "):
            content = stripped[2:]
            # Handle **bold** inside bullets
            content = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", content)
            segments.append({"type": "bullet", "content": content})
        else:
            # Inline bold
            content = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", stripped)
            segments.append({"type": "body", "content": content})
    return segments


class _PageTemplate:
    """Handles header and footer on every page."""

    def __init__(self, company: str, ticker: str, date_str: str):
        self.company = company
        self.ticker = ticker
        self.date_str = date_str

    def __call__(self, canvas, doc):
        canvas.saveState()
        w, h = letter

        # Header bar
        canvas.setFillColor(NAVY)
        canvas.rect(0, h - 36, w, 36, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(0.5 * inch, h - 22, f"Financial Research Memo  |  {self.company} ({self.ticker})")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#93c5fd"))
        canvas.drawRightString(w - 0.5 * inch, h - 22, self.date_str)

        # Footer
        canvas.setFillColor(RULE)
        canvas.rect(0.5 * inch, 0.45 * inch, w - inch, 0.5, fill=1, stroke=0)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(GRAY)
        canvas.drawString(0.5 * inch, 0.3 * inch,
                          "Generated by Financial Research Assistant · Powered by RAG + LangGraph · For informational purposes only.")
        canvas.drawRightString(w - 0.5 * inch, 0.3 * inch, f"Page {doc.page}")

        canvas.restoreState()


def generate_pdf(markdown_text: str, company: str, ticker: str) -> bytes:
    """
    Converts a markdown investment memo into a styled PDF.

    Args:
        markdown_text: The full markdown report string.
        company:       Company name, e.g. 'JPMorgan Chase'
        ticker:        Stock ticker, e.g. 'JPM'

    Returns:
        PDF file as bytes (ready to write to disk or return as download).
    """
    buffer = io.BytesIO()
    date_str = datetime.now().strftime("%B %d, %Y")

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = _build_styles()
    page_cb = _PageTemplate(company, ticker, date_str)
    story = []

    # Cover block 
    cover_data = [[
        Paragraph(f"Investment Research Memo", styles["cover_title"]),
        Paragraph(company, styles["cover_title"]),
        Spacer(1, 4),
        Paragraph(f"Ticker: {ticker.upper()}   ·   Filed: {date_str}", styles["cover_sub"]),
        Spacer(1, 4),
        Paragraph(
            "Generated by Financial Research Assistant using Multi-Agent AI (RAG + LangGraph + LLaMA 3)",
            styles["cover_meta"]
        ),
    ]]

    cover_table = Table([[cover_data[0]]], colWidths=[doc.width])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ("ROUNDEDCORNERS", (0, 0), (-1, -1), [8, 8, 8, 8]),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 18))

    # Body 
    segments = _parse_markdown(markdown_text)

    for seg in segments:
        t = seg["type"]

        if t == "h1":
            # Skip — already in cover
            pass

        elif t == "h2":
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=4))
            # Section label pill
            label_data = [[Paragraph(seg["content"].upper(), ParagraphStyle(
                "sec_label",
                fontName="Helvetica-Bold",
                fontSize=8.5,
                textColor=BLUE,
                leading=12,
            ))]]
            label_table = Table(label_data, colWidths=[doc.width])
            label_table.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_BLUE),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ("ROUNDEDCORNERS",(0, 0), (-1, -1), [4, 4, 4, 4]),
            ]))
            story.append(KeepTogether([label_table, Spacer(1, 6)]))

        elif t == "bullet":
            story.append(Paragraph(f"• {seg['content']}", styles["bullet"]))

        elif t == "body":
            if seg["content"].strip():
                story.append(Paragraph(seg["content"], styles["body"]))

        elif t == "space":
            story.append(Spacer(1, 4))

    # Disclaimer 
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=RULE))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Disclaimer:</b> This report was generated automatically by an AI system using publicly available "
        "SEC filings and news data. It is for informational and educational purposes only and does not "
        "constitute financial, investment, or legal advice. Always consult a qualified financial advisor "
        "before making investment decisions.",
        ParagraphStyle("disclaimer", fontName="Helvetica", fontSize=7.5,
                       textColor=GRAY, leading=11)
    ))

    doc.build(story, onFirstPage=page_cb, onLaterPages=page_cb)
    return buffer.getvalue()
