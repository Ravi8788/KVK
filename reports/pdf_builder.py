from datetime import datetime
from typing import Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PDFBuilder:
    """Builds report PDFs from activity record dictionaries."""

    @staticmethod
    def build_activity_report(
        records: List[Dict],
        output_path: str,
        title: str,
        columns: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        kvk_name: str = "Krishi Vigyan Kendra",
        kvk_address: str = "",
        filter_text: str = "",
    ) -> str:
        columns = columns or [
            "sr_no",
            "module_type",
            "farmer_name",
            "village",
            "district",
            "tehsil",
            "contact_number",
            "activity_date",
            "department",
            "season",
            "activity_type",
        ]
        headers = headers or {}
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            leftMargin=18,
            rightMargin=18,
            topMargin=18,
            bottomMargin=28,
        )
        styles = getSampleStyleSheet()
        cell_style = ParagraphStyle(
            "ReportCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#1c2b1e"),
        )
        header_style = ParagraphStyle(
            "ReportHeader",
            parent=cell_style,
            fontName="Helvetica-Bold",
            textColor=colors.white,
        )
        story = [
            Paragraph(kvk_name or "Krishi Vigyan Kendra", styles["Title"]),
            Paragraph(title, styles["Heading2"]),
            Spacer(1, 4),
        ]
        if kvk_address:
            story.append(Paragraph(kvk_address, styles["Normal"]))
        if filter_text:
            story.append(Paragraph(f"Filters: {filter_text}", styles["Normal"]))
        story.extend(
            [
                Paragraph(f"Generated on: {datetime.now():%d-%m-%Y %H:%M}", styles["Normal"]),
                Spacer(1, 8),
            ]
        )

        def cell(value, style):
            text = "" if value is None else str(value)
            return Paragraph(text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), style)

        table_data = [[cell(headers.get(column, column), header_style) for column in columns]]
        for row in records:
            table_data.append([cell(row.get(column, ""), cell_style) for column in columns])

        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#217a45")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#c5dcc8")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4faf5")]),
                ]
            )
        )
        story.append(table)

        def _page(canvas, doc_template):
            canvas.saveState()
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(colors.HexColor("#225d36"))
            canvas.drawString(18, 14, kvk_name or "Krishi Vigyan Kendra")
            canvas.drawRightString(doc_template.pagesize[0] - 18, 14, f"Page {doc_template.page}")
            canvas.restoreState()

        doc.build(story, onFirstPage=_page, onLaterPages=_page)
        return output_path
