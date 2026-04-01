from datetime import datetime
from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PDFBuilder:
    """Builds report PDFs from activity record dictionaries."""

    @staticmethod
    def build_activity_report(records: List[Dict], output_path: str, title: str) -> str:
        doc = SimpleDocTemplate(output_path, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        story = [
            Paragraph(title, styles["Title"]),
            Spacer(1, 12),
            Paragraph(f"Generated On: {datetime.now():%Y-%m-%d %H:%M:%S}", styles["Normal"]),
            Spacer(1, 12),
        ]

        table_data = [[
            "ID",
            "Module",
            "Farmer",
            "Village",
            "District",
            "Tehsil",
            "Contact",
            "Date",
            "Department",
            "Season",
            "Activity",
        ]]

        for row in records:
            table_data.append(
                [
                    str(row["id"]),
                    row["module_type"],
                    row["farmer_name"],
                    row["village"],
                    row.get("district", "N/A"),
                    row.get("tehsil", "N/A"),
                    row["contact_number"],
                    str(row["activity_date"]),
                    row["department"],
                    row["season"],
                    row["activity_type"],
                ]
            )

        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E8B57")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ]
            )
        )
        story.append(table)
        doc.build(story)
        return output_path
