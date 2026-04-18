from datetime import date
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, or_

from database.session import SessionLocal
from models.entities import Activity, Department, Farmer
from services.audit_service import AuditService


class ActivityService:
    """CRUD operations for farmer activities across all modules."""

    MODULES = [
        "Visitor Farmers",
        "On Farm Testing (OFT)",
        "Front Line Demonstrations (FLD)",
        "Training Programmes",
        "Vocational Training Programmes",
        "Extension Activities",
        "Other Extension Activities",
    ]

    @staticmethod
    def list_departments() -> List[Department]:
        session = SessionLocal()
        try:
            return session.query(Department).order_by(Department.name.asc()).all()
        finally:
            session.close()

    @staticmethod
    def list_villages() -> List[str]:
        session = SessionLocal()
        try:
            rows = (
                session.query(Farmer.village)
                .filter(Farmer.village.isnot(None))
                .distinct()
                .order_by(Farmer.village.asc())
                .all()
            )
            return [village for (village,) in rows if (village or "").strip()]
        finally:
            session.close()

    @staticmethod
    def _extract_district_tehsil(remarks: Optional[str]) -> Tuple[str, str]:
        raw = (remarks or "").strip()
        district_value = ""
        tehsil_value = ""

        if "District:" in raw and "| Tehsil:" in raw:
            district_part, tehsil_part = raw.split("| Tehsil:", 1)
            district_value = district_part.replace("District:", "").strip()
            tehsil_value = tehsil_part.strip()
        elif "Tehsil:" in raw and "| District:" in raw:
            # Backward compatibility for older saved records.
            tehsil_part, district_part = raw.split("| District:", 1)
            tehsil_value = tehsil_part.replace("Tehsil:", "").strip()
            district_value = district_part.strip()

        return district_value, tehsil_value

    @staticmethod
    def list_villages_for_visitor(district: str, tehsil: str) -> List[str]:
        district = (district or "").strip()
        tehsil = (tehsil or "").strip()
        if not district or not tehsil:
            return []

        session = SessionLocal()
        try:
            rows = (
                session.query(Farmer.village, Activity.remarks)
                .join(Activity, Activity.farmer_id == Farmer.id)
                .filter(Activity.module_type == "Visitor Farmers")
                .all()
            )

            matched = set()
            for village, remarks in rows:
                if not (village or "").strip():
                    continue
                row_district, row_tehsil = ActivityService._extract_district_tehsil(remarks)
                if row_district == district and row_tehsil == tehsil:
                    matched.add(village.strip())

            return sorted(matched)
        finally:
            session.close()

    @staticmethod
    def _extract_oft_district_tehsil(remarks: Optional[str]) -> Tuple[str, str]:
        raw = (remarks or "").strip()
        if not raw.startswith("OFT_META|"):
            return "", ""

        payload = raw[len("OFT_META|"):]
        district_value = ""
        tehsil_value = ""
        for part in payload.split("|"):
            if part.startswith("District:"):
                district_value = part.replace("District:", "", 1).strip()
            elif part.startswith("Tehsil:"):
                tehsil_value = part.replace("Tehsil:", "", 1).strip()
            elif part.startswith("Taluka:"):
                # Backward compatibility for older OFT metadata.
                tehsil_value = part.replace("Taluka:", "", 1).strip()

        return district_value, tehsil_value

    @staticmethod
    def list_villages_for_oft(district: str, tehsil: str) -> List[str]:
        district = (district or "").strip()
        tehsil = (tehsil or "").strip()
        if not district or not tehsil:
            return []

        session = SessionLocal()
        try:
            rows = (
                session.query(Farmer.village, Activity.remarks)
                .join(Activity, Activity.farmer_id == Farmer.id)
                .filter(Activity.module_type == "On Farm Testing (OFT)")
                .all()
            )

            matched = set()
            for village, remarks in rows:
                if not (village or "").strip():
                    continue
                row_district, row_tehsil = ActivityService._extract_oft_district_tehsil(remarks)
                if row_district == district and row_tehsil == tehsil:
                    matched.add(village.strip())

            return sorted(matched)
        finally:
            session.close()

    @staticmethod
    def _get_or_create_farmer(session, farmer_name: str, village: str, contact_number: str) -> Farmer:
        farmer = (
            session.query(Farmer)
            .filter(
                and_(
                    Farmer.farmer_name == farmer_name.strip(),
                    Farmer.village == village.strip(),
                    Farmer.contact_number == contact_number.strip(),
                )
            )
            .first()
        )
        if farmer:
            return farmer

        farmer = Farmer(
            farmer_name=farmer_name.strip(),
            village=village.strip(),
            contact_number=contact_number.strip(),
        )
        session.add(farmer)
        session.flush()
        return farmer

    @staticmethod
    def create_activity(payload: Dict, current_user_id: int) -> int:
        session = SessionLocal()
        try:
            farmer = ActivityService._get_or_create_farmer(
                session,
                payload["farmer_name"],
                payload["village"],
                payload["contact_number"],
            )

            activity = Activity(
                module_type=payload["module_type"],
                farmer_id=farmer.id,
                department_id=payload["department_id"],
                season=payload["season"],
                activity_type=payload["activity_type"],
                activity_date=payload["activity_date"],
                description=payload.get("description"),
                remarks=payload.get("remarks"),
                created_by=current_user_id,
            )
            session.add(activity)
            session.commit()

            AuditService.log_action(
                user_id=current_user_id,
                action="create_activity",
                module_type=payload["module_type"],
                record_id=activity.id,
                details=f"Created activity for {payload['farmer_name']}",
            )
            return activity.id
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update_activity(activity_id: int, payload: Dict, current_user_id: int) -> None:
        session = SessionLocal()
        try:
            activity = session.query(Activity).filter(Activity.id == activity_id).first()
            if activity is None:
                raise ValueError("Activity not found")

            farmer = ActivityService._get_or_create_farmer(
                session,
                payload["farmer_name"],
                payload["village"],
                payload["contact_number"],
            )

            activity.module_type = payload["module_type"]
            activity.farmer_id = farmer.id
            activity.department_id = payload["department_id"]
            activity.season = payload["season"]
            activity.activity_type = payload["activity_type"]
            activity.activity_date = payload["activity_date"]
            activity.description = payload.get("description")
            activity.remarks = payload.get("remarks")
            session.commit()

            AuditService.log_action(
                user_id=current_user_id,
                action="update_activity",
                module_type=payload["module_type"],
                record_id=activity_id,
                details="Updated activity",
            )
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def delete_activity(activity_id: int, current_user_id: int) -> None:
        session = SessionLocal()
        try:
            activity = session.query(Activity).filter(Activity.id == activity_id).first()
            if activity is None:
                raise ValueError("Activity not found")

            module_type = activity.module_type
            session.delete(activity)
            session.commit()

            AuditService.log_action(
                user_id=current_user_id,
                action="delete_activity",
                module_type=module_type,
                record_id=activity_id,
                details="Deleted activity",
            )
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def fetch_activities(
        module_type: str,
        page: int = 1,
        page_size: int = 100,
        filters: Optional[Dict] = None,
    ) -> Tuple[List[Dict], int]:
        session = SessionLocal()
        try:
            base_query = (
                session.query(Activity, Farmer, Department)
                .join(Farmer, Activity.farmer_id == Farmer.id)
                .join(Department, Activity.department_id == Department.id)
                .filter(Activity.module_type == module_type)
            )

            if filters:
                search_text = (filters.get("search_text") or "").strip()
                department_id = filters.get("department_id")
                season = filters.get("season")
                start_date = filters.get("start_date")
                end_date = filters.get("end_date")

                if search_text:
                    like_pattern = f"%{search_text}%"
                    base_query = base_query.filter(
                        or_(
                            Farmer.farmer_name.ilike(like_pattern),
                            Farmer.village.ilike(like_pattern),
                            Farmer.contact_number.ilike(like_pattern),
                            Activity.activity_type.ilike(like_pattern),
                            Activity.description.ilike(like_pattern),
                            Activity.remarks.ilike(like_pattern),
                        )
                    )

                if department_id:
                    base_query = base_query.filter(Activity.department_id == department_id)

                if season and season != "All":
                    base_query = base_query.filter(Activity.season == season)

                if start_date:
                    base_query = base_query.filter(Activity.activity_date >= start_date)

                if end_date:
                    base_query = base_query.filter(Activity.activity_date <= end_date)

            total = base_query.count()
            rows = (
                base_query
                .order_by(Activity.activity_date.desc(), Activity.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            records: List[Dict] = []
            for activity, farmer, department in rows:
                records.append(
                    {
                        "id": activity.id,
                        "farmer_name": farmer.farmer_name,
                        "village": farmer.village,
                        "contact_number": farmer.contact_number,
                        "activity_date": activity.activity_date,
                        "department": department.name,
                        "department_id": department.id,
                        "season": activity.season,
                        "activity_type": activity.activity_type,
                        "description": activity.description or "",
                        "remarks": activity.remarks or "",
                    }
                )
            return records, total
        finally:
            session.close()
