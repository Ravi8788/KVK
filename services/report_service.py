import csv
import json
import os
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_

from database.session import SessionLocal
from models.entities import Activity, Department, Farmer, Report
from reports.pdf_builder import PDFBuilder
from services.audit_service import AuditService


class ReportService:
    """Filtering, tabular retrieval, and file export for reports."""

    @staticmethod
    def _is_oft_style_module(module_type: str) -> bool:
        return module_type in {"On Farm Testing (OFT)", "Front Line Demonstrations (FLD)"}

    @staticmethod
    def _normalize_optional_text(value: Optional[str]) -> str:
        text_value = (value or "").strip()
        return text_value if text_value else "N/A"

    @staticmethod
    def _parse_oft_technical_assessment(value: Optional[str]) -> Dict[str, str]:
        raw = (value or "").strip()
        parsed = {"oft_t1": "", "oft_t2": "", "oft_t3": ""}
        found_labeled_value = False

        for line in raw.splitlines():
            label, separator, text = line.partition(":")
            key = label.strip().lower()
            if separator and key in {"t1", "t2", "t3"}:
                parsed[f"oft_{key}"] = text.strip()
                found_labeled_value = True

        if raw and not found_labeled_value:
            parsed["oft_t1"] = raw

        return {
            "oft_t1": ReportService._normalize_optional_text(parsed["oft_t1"]),
            "oft_t2": ReportService._normalize_optional_text(parsed["oft_t2"]),
            "oft_t3": ReportService._normalize_optional_text(parsed["oft_t3"]),
        }

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
        elif module_type == "On Farm Testing (OFT)" and (
            department_name != "Agronomy" or activity_value == "Refinement"
        ):
            display_season = "N/A"
        elif not season_value or season_value.lower() in {"not required", "na", "n/a", "none", "null"}:
            display_season = "N/A"
        else:
            display_season = season_value

        if module_type in ["Training Programmes", "Vocational Training Programmes"]:
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
    def _has_meaningful_value(record: Dict, key: str) -> bool:
        value = record.get(key)
        if value is None:
            return False
        text = str(value).strip()
        return text not in {"", "N/A", "None", "null"}

    @staticmethod
    def _export_columns(records: List[Dict], filters: Optional[Dict] = None) -> List[str]:
        module_type = (filters or {}).get("module_type", "All")
        include_department = (filters or {}).get("department_id") is None
        modules_in_records = {str(row.get("module_type", "")).strip() for row in records if str(row.get("module_type", "")).strip()}

        # If filtered as All but current result set contains only one module, use that module schema.
        if module_type == "All" and len(modules_in_records) == 1:
            only_module = next(iter(modules_in_records))
            module_type = only_module

        if ReportService._is_oft_style_module(module_type):
            columns = [
                "sr_no",
                "activity_date",
                "oft_title",
                "oft_crop_variety",
                "oft_farmer_count",
                "farmer_name",
                "village",
                "contact_number",
                "oft_farmer_scientist",
                "oft_farmer_purpose",
                "oft_farmer_district",
                "oft_farmer_tehsil",
            ]
            if module_type == "On Farm Testing (OFT)":
                columns.extend(["oft_t1", "oft_t2", "oft_t3"])
            columns.append("oft_area")
            if include_department:
                columns.append("department")
            columns.extend(["activity_type", "season"])
            return columns

        if module_type == "Visitor Farmers":
            return [
                "sr_no",
                "module_type",
                "activity_date",
                "department",
                "farmer_name",
                "village",
                "district",
                "tehsil",
                "contact_number",
                "activity_type",
                "description",
                "remarks",
            ]

        if module_type in ["Training Programmes", "Vocational Training Programmes"]:
            return [
                "sr_no",
                "module_type",
                "training_title",
                "activity_date",
                "training_end_date",
                "department",
                "training_type",
                "venue",
                "venue_is_offline",
                "venue_village",
                "venue_taluka",
                "venue_district",
                "clientele",
                "training_farmer_count",
                "farmer_name",
                "village",
                "contact_number",
                "training_farmer_scientist",
                "training_farmer_purpose",
                "training_farmer_category",
                "training_farmer_district",
                "training_farmer_tehsil",
                "description",
                "remarks",
            ]

        if module_type == "Extension Activities":
            return [
                "sr_no",
                "module_type",
                "activity_date",
                "activity_type",
                "extension_venue",
                "extension_location",
                "extension_department",
                "extension_purpose",
                "extension_farmer_count",
            ]

        if module_type == "Other Extension Activities":
            return [
                "sr_no",
                "module_type",
                "activity_date",
                "activity_type",
                "other_extension_title",
            ]

        if module_type and module_type != "All":
            return [
                "sr_no",
                "module_type",
                "activity_date",
                "department",
                "season",
                "activity_type",
                "farmer_name",
                "village",
                "contact_number",
                "description",
                "remarks",
            ]

        columns = [
            "sr_no",
            "module_type",
            "activity_date",
            "department",
            "season",
            "activity_type",
            "farmer_name",
            "village",
            "contact_number",
            "district",
            "tehsil",
        ]

        optional_columns = [
            "oft_title",
            "oft_crop_variety",
            "oft_farmer_count",
            "oft_farmer_scientist",
            "oft_farmer_purpose",
            "oft_t1",
            "oft_t2",
            "oft_t3",
            "oft_area",
            "training_title",
            "training_end_date",
            "training_type",
            "venue",
            "venue_is_offline",
            "venue_village",
            "venue_taluka",
            "venue_district",
            "clientele",
            "training_farmer_count",
            "training_farmer_category",
            "training_farmer_scientist",
            "training_farmer_purpose",
            "training_farmer_district",
            "training_farmer_tehsil",
            "extension_venue",
            "extension_location",
            "extension_department",
            "extension_purpose",
            "extension_farmer_count",
            "other_extension_title",
            "description",
            "remarks",
        ]

        for col in optional_columns:
            if any(ReportService._has_meaningful_value(row, col) for row in records):
                columns.append(col)

        return columns

    @staticmethod
    def _export_header_labels() -> Dict[str, str]:
        return {
            "sr_no": "Sr No",
            "module_type": "Module",
            "activity_date": "Date",
            "department": "Department",
            "season": "Season",
            "activity_type": "Activity",
            "farmer_name": "Farmer Name",
            "village": "Farmer Village",
            "district": "District",
            "tehsil": "Tehsil",
            "contact_number": "Mobile No.",
            "description": "Description",
            "remarks": "Remarks",
            "oft_title": "Title of OFT",
            "oft_crop_variety": "Crop Variety",
            "oft_farmer_count": "No. of Farmers",
            "oft_farmer_scientist": "Scientist",
            "oft_farmer_purpose": "Purpose",
            "oft_farmer_district": "District",
            "oft_farmer_tehsil": "Tehsil",
            "oft_t1": "t1",
            "oft_t2": "t2",
            "oft_t3": "t3",
            "oft_area": "Area",
            "training_title": "Training Title",
            "training_type": "Training Type",
            "training_end_date": "End Date",
            "clientele": "Clientele",
            "venue": "Venue",
            "venue_is_offline": "Venue Mode",
            "venue_village": "Venue Village",
            "venue_taluka": "Venue Taluka",
            "venue_district": "Venue District",
            "training_farmer_count": "No. of Farmers",
            "training_farmer_category": "Category",
            "training_farmer_scientist": "Scientist",
            "training_farmer_purpose": "Purpose",
            "training_farmer_district": "Farmer District",
            "training_farmer_tehsil": "Farmer Tehsil",
            "extension_venue": "Venue",
            "extension_location": "Location",
            "extension_department": "Department",
            "extension_purpose": "Purpose of Visit",
            "extension_farmer_count": "No. of Farmers",
            "other_extension_title": "Title of Show",
        }

    @staticmethod
    def get_visible_columns(records: List[Dict], filters: Optional[Dict] = None) -> List[str]:
        return ReportService._export_columns(records, filters)

    @staticmethod
    def get_header_labels(filters: Optional[Dict] = None) -> Dict[str, str]:
        labels = ReportService._export_header_labels().copy()
        module_type = (filters or {}).get("module_type", "All")
        if module_type == "On Farm Testing (OFT)":
            labels["oft_title"] = "Title of OFT"
        elif module_type == "Front Line Demonstrations (FLD)":
            labels["oft_title"] = "Title of FLD"
        else:
            labels["oft_title"] = "Title"
        return labels

    @staticmethod
    def query_records(
        start_date: Optional[date],
        end_date: Optional[date],
        department_id: Optional[int],
        module_type: Optional[str],
        mobile_number: Optional[str] = None,
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
            if start_date and end_date:
                conditions.append(
                    or_(
                        and_(Activity.activity_date >= start_date, Activity.activity_date <= end_date),
                        and_(func.date(Activity.created_at) >= start_date, func.date(Activity.created_at) <= end_date),
                    )
                )
            if department_id:
                conditions.append(Activity.department_id == department_id)
            if module_type and module_type != "All":
                conditions.append(Activity.module_type == module_type)
            if mobile_number:
                conditions.append(Farmer.contact_number.ilike(f"%{mobile_number}%"))

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
            serial_start = (page - 1) * page_size
            for activity, farmer, department in rows:
                normalized = ReportService._normalize_report_row(
                    module_type=activity.module_type,
                    department_name=department.name,
                    season=activity.season,
                    activity_type=activity.activity_type,
                )
                if activity.module_type == "Visitor Farmers":
                    raw_district = (activity.visitor_district or "").strip()
                    raw_tehsil = (activity.visitor_tehsil or "").strip()
                    if not raw_district and not raw_tehsil:
                        location_parts = ReportService._extract_district_tehsil(activity.module_type, activity.remarks)
                    else:
                        location_parts = {
                            "district": ReportService._normalize_optional_text(raw_district),
                            "tehsil": ReportService._normalize_optional_text(raw_tehsil),
                        }
                elif ReportService._is_oft_style_module(activity.module_type):
                    location_parts = {
                        "district": ReportService._normalize_optional_text(activity.oft_farmer_district),
                        "tehsil": ReportService._normalize_optional_text(activity.oft_farmer_tehsil),
                    }
                elif activity.module_type in ["Training Programmes", "Vocational Training Programmes"]:
                    location_parts = {
                        "district": ReportService._normalize_optional_text(activity.training_farmer_district),
                        "tehsil": ReportService._normalize_optional_text(activity.training_farmer_tehsil),
                    }
                else:
                    location_parts = {"district": "N/A", "tehsil": "N/A"}
                description_text = activity.description or activity.visitor_scientist
                remarks_text = activity.remarks
                if activity.module_type == "Visitor Farmers" and not remarks_text:
                    remarks_text = (
                        f"District: {ReportService._normalize_optional_text(activity.visitor_district)} | "
                        f"Tehsil: {ReportService._normalize_optional_text(activity.visitor_tehsil)}"
                    ).strip()
                farmer_name = "N/A" if activity.module_type in [
                    "Extension Activities",
                    "Other Extension Activities",
                ] else ReportService._normalize_optional_text(farmer.farmer_name)
                oft_technical_parts = ReportService._parse_oft_technical_assessment(activity.oft_technical_assessment)
                venue_mode = "Off" if activity.venue_is_offline else "On"
                data.append(
                    {
                        "sr_no": serial_start + len(data) + 1,
                        "module_type": activity.module_type,
                        "farmer_name": farmer_name,
                        "village": ReportService._normalize_optional_text(farmer.village),
                        "district": location_parts["district"],
                        "tehsil": location_parts["tehsil"],
                        "contact_number": ReportService._normalize_optional_text(farmer.contact_number),
                        "activity_date": activity.activity_date,
                        "department": ReportService._normalize_optional_text(department.name),
                        "season": normalized["season"],
                        "activity_type": normalized["activity_type"],
                        "description": ReportService._normalize_optional_text(description_text),
                        "remarks": ReportService._normalize_optional_text(remarks_text),
                        "oft_title": ReportService._normalize_optional_text(activity.oft_title),
                        "oft_crop_variety": ReportService._normalize_optional_text(activity.oft_crop_variety),
                        "oft_farmer_count": activity.oft_farmer_count if activity.oft_farmer_count is not None else "N/A",
                        "oft_technical_assessment": ReportService._normalize_optional_text(activity.oft_technical_assessment),
                        "oft_t1": oft_technical_parts["oft_t1"],
                        "oft_t2": oft_technical_parts["oft_t2"],
                        "oft_t3": oft_technical_parts["oft_t3"],
                        "oft_area": ReportService._normalize_optional_text(activity.oft_area),
                        "oft_farmer_scientist": ReportService._normalize_optional_text(activity.oft_farmer_scientist),
                        "oft_farmer_purpose": ReportService._normalize_optional_text(activity.oft_farmer_purpose),
                        "oft_farmer_district": ReportService._normalize_optional_text(activity.oft_farmer_district),
                        "oft_farmer_tehsil": ReportService._normalize_optional_text(activity.oft_farmer_tehsil),
                        "training_title": ReportService._normalize_optional_text(activity.training_title),
                        "training_type": ReportService._normalize_optional_text(activity.training_type),
                        "training_end_date": activity.training_end_date if activity.training_end_date else "N/A",
                        "clientele": ReportService._normalize_optional_text(activity.clientele),
                        "venue": ReportService._normalize_optional_text(activity.venue),
                        "venue_is_offline": venue_mode if activity.module_type in ["Training Programmes", "Vocational Training Programmes"] else "N/A",
                        "venue_village": ReportService._normalize_optional_text(activity.venue_village),
                        "venue_taluka": ReportService._normalize_optional_text(activity.venue_taluka),
                        "venue_district": ReportService._normalize_optional_text(activity.venue_district),
                        "training_farmer_count": activity.training_farmer_count if activity.training_farmer_count is not None else "N/A",
                        "training_farmer_category": ReportService._normalize_optional_text(activity.training_farmer_category),
                        "training_farmer_scientist": ReportService._normalize_optional_text(activity.training_farmer_scientist),
                        "training_farmer_purpose": ReportService._normalize_optional_text(activity.training_farmer_purpose),
                        "training_farmer_district": ReportService._normalize_optional_text(activity.training_farmer_district),
                        "training_farmer_tehsil": ReportService._normalize_optional_text(activity.training_farmer_tehsil),
                        "extension_venue": ReportService._normalize_optional_text(activity.extension_venue),
                        "extension_location": ReportService._normalize_optional_text(activity.extension_location),
                        "extension_department": ReportService._normalize_optional_text(activity.extension_department),
                        "extension_purpose": ReportService._normalize_optional_text(activity.extension_purpose),
                        "extension_farmer_count": activity.extension_farmer_count if activity.extension_farmer_count is not None else "N/A",
                        "other_extension_title": ReportService._normalize_optional_text(activity.other_extension_title),
                    }
                )
            return data, total
        finally:
            session.close()

    @staticmethod
    def export_csv(records: List[Dict], output_path: str, filters: Optional[Dict] = None) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        columns = ReportService._export_columns(records, filters)
        labels = ReportService.get_header_labels(filters)
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writerow({col: labels.get(col, col.replace("_", " ").title()) for col in columns})
            for row in records:
                writer.writerow({col: row.get(col, "") for col in columns})
        return output_path

    @staticmethod
    def export_pdf(records: List[Dict], output_path: str, title: str, filters: Optional[Dict] = None) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        columns = ReportService._export_columns(records, filters)
        labels = ReportService.get_header_labels(filters)
        return PDFBuilder.build_activity_report(records, output_path, title, columns=columns, headers=labels)

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
