from datetime import date
from typing import Dict, List, Optional, Tuple

from sqlalchemy import Integer, and_, cast, func, or_

from database.session import SessionLocal
from models.entities import Activity, Department, DuplicateReview, Farmer
from services.audit_service import AuditService


class ActivityService:
    """CRUD operations for farmer activities across all modules."""

    @staticmethod
    def farmer_id_number_match(term: str):
        """Match KVK-F-000048 when the search is 48, 048, or 000048."""
        digits = (term or "").strip()
        if not digits.isdigit():
            return None
        numeric_code = cast(
            func.nullif(func.regexp_replace(Farmer.farmer_code, "[^0-9]", "", "g"), ""),
            Integer,
        )
        return numeric_code == int(digits)

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
                session.query(Farmer.village, Activity.visitor_district, Activity.visitor_tehsil, Activity.remarks)
                .join(Activity, Activity.farmer_id == Farmer.id)
                .filter(Activity.module_type == "Visitor Farmers")
                .all()
            )

            matched = set()
            for village, stored_district, stored_tehsil, remarks in rows:
                if not (village or "").strip():
                    continue
                row_district = (stored_district or "").strip()
                row_tehsil = (stored_tehsil or "").strip()
                if not row_district or not row_tehsil:
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
    def list_villages_for_oft(district: str, tehsil: str, module_type: str = "") -> List[str]:
        district = (district or "").strip()
        tehsil = (tehsil or "").strip()
        if not district or not tehsil:
            return []

        session = SessionLocal()
        try:
            module_filter = [module_type] if module_type else ["On Farm Testing (OFT)", "Front Line Demonstrations (FLD)"]
            rows = (
                session.query(Farmer.village, Activity.oft_farmer_district, Activity.oft_farmer_tehsil, Activity.remarks)
                .join(Activity, Activity.farmer_id == Farmer.id)
                .filter(Activity.module_type.in_(module_filter))
                .all()
            )

            matched = set()
            for village, stored_district, stored_tehsil, remarks in rows:
                if not (village or "").strip():
                    continue
                row_district = (stored_district or "").strip()
                row_tehsil = (stored_tehsil or "").strip()
                if not row_district or not row_tehsil:
                    row_district, row_tehsil = ActivityService._extract_oft_district_tehsil(remarks)
                if row_district == district and row_tehsil == tehsil:
                    matched.add(village.strip())

            return sorted(matched)
        finally:
            session.close()

    @staticmethod
    def list_villages_for_training(district: str, tehsil: str, module_type: str = "") -> List[str]:
        district = (district or "").strip()
        tehsil = (tehsil or "").strip()
        if not district or not tehsil:
            return []

        session = SessionLocal()
        try:
            module_filter = [module_type] if module_type else ["Training Programmes", "Vocational Training Programmes"]
            rows = (
                session.query(Farmer.village)
                .join(Activity, Activity.farmer_id == Farmer.id)
                .filter(
                    Activity.module_type.in_(module_filter),
                    Activity.training_farmer_district == district,
                    Activity.training_farmer_tehsil == tehsil,
                )
                .all()
            )
            return sorted({(village or "").strip() for (village,) in rows if (village or "").strip()})
        finally:
            session.close()

    @staticmethod
    def _get_or_create_farmer(session, farmer_name: str, village: str, contact_number: str) -> Farmer:
        contact_number = contact_number.strip()
        if not contact_number.isdigit() or len(contact_number) != 10:
            raise ValueError("Mobile number must be exactly 10 digits.")

        farmer = (
            session.query(Farmer)
            .filter(
                and_(
                    Farmer.farmer_name == farmer_name.strip(),
                    Farmer.village == village.strip(),
                    Farmer.contact_number == contact_number,
                )
            )
            .first()
        )
        if farmer:
            if not farmer.farmer_code:
                farmer.farmer_code = f"KVK-F-{farmer.id:06d}"
            return farmer

        farmer = Farmer(
            farmer_name=farmer_name.strip(),
            village=village.strip(),
            contact_number=contact_number,
        )
        session.add(farmer)
        session.flush()
        if not farmer.farmer_code:
            farmer.farmer_code = f"KVK-F-{farmer.id:06d}"
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
                visitor_scientist=payload.get("visitor_scientist"),
                visitor_district=payload.get("visitor_district"),
                visitor_tehsil=payload.get("visitor_tehsil"),
                oft_title=payload.get("oft_title"),
                oft_batch_key=payload.get("oft_batch_key"),
                oft_crop_variety=payload.get("oft_crop_variety"),
                oft_farmer_count=payload.get("oft_farmer_count"),
                oft_technical_assessment=payload.get("oft_technical_assessment"),
                oft_area=payload.get("oft_area"),
                oft_farmer_scientist=payload.get("oft_farmer_scientist"),
                oft_farmer_purpose=payload.get("oft_farmer_purpose"),
                oft_farmer_district=payload.get("oft_farmer_district"),
                oft_farmer_tehsil=payload.get("oft_farmer_tehsil"),
                oft_farmer_category=payload.get("oft_farmer_category"),
                training_title=payload.get("training_title"),
                training_type=payload.get("training_type"),
                training_end_date=payload.get("training_end_date"),
                clientele=payload.get("clientele"),
                thematic_area=payload.get("thematic_area"),
                venue=payload.get("venue"),
                venue_is_offline=payload.get("venue_is_offline"),
                venue_village=payload.get("venue_village"),
                venue_taluka=payload.get("venue_taluka"),
                venue_district=payload.get("venue_district"),
                training_farmer_count=payload.get("training_farmer_count"),
                training_farmer_category=payload.get("training_farmer_category"),
                training_farmer_scientist=payload.get("training_farmer_scientist"),
                training_farmer_purpose=payload.get("training_farmer_purpose"),
                training_farmer_district=payload.get("training_farmer_district"),
                training_farmer_tehsil=payload.get("training_farmer_tehsil"),
                extension_venue=payload.get("extension_venue"),
                extension_location=payload.get("extension_location"),
                extension_department=payload.get("extension_department"),
                extension_purpose=payload.get("extension_purpose"),
                extension_farmer_count=payload.get("extension_farmer_count"),
                other_extension_title=payload.get("other_extension_title"),
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
            activity.visitor_scientist = payload.get("visitor_scientist")
            activity.visitor_district = payload.get("visitor_district")
            activity.visitor_tehsil = payload.get("visitor_tehsil")
            activity.oft_title = payload.get("oft_title")
            activity.oft_batch_key = payload.get("oft_batch_key")
            activity.oft_crop_variety = payload.get("oft_crop_variety")
            activity.oft_farmer_count = payload.get("oft_farmer_count")
            activity.oft_technical_assessment = payload.get("oft_technical_assessment")
            activity.oft_area = payload.get("oft_area")
            activity.oft_farmer_scientist = payload.get("oft_farmer_scientist")
            activity.oft_farmer_purpose = payload.get("oft_farmer_purpose")
            activity.oft_farmer_district = payload.get("oft_farmer_district")
            activity.oft_farmer_tehsil = payload.get("oft_farmer_tehsil")
            activity.oft_farmer_category = payload.get("oft_farmer_category")
            activity.training_title = payload.get("training_title")
            activity.training_type = payload.get("training_type")
            activity.training_end_date = payload.get("training_end_date")
            activity.clientele = payload.get("clientele")
            activity.thematic_area = payload.get("thematic_area")
            activity.venue = payload.get("venue")
            activity.venue_is_offline = payload.get("venue_is_offline")
            activity.venue_village = payload.get("venue_village")
            activity.venue_taluka = payload.get("venue_taluka")
            activity.venue_district = payload.get("venue_district")
            activity.training_farmer_count = payload.get("training_farmer_count")
            activity.training_farmer_category = payload.get("training_farmer_category")
            activity.training_farmer_scientist = payload.get("training_farmer_scientist")
            activity.training_farmer_purpose = payload.get("training_farmer_purpose")
            activity.training_farmer_district = payload.get("training_farmer_district")
            activity.training_farmer_tehsil = payload.get("training_farmer_tehsil")
            activity.extension_venue = payload.get("extension_venue")
            activity.extension_location = payload.get("extension_location")
            activity.extension_department = payload.get("extension_department")
            activity.extension_purpose = payload.get("extension_purpose")
            activity.extension_farmer_count = payload.get("extension_farmer_count")
            activity.other_extension_title = payload.get("other_extension_title")
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
            farmer_id = activity.farmer_id
            session.delete(activity)
            session.flush()
            remaining = session.query(Activity.id).filter(Activity.farmer_id == farmer_id).count()
            removed_farmer = False
            if remaining == 0:
                session.query(DuplicateReview).filter(
                    or_(
                        DuplicateReview.farmer_low_id == farmer_id,
                        DuplicateReview.farmer_high_id == farmer_id,
                    )
                ).delete(synchronize_session=False)
                farmer = session.query(Farmer).filter(Farmer.id == farmer_id).first()
                if farmer is not None:
                    session.delete(farmer)
                    removed_farmer = True
            session.commit()

            AuditService.log_action(
                user_id=current_user_id,
                action="delete_activity",
                module_type=module_type,
                record_id=activity_id,
                details="Deleted activity and farmer record" if removed_farmer else "Deleted activity",
            )
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def remove_farmers_without_activities() -> int:
        """Removes farmer rows left behind after their activities were deleted."""
        session = SessionLocal()
        try:
            orphan_ids = [
                farmer_id
                for (farmer_id,) in session.query(Farmer.id)
                .outerjoin(Activity, Activity.farmer_id == Farmer.id)
                .filter(Activity.id.is_(None))
                .all()
            ]
            if not orphan_ids:
                return 0
            session.query(DuplicateReview).filter(
                or_(
                    DuplicateReview.farmer_low_id.in_(orphan_ids),
                    DuplicateReview.farmer_high_id.in_(orphan_ids),
                )
            ).delete(synchronize_session=False)
            deleted = (
                session.query(Farmer)
                .filter(Farmer.id.in_(orphan_ids))
                .delete(synchronize_session=False)
            )
            session.commit()
            return int(deleted or 0)
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
                    id_match = ActivityService.farmer_id_number_match(search_text)
                    if search_text.isdigit() and len(search_text) <= 6 and id_match is not None:
                        base_query = base_query.filter(id_match)
                    else:
                        search_match = [
                            Farmer.farmer_name.ilike(like_pattern),
                            Farmer.farmer_code.ilike(like_pattern),
                        ]
                        if id_match is not None:
                            search_match.append(id_match)
                        base_query = base_query.filter(
                            or_(
                                *search_match,
                            Farmer.village.ilike(like_pattern),
                            Farmer.contact_number.ilike(like_pattern),
                            Activity.activity_type.ilike(like_pattern),
                            Activity.description.ilike(like_pattern),
                            Activity.remarks.ilike(like_pattern),
                            Activity.visitor_scientist.ilike(like_pattern),
                            Activity.visitor_district.ilike(like_pattern),
                            Activity.visitor_tehsil.ilike(like_pattern),
                            Activity.oft_title.ilike(like_pattern),
                            Activity.oft_crop_variety.ilike(like_pattern),
                            Activity.oft_technical_assessment.ilike(like_pattern),
                            Activity.oft_area.ilike(like_pattern),
                            Activity.oft_farmer_scientist.ilike(like_pattern),
                            Activity.oft_farmer_purpose.ilike(like_pattern),
                            Activity.oft_farmer_district.ilike(like_pattern),
                            Activity.oft_farmer_tehsil.ilike(like_pattern),
                            Activity.oft_farmer_category.ilike(like_pattern),
                            Activity.training_title.ilike(like_pattern),
                            Activity.training_type.ilike(like_pattern),
                            Activity.clientele.ilike(like_pattern),
                            Activity.venue.ilike(like_pattern),
                            Activity.venue_village.ilike(like_pattern),
                            Activity.venue_taluka.ilike(like_pattern),
                            Activity.venue_district.ilike(like_pattern),
                            Activity.training_farmer_category.ilike(like_pattern),
                            Activity.training_farmer_scientist.ilike(like_pattern),
                            Activity.training_farmer_purpose.ilike(like_pattern),
                            Activity.training_farmer_district.ilike(like_pattern),
                            Activity.training_farmer_tehsil.ilike(like_pattern),
                            Activity.extension_venue.ilike(like_pattern),
                            Activity.extension_location.ilike(like_pattern),
                            Activity.extension_department.ilike(like_pattern),
                            Activity.extension_purpose.ilike(like_pattern),
                            Activity.other_extension_title.ilike(like_pattern),
                        )
                    )

                if department_id:
                    base_query = base_query.filter(Activity.department_id == department_id)

                if season and season != "All":
                    base_query = base_query.filter(Activity.season == season)

                if start_date:
                    date_match = or_(
                        and_(Activity.activity_date >= start_date, Activity.activity_date <= end_date),
                        and_(func.date(Activity.created_at) >= start_date, func.date(Activity.created_at) <= end_date),
                    )
                    base_query = base_query.filter(date_match)

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
                visitor_district = activity.visitor_district or ""
                visitor_tehsil = activity.visitor_tehsil or ""
                if activity.module_type == "Visitor Farmers" and (not visitor_district or not visitor_tehsil):
                    parsed_district, parsed_tehsil = ActivityService._extract_district_tehsil(activity.remarks)
                    visitor_district = visitor_district or parsed_district
                    visitor_tehsil = visitor_tehsil or parsed_tehsil
                records.append(
                    {
                        "id": activity.id,
                        "farmer_name": farmer.farmer_name,
                        "farmer_code": farmer.farmer_code or "",
                        "village": farmer.village,
                        "contact_number": farmer.contact_number,
                        "activity_date": activity.activity_date,
                        "department": department.name,
                        "department_id": department.id,
                        "season": activity.season,
                        "activity_type": activity.activity_type,
                        "description": activity.description or "",
                        "remarks": activity.remarks or "",
                        "visitor_scientist": activity.visitor_scientist or "",
                        "visitor_district": visitor_district,
                        "visitor_tehsil": visitor_tehsil,
                        "district": visitor_district,
                        "tehsil": visitor_tehsil,
                        "oft_title": activity.oft_title or "",
                        "oft_batch_key": activity.oft_batch_key or "",
                        "oft_crop_variety": activity.oft_crop_variety or "",
                        "oft_farmer_count": activity.oft_farmer_count,
                        "oft_technical_assessment": activity.oft_technical_assessment or "",
                        "oft_area": activity.oft_area or "",
                        "oft_farmer_scientist": activity.oft_farmer_scientist or "",
                        "oft_farmer_purpose": activity.oft_farmer_purpose or "",
                        "oft_farmer_district": activity.oft_farmer_district or "",
                        "oft_farmer_tehsil": activity.oft_farmer_tehsil or "",
                        "oft_farmer_category": activity.oft_farmer_category or "",
                        "training_title": activity.training_title or "",
                        "training_type": activity.training_type or "",
                        "training_end_date": activity.training_end_date,
                        "clientele": activity.clientele or "",
                        "thematic_area": activity.thematic_area or "",
                        "venue": activity.venue or "",
                        "venue_is_offline": activity.venue_is_offline,
                        "venue_village": activity.venue_village or "",
                        "venue_taluka": activity.venue_taluka or "",
                        "venue_district": activity.venue_district or "",
                        "training_farmer_count": activity.training_farmer_count,
                        "training_farmer_category": activity.training_farmer_category or "",
                        "training_farmer_scientist": activity.training_farmer_scientist or "",
                        "training_farmer_purpose": activity.training_farmer_purpose or "",
                        "training_farmer_district": activity.training_farmer_district or "",
                        "training_farmer_tehsil": activity.training_farmer_tehsil or "",
                        "extension_venue": activity.extension_venue or "",
                        "extension_location": activity.extension_location or "",
                        "extension_department": activity.extension_department or "",
                        "extension_purpose": activity.extension_purpose or "",
                        "extension_farmer_count": activity.extension_farmer_count,
                        "other_extension_title": activity.other_extension_title or "",
                    }
                )
            return records, total
        finally:
            session.close()

    @staticmethod
    def fetch_oft_batch_records(activity_id: int, batch_key: str = "") -> List[Dict]:
        session = SessionLocal()
        try:
            if batch_key:
                anchor = session.query(Activity).filter(Activity.id == activity_id).first()
                module_type = anchor.module_type if anchor is not None else None
                module_condition = (
                    Activity.module_type == module_type
                    if module_type
                    else Activity.module_type.in_(["On Farm Testing (OFT)", "Front Line Demonstrations (FLD)"])
                )
                rows = (
                    session.query(Activity, Farmer, Department)
                    .join(Farmer, Activity.farmer_id == Farmer.id)
                    .join(Department, Activity.department_id == Department.id)
                    .filter(
                        module_condition,
                        Activity.oft_batch_key == batch_key,
                    )
                    .order_by(Activity.id.asc())
                    .all()
                )
            else:
                rows = (
                    session.query(Activity, Farmer, Department)
                    .join(Farmer, Activity.farmer_id == Farmer.id)
                    .join(Department, Activity.department_id == Department.id)
                    .filter(Activity.id == activity_id)
                    .all()
                )

            records: List[Dict] = []
            for activity, farmer, department in rows:
                visitor_district = activity.visitor_district or ""
                visitor_tehsil = activity.visitor_tehsil or ""
                if activity.module_type == "Visitor Farmers" and (not visitor_district or not visitor_tehsil):
                    parsed_district, parsed_tehsil = ActivityService._extract_district_tehsil(activity.remarks)
                    visitor_district = visitor_district or parsed_district
                    visitor_tehsil = visitor_tehsil or parsed_tehsil
                records.append(
                    {
                        "id": activity.id,
                        "farmer_name": farmer.farmer_name,
                        "farmer_code": farmer.farmer_code or "",
                        "village": farmer.village,
                        "contact_number": farmer.contact_number,
                        "activity_date": activity.activity_date,
                        "department": department.name,
                        "department_id": department.id,
                        "season": activity.season,
                        "activity_type": activity.activity_type,
                        "description": activity.description or "",
                        "remarks": activity.remarks or "",
                        "visitor_scientist": activity.visitor_scientist or "",
                        "visitor_district": visitor_district,
                        "visitor_tehsil": visitor_tehsil,
                        "district": visitor_district,
                        "tehsil": visitor_tehsil,
                        "oft_title": activity.oft_title or "",
                        "oft_batch_key": activity.oft_batch_key or "",
                        "oft_crop_variety": activity.oft_crop_variety or "",
                        "oft_farmer_count": activity.oft_farmer_count,
                        "oft_technical_assessment": activity.oft_technical_assessment or "",
                        "oft_area": activity.oft_area or "",
                        "oft_farmer_scientist": activity.oft_farmer_scientist or "",
                        "oft_farmer_purpose": activity.oft_farmer_purpose or "",
                        "oft_farmer_district": activity.oft_farmer_district or "",
                        "oft_farmer_tehsil": activity.oft_farmer_tehsil or "",
                        "oft_farmer_category": activity.oft_farmer_category or "",
                    }
                )
            return records
        finally:
            session.close()
