import csv
import json
import os
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_

from database.session import SessionLocal
from models.entities import Activity, Department, Farmer, Report
from reports.pdf_builder import PDFBuilder
from services.audit_service import AuditService


class ReportService:
    """Filtering, tabular retrieval, and file export for reports."""

    @staticmethod
    def _normalize_optional_text(value: Optional[str]) -> str:
        text_value = (value or "").strip()
        return text_value if text_value else "N/A"

    @staticmethod
    def _normalize_report_row(module_type: str, department_name: str, season: Optional[str], activity_type: Optional[str]) -> Dict[str, str]:
        season_value = (season or "").strip()
        activity_value = (activity_type or "").strip()

        if module_type in [
            "Training Programmes",
            "Vocational Training Programmes",
            "Extension Activities",
            "Other Extension Activities",
        ]:
            display_season = "N/A"
        elif module_type == "Front Line Demonstrations (FLD)" and department_name != "Horticulture":
            display_season = "N/A"
        elif module_type == "On Farm Testing (OFT)" and (
            department_name != "Agronomy" or activity_value == "Refinement"
        ):
            display_season = "N/A"
        elif not season_value or season_value.lower() in {"not required", "na", "n/a", "none", "null"}:
            display_season = "N/A"
        else:
            display_season = season_value

        if module_type in ["Front Line Demonstrations (FLD)", "Training Programmes", "Vocational Training Programmes"]:
            display_activity = "N/A"
        elif module_type == "On Farm Testing (OFT)" and department_name != "Agronomy":
            display_activity = "N/A"
        elif not activity_value or activity_value.lower() in {
            "not applicable",
            "not required",
            "na",
            "n/a",
            "none",
            "null",
            "select activity type",
            "select department first",
            "general oft",
        }:
            display_activity = "N/A"
        else:
            display_activity = activity_value

        return {"season": display_season, "activity_type": display_activity}

    @staticmethod
    def _extract_district_tehsil(module_type: str, remarks: Optional[str]) -> Dict[str, str]:
        if module_type != "Visitor Farmers":
            return {"district": "N/A", "tehsil": "N/A"}

        raw = (remarks or "").strip()
        tehsil_value = "N/A"
        district_value = "N/A"

        if "District:" in raw and "| Tehsil:" in raw:
            district_part, tehsil_part = raw.split("| Tehsil:", 1)
            district_value = district_part.replace("District:", "").strip() or "N/A"
            tehsil_value = tehsil_part.strip() or "N/A"
        elif "Tehsil:" in raw and "| District:" in raw:
            # Backward compatibility for older data.
            tehsil_part, district_part = raw.split("| District:", 1)
            tehsil_value = tehsil_part.replace("Tehsil:", "").strip() or "N/A"
            district_value = district_part.strip() or "N/A"

        return {"district": district_value, "tehsil": tehsil_value}

    @staticmethod
    def _serialize_for_json(value):
        """Converts date-like and nested values into JSON-safe primitives."""
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if isinstance(value, dict):
            return {k: ReportService._serialize_for_json(v) for k, v in value.items()}
        if isinstance(value, list):
            return [ReportService._serialize_for_json(item) for item in value]
        if isinstance(value, tuple):
            return [ReportService._serialize_for_json(item) for item in value]
        return value

    @staticmethod
    def query_records(
        start_date: Optional[date],
        end_date: Optional[date],
        department_id: Optional[int],
        module_type: Optional[str],
        page: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[Dict], int]:
        session = SessionLocal()
        try:
            query = (
                session.query(Activity, Farmer, Department)
                .join(Farmer, Activity.farmer_id == Farmer.id)
                .join(Department, Activity.department_id == Department.id)
            )

            conditions = []
            if start_date:
                conditions.append(Activity.activity_date >= start_date)
            if end_date:
                conditions.append(Activity.activity_date <= end_date)
            if department_id:
                conditions.append(Activity.department_id == department_id)
            if module_type and module_type != "All":
                conditions.append(Activity.module_type == module_type)

            if conditions:
                query = query.filter(and_(*conditions))

            total = query.count()
            rows = (
                query.order_by(Activity.activity_date.desc(), Activity.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            data: List[Dict] = []
            for activity, farmer, department in rows:
                normalized = ReportService._normalize_report_row(
                    module_type=activity.module_type,
                    department_name=department.name,
                    season=activity.season,
                    activity_type=activity.activity_type,
                )
                location_parts = ReportService._extract_district_tehsil(activity.module_type, activity.remarks)
                data.append(
                    {
                        "id": activity.id,
                        "module_type": activity.module_type,
                        "farmer_name": ReportService._normalize_optional_text(farmer.farmer_name),
                        "village": ReportService._normalize_optional_text(farmer.village),
                        "district": location_parts["district"],
                        "tehsil": location_parts["tehsil"],
                        "contact_number": ReportService._normalize_optional_text(farmer.contact_number),
                        "activity_date": activity.activity_date,
                        "department": ReportService._normalize_optional_text(department.name),
                        "season": normalized["season"],
                        "activity_type": normalized["activity_type"],
                        "description": ReportService._normalize_optional_text(activity.description),
                        "remarks": ReportService._normalize_optional_text(activity.remarks),
                    }
                )
            return data, total
        finally:
            session.close()

    @staticmethod
    def export_csv(records: List[Dict], output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        columns = [
            "id",
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
            "description",
            "remarks",
        ]
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            for row in records:
                writer.writerow(row)
        return output_path

    @staticmethod
    def export_pdf(records: List[Dict], output_path: str, title: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        return PDFBuilder.build_activity_report(records, output_path, title)

    @staticmethod
    def record_report_generation(
        user_id: int,
        report_name: str,
        filters: Dict,
        file_path: str,
    ) -> None:
        session = SessionLocal()
        try:
            safe_filters = ReportService._serialize_for_json(filters)
            report = Report(
                report_name=report_name,
                generated_by=user_id,
                filter_json=json.dumps(safe_filters),
                file_path=file_path,
            )
            session.add(report)
            session.commit()
            AuditService.log_action(
                user_id=user_id,
                action="generate_report",
                module_type="Reports",
                record_id=report.id,
                details=f"Generated report file: {file_path}",
            )
        finally:
            session.close()
