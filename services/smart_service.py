"""Office features that sit beside the existing activity, report, and analytics services."""

from __future__ import annotations

import logging
import os
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
from statistics import mean, pstdev
from typing import Dict, List, Optional

from sqlalchemy import and_, func, or_

from database.session import SessionLocal
from models.entities import Activity, AppSetting, Department, DuplicateReview, Farmer
from services.activity_service import ActivityService
from services.audit_service import AuditService

logger = logging.getLogger(__name__)

PLACEHOLDER_MOBILES = {"0000000000", ""}
PLACEHOLDER_TEXT = {"", "n/a", "na", "none", "null"}
PARTICIPANT_FIELDS = ("oft_farmer_count", "training_farmer_count", "extension_farmer_count")


class SettingsService:
    DEFAULTS = {
        "kvk_name": "Krishi Vigyan Kendra",
        "kvk_address": "",
        "backup_folder": "backups",
        "session_timeout_minutes": "30",
        "backup_overdue_days": "7",
        "last_import_invalid": "0",
    }

    @staticmethod
    def get(key: str, default: Optional[str] = None) -> str:
        session = SessionLocal()
        try:
            row = session.query(AppSetting).filter(AppSetting.key == key).first()
            if row and row.value is not None:
                return row.value
            return SettingsService.DEFAULTS.get(key, default or "")
        finally:
            session.close()

    @staticmethod
    def all_values() -> Dict[str, str]:
        values = dict(SettingsService.DEFAULTS)
        session = SessionLocal()
        try:
            for row in session.query(AppSetting).all():
                values[row.key] = row.value or ""
            return values
        finally:
            session.close()

    @staticmethod
    def save(updates: Dict[str, str], user_id: Optional[int]) -> None:
        session = SessionLocal()
        try:
            for key, value in updates.items():
                row = session.query(AppSetting).filter(AppSetting.key == key).first()
                if row is None:
                    session.add(AppSetting(key=key, value=value, updated_at=datetime.utcnow()))
                else:
                    row.value = value
                    row.updated_at = datetime.utcnow()
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        AuditService.log_action(user_id, "update_settings", "Settings", None, ", ".join(sorted(updates)))

    @staticmethod
    def put(key: str, value: str) -> None:
        session = SessionLocal()
        try:
            row = session.query(AppSetting).filter(AppSetting.key == key).first()
            if row is None:
                session.add(AppSetting(key=key, value=value, updated_at=datetime.utcnow()))
            else:
                row.value = value
                row.updated_at = datetime.utcnow()
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def add_department(name: str, user_id: Optional[int]) -> None:
        cleaned = (name or "").strip()
        if len(cleaned) < 2:
            raise ValueError("Enter a department name.")
        session = SessionLocal()
        try:
            exists = session.query(Department).filter(func.lower(Department.name) == cleaned.lower()).first()
            if exists:
                raise ValueError("That department already exists.")
            session.add(Department(name=cleaned))
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        AuditService.log_action(user_id, "add_department", "Settings", None, cleaned)


class SearchService:
    @staticmethod
    def search(text: str, limit: int = 50) -> List[Dict]:
        term = (text or "").strip()
        if len(term) < 1 or (len(term) < 2 and not term.isdigit()):
            return []
        like = f"%{term}%"
        id_match = ActivityService.farmer_id_number_match(term)
        if term.isdigit() and len(term) <= 6:
            conditions = [id_match]
        else:
            conditions = [
                Farmer.farmer_name.ilike(like),
                Farmer.farmer_code.ilike(like),
                Farmer.contact_number.ilike(like),
                Farmer.village.ilike(like),
                Activity.module_type.ilike(like),
                Activity.activity_type.ilike(like),
                Activity.oft_title.ilike(like),
                Activity.training_title.ilike(like),
                Activity.other_extension_title.ilike(like),
                Activity.extension_purpose.ilike(like),
            ]
            if id_match is not None:
                conditions.append(id_match)
        session = SessionLocal()
        try:
            rows = (
                session.query(Activity, Farmer, Department)
                .join(Farmer, Activity.farmer_id == Farmer.id)
                .join(Department, Activity.department_id == Department.id)
                .filter(or_(*conditions))
                .order_by(Activity.activity_date.desc(), Activity.id.desc())
                .limit(limit)
                .all()
            )
            results = []
            for activity, farmer, department in rows:
                title = (
                    activity.oft_title
                    or activity.training_title
                    or activity.other_extension_title
                    or activity.activity_type
                    or farmer.farmer_name
                )
                results.append(
                    {
                        "activity_id": activity.id,
                        "record_type": activity.module_type,
                        "title": title or "Untitled",
                        "activity_date": activity.activity_date,
                        "identifier": farmer.farmer_code or f"Activity {activity.id}",
                        "farmer_name": farmer.farmer_name,
                        "farmer_code": farmer.farmer_code or "",
                        "village": farmer.village,
                        "contact_number": farmer.contact_number,
                        "department": department.name,
                        "season": activity.season,
                        "activity_type": activity.activity_type,
                        "search_text": farmer.farmer_code or farmer.contact_number or farmer.farmer_name,
                    }
                )
            return results
        finally:
            session.close()


class QualityService:
    @staticmethod
    def summary() -> Dict[str, int]:
        session = SessionLocal()
        try:
            farmers = session.query(Farmer).all()
            activities = session.query(Activity).all()
            complete = 0
            incomplete = 0
            missing_mobile = 0
            missing_village = 0
            for farmer in farmers:
                mobile_ok = _valid_mobile(farmer.contact_number)
                village_ok = _meaningful(farmer.village)
                name_ok = _meaningful(farmer.farmer_name)
                if mobile_ok and village_ok and name_ok:
                    complete += 1
                else:
                    incomplete += 1
                if not mobile_ok:
                    missing_mobile += 1
                if not village_ok:
                    missing_village += 1
            today = date.today()
            invalid_dates = 0
            invalid_values = 0
            for activity in activities:
                if activity.activity_date > today or activity.activity_date.year < 1990:
                    invalid_dates += 1
                for field in PARTICIPANT_FIELDS:
                    value = getattr(activity, field)
                    if value is not None and (value < 0 or value > 1000):
                        invalid_values += 1
                        break
            return {
                "total_checked": len(farmers) + len(activities),
                "complete": complete,
                "incomplete": incomplete,
                "missing_mobile": missing_mobile,
                "missing_village": missing_village,
                "invalid_dates": invalid_dates,
                "invalid_values": invalid_values,
                "possible_duplicates": len(DuplicateService.find_pairs()),
            }
        finally:
            session.close()

    @staticmethod
    def records(metric: str, limit: int = 200) -> List[Dict]:
        session = SessionLocal()
        try:
            if metric == "possible_duplicates":
                return [
                    {
                        "module": "Farmers",
                        "title": f"{pair['left_name']}  /  {pair['right_name']}",
                        "detail": pair["reason"],
                        "identifier": f"{pair['left_code']} · {pair['right_code']}",
                        "open_module": "Duplicates",
                        "search_text": "",
                    }
                    for pair in DuplicateService.find_pairs()[:limit]
                ]
            if metric in {"invalid_dates", "invalid_values"}:
                rows = (
                    session.query(Activity, Farmer)
                    .join(Farmer, Activity.farmer_id == Farmer.id)
                    .order_by(Activity.activity_date.desc())
                    .all()
                )
                found = []
                today = date.today()
                for activity, farmer in rows:
                    problem = ""
                    if metric == "invalid_dates" and (activity.activity_date > today or activity.activity_date.year < 1990):
                        problem = f"Date {activity.activity_date}"
                    if metric == "invalid_values":
                        for field in PARTICIPANT_FIELDS:
                            value = getattr(activity, field)
                            if value is not None and (value < 0 or value > 1000):
                                problem = f"{field.replace('_', ' ')} = {value}"
                                break
                    if not problem:
                        continue
                    found.append(
                        {
                            "module": activity.module_type,
                            "title": farmer.farmer_name if _meaningful(farmer.farmer_name) else (
                                activity.oft_title
                                or activity.training_title
                                or activity.other_extension_title
                                or activity.extension_purpose
                                or activity.activity_type
                                or "Untitled"
                            ),
                            "detail": problem,
                            "identifier": farmer.farmer_code or "",
                            "department": "",
                            "open_module": activity.module_type,
                            "search_text": farmer.farmer_code or str(activity.id),
                        }
                    )
                    if len(found) >= limit:
                        break
                return found

            farmers = session.query(Farmer).order_by(Farmer.farmer_name).all()
            found = []
            for farmer in farmers:
                mobile_ok = _valid_mobile(farmer.contact_number)
                village_ok = _meaningful(farmer.village)
                name_ok = _meaningful(farmer.farmer_name)
                include = False
                detail = []
                if metric == "complete" and mobile_ok and village_ok and name_ok:
                    include = True
                    detail.append("Complete")
                if metric == "incomplete" and not (mobile_ok and village_ok and name_ok):
                    include = True
                if metric == "missing_mobile" and not mobile_ok:
                    include = True
                    detail.append("Missing or invalid mobile")
                if metric == "missing_village" and not village_ok:
                    include = True
                    detail.append("Missing village")
                if metric == "incomplete":
                    if not name_ok:
                        detail.append("Missing name")
                    if not village_ok:
                        detail.append("Missing village")
                    if not mobile_ok:
                        detail.append("Missing or invalid mobile")
                if not include:
                    continue
                context = _farmer_open_context(session, farmer)
                found.append(
                    {
                        "module": context["module"],
                        "title": context["title"],
                        "detail": ", ".join(detail),
                        "identifier": farmer.farmer_code or "",
                        "department": context["department"],
                        "open_module": context["open_module"],
                        "search_text": farmer.farmer_code or farmer.contact_number or farmer.farmer_name,
                    }
                )
                if len(found) >= limit:
                    break
            return found
        finally:
            session.close()


def _farmer_open_context(session, farmer: Farmer) -> Dict:
    """Finds the module that owns this farmer so quality clicks open the right page."""
    rows = (
        session.query(Activity, Department)
        .join(Department, Activity.department_id == Department.id)
        .filter(Activity.farmer_id == farmer.id)
        .order_by(Activity.activity_date.desc(), Activity.id.desc())
        .all()
    )
    if not rows:
        return {
            "module": "Farmer",
            "title": farmer.farmer_name or "Untitled",
            "department": "",
            "open_module": "Visitor Farmers",
        }

    preferred = [
        "Visitor Farmers",
        "On Farm Testing (OFT)",
        "Front Line Demonstrations (FLD)",
        "Training Programmes",
        "Vocational Training Programmes",
        "Extension Activities",
        "Other Extension Activities",
    ]
    if not _meaningful(farmer.farmer_name) or not _valid_mobile(farmer.contact_number):
        preferred = [
            "Extension Activities",
            "Other Extension Activities",
            "Visitor Farmers",
            "On Farm Testing (OFT)",
            "Front Line Demonstrations (FLD)",
            "Training Programmes",
            "Vocational Training Programmes",
        ]
    chosen = None
    for module_name in preferred:
        for activity, department in rows:
            if activity.module_type == module_name:
                chosen = (activity, department)
                break
        if chosen is not None:
            break
    if chosen is None:
        chosen = rows[0]
    activity, department = chosen
    title = (
        activity.oft_title
        or activity.training_title
        or activity.other_extension_title
        or activity.extension_purpose
        or activity.activity_type
        or farmer.farmer_name
        or "Untitled"
    )
    if not _meaningful(farmer.farmer_name) and activity.module_type in {
        "Extension Activities",
        "Other Extension Activities",
    }:
        title = activity.other_extension_title or activity.extension_purpose or activity.activity_type or title
    return {
        "module": activity.module_type,
        "title": title,
        "department": department.name,
        "open_module": activity.module_type,
    }


class DuplicateService:
    @staticmethod
    def find_pairs(limit: int = 80) -> List[Dict]:
        session = SessionLocal()
        try:
            farmers = [row for row in session.query(Farmer).all() if _meaningful(row.farmer_name)]
            dismissed = {
                (row.farmer_low_id, row.farmer_high_id)
                for row in session.query(DuplicateReview).filter(DuplicateReview.decision == "keep_both").all()
            }
            pairs = []
            for index, left in enumerate(farmers):
                for right in farmers[index + 1 :]:
                    low, high = sorted((left.id, right.id))
                    if (low, high) in dismissed:
                        continue
                    reasons = []
                    if (
                        left.contact_number == right.contact_number
                        and left.contact_number not in PLACEHOLDER_MOBILES
                        and _valid_mobile(left.contact_number)
                    ):
                        reasons.append("Same mobile number")
                    same_village = (left.village or "").strip().lower() == (right.village or "").strip().lower()
                    ratio = SequenceMatcher(None, left.farmer_name.strip().lower(), right.farmer_name.strip().lower()).ratio()
                    if same_village and ratio >= 0.86 and left.farmer_name.strip().lower() != right.farmer_name.strip().lower():
                        reasons.append(f"Similar name in the same village ({ratio:.0%})")
                    if left.farmer_name.strip().lower() == right.farmer_name.strip().lower() and same_village:
                        reasons.append("Same name and village")
                    if not reasons:
                        continue
                    pairs.append(
                        {
                            "left_id": left.id,
                            "right_id": right.id,
                            "left_name": left.farmer_name,
                            "right_name": right.farmer_name,
                            "left_code": left.farmer_code or "",
                            "right_code": right.farmer_code or "",
                            "left_village": left.village,
                            "right_village": right.village,
                            "left_mobile": left.contact_number,
                            "right_mobile": right.contact_number,
                            "reason": "; ".join(reasons),
                            "score": f"{max(ratio, 1.0 if 'Same mobile' in reasons else ratio):.0%}",
                        }
                    )
                    if len(pairs) >= limit:
                        return pairs
            return pairs
        finally:
            session.close()

    @staticmethod
    def keep_both(left_id: int, right_id: int, user_id: Optional[int]) -> None:
        low, high = sorted((int(left_id), int(right_id)))
        session = SessionLocal()
        try:
            row = (
                session.query(DuplicateReview)
                .filter(DuplicateReview.farmer_low_id == low, DuplicateReview.farmer_high_id == high)
                .first()
            )
            if row is None:
                session.add(
                    DuplicateReview(
                        farmer_low_id=low,
                        farmer_high_id=high,
                        decision="keep_both",
                        reviewed_by=user_id,
                    )
                )
            else:
                row.decision = "keep_both"
                row.reviewed_by = user_id
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        AuditService.log_action(user_id, "keep_duplicate_pair", "Duplicates", low, f"Kept farmers {low} and {high}")

    @staticmethod
    def merge(keep_id: int, drop_id: int, user_id: Optional[int]) -> None:
        keep_id = int(keep_id)
        drop_id = int(drop_id)
        if keep_id == drop_id:
            raise ValueError("Choose two different farmer records.")
        session = SessionLocal()
        try:
            keep = session.query(Farmer).filter(Farmer.id == keep_id).first()
            drop = session.query(Farmer).filter(Farmer.id == drop_id).first()
            if keep is None or drop is None:
                raise ValueError("One of the farmer records is no longer available.")
            session.query(Activity).filter(Activity.farmer_id == drop_id).update(
                {Activity.farmer_id: keep_id}, synchronize_session=False
            )
            session.query(DuplicateReview).filter(
                or_(
                    DuplicateReview.farmer_low_id == drop_id,
                    DuplicateReview.farmer_high_id == drop_id,
                )
            ).delete(synchronize_session=False)
            session.delete(drop)
            session.commit()
            kept_code = keep.farmer_code
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        AuditService.log_action(
            user_id,
            "merge_farmers",
            "Duplicates",
            keep_id,
            f"Moved records from farmer {drop_id} to {keep_id} ({kept_code})",
        )


class AnomalyService:
    """Flags unusual participant counts. Uses a statistical band when history is sufficient."""

    @staticmethod
    def find(limit: int = 100) -> List[Dict]:
        session = SessionLocal()
        try:
            activities = session.query(Activity, Farmer).join(Farmer, Activity.farmer_id == Farmer.id).all()
            series = {field: [] for field in PARTICIPANT_FIELDS}
            for activity, _farmer in activities:
                for field in PARTICIPANT_FIELDS:
                    value = getattr(activity, field)
                    if value is not None and value >= 0:
                        series[field].append(value)
            bands = {}
            for field, values in series.items():
                if len(values) >= 8:
                    try:
                        import numpy as np

                        center = float(np.mean(values))
                        spread = float(np.std(values))
                    except Exception:
                        center = mean(values)
                        spread = pstdev(values) or 0
                    bands[field] = (center, spread, True)
                else:
                    bands[field] = (None, None, False)
            findings = []
            for activity, farmer in activities:
                for field in PARTICIPANT_FIELDS:
                    value = getattr(activity, field)
                    if value is None:
                        continue
                    center, spread, statistical = bands[field]
                    unusual = False
                    if statistical:
                        unusual = abs(value - center) > max(3 * spread, 1) and value > center
                    else:
                        unusual = value > 300 or value < 0
                    if not unusual:
                        continue
                    title = activity.oft_title or activity.training_title or activity.activity_type or farmer.farmer_name
                    findings.append(
                        {
                            "activity_id": activity.id,
                            "module": activity.module_type,
                            "title": title,
                            "activity_date": activity.activity_date,
                            "identifier": farmer.farmer_code or "",
                            "message": f"Unusual value detected. Please verify. {field.replace('_', ' ')} is {value}.",
                            "open_module": activity.module_type,
                        }
                    )
                    break
                if len(findings) >= limit:
                    break
            return findings
        finally:
            session.close()


class InsightService:
    @staticmethod
    def recent(limit: int = 8) -> Dict[str, List[Dict]]:
        session = SessionLocal()
        try:
            added_rows = (
                session.query(Activity, Farmer)
                .join(Farmer, Activity.farmer_id == Farmer.id)
                .order_by(Activity.created_at.desc())
                .limit(limit)
                .all()
            )
            updated_rows = (
                session.query(Activity, Farmer)
                .join(Farmer, Activity.farmer_id == Farmer.id)
                .filter(Activity.updated_at > Activity.created_at)
                .order_by(Activity.updated_at.desc())
                .limit(limit)
                .all()
            )
            return {"added": [_recent_row(a, f, a.created_at) for a, f in added_rows], "updated": [_recent_row(a, f, a.updated_at) for a, f in updated_rows]}
        finally:
            session.close()

    @staticmethod
    def month_events(year: int, month: int) -> List[Dict]:
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)
        session = SessionLocal()
        try:
            rows = (
                session.query(Activity, Farmer)
                .join(Farmer, Activity.farmer_id == Farmer.id)
                .filter(Activity.activity_date >= start, Activity.activity_date < end)
                .order_by(Activity.activity_date, Activity.id)
                .all()
            )
            events = []
            for activity, farmer in rows:
                title = activity.oft_title or activity.training_title or activity.other_extension_title or activity.activity_type
                events.append(
                    {
                        "activity_id": activity.id,
                        "activity_date": activity.activity_date,
                        "module": activity.module_type,
                        "title": title or farmer.farmer_name,
                        "identifier": farmer.farmer_code or "",
                        "village": farmer.village,
                        "open_module": activity.module_type,
                    }
                )
            return events
        finally:
            session.close()

    @staticmethod
    def financial_years() -> List[str]:
        session = SessionLocal()
        try:
            dates = [row[0] for row in session.query(Activity.activity_date).distinct().all() if row[0]]
        finally:
            session.close()
        years = {financial_year(value) for value in dates}
        years.add(financial_year(date.today()))
        return sorted(years)

    @staticmethod
    def compare_years(left_year: str, right_year: str) -> List[Dict]:
        session = SessionLocal()
        try:
            rows = session.query(Activity, Farmer).join(Farmer, Activity.farmer_id == Farmer.id).all()
        finally:
            session.close()
        labels = [
            ("Farmers", "farmers"),
            ("OFT", "On Farm Testing (OFT)"),
            ("FLD", "Front Line Demonstrations (FLD)"),
            ("Training", "Training Programmes"),
            ("Vocational Training", "Vocational Training Programmes"),
            ("Extension Activities", "Extension Activities"),
            ("Other Extension Activities", "Other Extension Activities"),
            ("Participation", "participation"),
        ]
        buckets = {left_year: _empty_bucket(), right_year: _empty_bucket()}
        seen = {left_year: set(), right_year: set()}
        for activity, farmer in rows:
            year_key = financial_year(activity.activity_date)
            if year_key not in buckets:
                continue
            bucket = buckets[year_key]
            bucket[activity.module_type] = bucket.get(activity.module_type, 0) + 1
            if farmer.id not in seen[year_key]:
                seen[year_key].add(farmer.id)
                bucket["farmers"] += 1
            for field in PARTICIPANT_FIELDS:
                value = getattr(activity, field) or 0
                if value:
                    bucket["participation"] += int(value)
        result = []
        for label, key in labels:
            left_value = buckets[left_year].get(key, 0)
            right_value = buckets[right_year].get(key, 0)
            result.append({"label": label, "left": left_value, "right": right_value, "change": right_value - left_value})
        return result

    @staticmethod
    def villages() -> List[Dict]:
        session = SessionLocal()
        try:
            rows = (
                session.query(Activity, Farmer)
                .join(Farmer, Activity.farmer_id == Farmer.id)
                .all()
            )
        finally:
            session.close()
        grouped: Dict[str, Dict] = {}
        farmers_seen: Dict[str, set] = {}
        for activity, farmer in rows:
            village = (farmer.village or "").strip() or "Unspecified"
            item = grouped.setdefault(
                village,
                {"village": village, "farmers": 0, "activities": 0, "oft": 0, "fld": 0, "training_participation": 0},
            )
            seen = farmers_seen.setdefault(village, set())
            if farmer.id not in seen and _meaningful(farmer.farmer_name):
                seen.add(farmer.id)
                item["farmers"] += 1
            item["activities"] += 1
            if activity.module_type == "On Farm Testing (OFT)":
                item["oft"] += 1
            if activity.module_type == "Front Line Demonstrations (FLD)":
                item["fld"] += 1
            if activity.module_type in {"Training Programmes", "Vocational Training Programmes"}:
                item["training_participation"] += int(activity.training_farmer_count or 1)
        return sorted(grouped.values(), key=lambda row: (-row["farmers"], row["village"].lower()))

    @staticmethod
    def alerts() -> List[Dict]:
        alerts = []
        quality = QualityService.summary()
        if quality["incomplete"]:
            alerts.append({"title": "Incomplete records", "detail": f"{quality['incomplete']} farmer records are incomplete.", "open_module": "Data Quality"})
        if quality["missing_mobile"]:
            alerts.append({"title": "Missing mobile numbers", "detail": f"{quality['missing_mobile']} records have a missing or invalid mobile number.", "open_module": "Data Quality"})
        if quality["invalid_dates"] or quality["invalid_values"]:
            alerts.append(
                {
                    "title": "Validation issues",
                    "detail": f"{quality['invalid_dates']} invalid dates and {quality['invalid_values']} invalid values.",
                    "open_module": "Data Quality",
                }
            )
        if quality["possible_duplicates"]:
            alerts.append({"title": "Possible duplicate farmers", "detail": f"{quality['possible_duplicates']} pairs need review.", "open_module": "Duplicates"})
        anomalies = AnomalyService.find(limit=20)
        if anomalies:
            alerts.append({"title": "Anomalies detected", "detail": f"{len(anomalies)} unusual values need verification.", "open_module": "Alerts"})
        invalid_import = int(SettingsService.get("last_import_invalid") or "0")
        if invalid_import:
            alerts.append({"title": "Import errors", "detail": f"The last import left {invalid_import} invalid rows out.", "open_module": "Import"})
        last = last_backup()
        overdue_days = int(SettingsService.get("backup_overdue_days") or "7")
        if last is None:
            alerts.append({"title": "Backup overdue", "detail": "No database backup has been recorded yet.", "open_module": "Backup & Restore"})
        elif datetime.utcnow() - last["created_at"] > timedelta(days=overdue_days):
            alerts.append(
                {
                    "title": "Backup overdue",
                    "detail": f"Last backup was {last['created_at']:%d-%m-%Y %H:%M}.",
                    "open_module": "Backup & Restore",
                }
            )
        return alerts


class ImportService:
    REQUIRED = ("farmer_name", "village", "contact_number")
    OPTIONAL = ("activity_date", "department", "activity_type")
    LABELS = {
        "farmer_name": "Farmer name",
        "village": "Village",
        "contact_number": "Mobile number",
        "activity_date": "Date",
        "department": "Department",
        "activity_type": "Activity type",
    }

    @staticmethod
    def read_file(path: str) -> Dict:
        ext = os.path.splitext(path)[1].lower()
        if ext in {".xlsx", ".xls"}:
            import pandas as pd

            frame = pd.read_excel(path, dtype=str)
        else:
            try:
                import pandas as pd

                frame = pd.read_csv(path, dtype=str)
            except ImportError:
                import csv

                with open(path, newline="", encoding="utf-8-sig") as handle:
                    reader = csv.DictReader(handle)
                    columns = reader.fieldnames or []
                    rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
                return {"columns": list(columns), "rows": rows}
        frame = frame.fillna("")
        columns = [str(column).strip() for column in frame.columns]
        rows = []
        for record in frame.to_dict(orient="records"):
            rows.append({str(key).strip(): str(value).strip() for key, value in record.items()})
        return {"columns": columns, "rows": rows}

    @staticmethod
    def suggest_mapping(columns: List[str]) -> Dict[str, str]:
        aliases = {
            "farmer_name": ["farmer name", "name", "farmer", "name of farmer"],
            "village": ["village", "farmer village"],
            "contact_number": ["mobile", "mobile number", "contact", "phone", "contact number"],
            "activity_date": ["date", "activity date"],
            "department": ["department"],
            "activity_type": ["activity", "activity type"],
        }
        lookup = {column.strip().lower(): column for column in columns}
        mapping = {}
        for field, names in aliases.items():
            mapping[field] = ""
            for name in names:
                if name in lookup:
                    mapping[field] = lookup[name]
                    break
        return mapping

    @staticmethod
    def review(rows: List[Dict], mapping: Dict[str, str]) -> Dict[str, List[Dict]]:
        session = SessionLocal()
        try:
            existing = session.query(Farmer).all()
            departments = {row.name.strip().lower(): row.id for row in session.query(Department).all()}
        finally:
            session.close()
        existing_keys = {
            ((row.farmer_name or "").strip().lower(), (row.village or "").strip().lower(), (row.contact_number or "").strip())
            for row in existing
        }
        existing_mobiles = {row.contact_number for row in existing if _valid_mobile(row.contact_number)}
        valid, invalid, duplicates = [], [], []
        seen = set()
        for index, source in enumerate(rows, start=2):
            item = {field: (source.get(mapping.get(field, ""), "") or "").strip() for field in ImportService.LABELS}
            item["row_number"] = index
            problems = []
            if not item["farmer_name"]:
                problems.append("Farmer name is required")
            if not item["village"]:
                problems.append("Village is required")
            digits = "".join(ch for ch in item["contact_number"] if ch.isdigit())
            if len(digits) != 10:
                problems.append("Mobile number must be 10 digits")
            else:
                item["contact_number"] = digits
            if item["activity_date"]:
                parsed = _parse_date(item["activity_date"])
                if parsed is None:
                    problems.append("Date is not valid")
                else:
                    item["activity_date"] = parsed.isoformat()
            if item["department"] and item["department"].lower() not in departments:
                problems.append("Department was not found")
            key = (item["farmer_name"].lower(), item["village"].lower(), item["contact_number"])
            if problems:
                item["problems"] = "; ".join(problems)
                invalid.append(item)
                continue
            if key in existing_keys or key in seen or item["contact_number"] in existing_mobiles:
                item["problems"] = "Possible duplicate of an existing farmer"
                duplicates.append(item)
                continue
            seen.add(key)
            existing_mobiles.add(item["contact_number"])
            item["department_id"] = departments.get(item["department"].lower()) if item["department"] else None
            valid.append(item)
        return {"valid": valid, "invalid": invalid, "duplicates": duplicates}

    @staticmethod
    def commit(valid_rows: List[Dict], user_id: int) -> int:
        departments = {row.id: row.name for row in ActivityService.list_departments()}
        default_department = None
        for dep_id, name in departments.items():
            if name == "Agricultural Extension":
                default_department = dep_id
                break
        if default_department is None and departments:
            default_department = next(iter(departments))
        saved = 0
        for row in valid_rows:
            payload = {
                "farmer_name": row["farmer_name"],
                "village": row["village"],
                "contact_number": row["contact_number"],
                "module_type": "Visitor Farmers",
                "department_id": row.get("department_id") or default_department,
                "season": "Kharif",
                "activity_type": row.get("activity_type") or "Imported record",
                "activity_date": _parse_date(row.get("activity_date") or "") or date.today(),
                "description": "Imported from spreadsheet",
                "remarks": "",
            }
            if not payload["department_id"]:
                raise ValueError("Add a department before importing farmers.")
            ActivityService.create_activity(payload, user_id)
            saved += 1
        AuditService.log_action(user_id, "import_farmers", "Import", None, f"Imported {saved} farmer records")
        return saved


def last_backup() -> Optional[Dict]:
    from models.entities import AuditLog

    session = SessionLocal()
    try:
        row = (
            session.query(AuditLog)
            .filter(AuditLog.action == "backup_database")
            .order_by(AuditLog.created_at.desc())
            .first()
        )
        if row is None:
            return None
        return {"created_at": row.created_at, "details": row.details or "", "status": "Completed"}
    finally:
        session.close()


def financial_year(value: date) -> str:
    if value.month >= 4:
        start = value.year
    else:
        start = value.year - 1
    return f"{start}-{str(start + 1)[-2:]}"


def _valid_mobile(value: Optional[str]) -> bool:
    text = (value or "").strip()
    return text.isdigit() and len(text) == 10 and text not in PLACEHOLDER_MOBILES


def _meaningful(value: Optional[str]) -> bool:
    return (value or "").strip().lower() not in PLACEHOLDER_TEXT


def _parse_date(value: str) -> Optional[date]:
    text = (value or "").strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y", "%d/%m/%y"):
        try:
            return datetime.strptime(text[:10], fmt).date()
        except ValueError:
            continue
    return None


def _recent_row(activity: Activity, farmer: Farmer, stamp: datetime) -> Dict:
    title = activity.oft_title or activity.training_title or activity.other_extension_title or farmer.farmer_name
    return {
        "title": title or activity.activity_type,
        "module": activity.module_type,
        "when": stamp,
        "identifier": farmer.farmer_code or "",
        "open_module": activity.module_type,
    }


def _empty_bucket() -> Dict[str, int]:
    bucket = {"farmers": 0, "participation": 0}
    for name in ActivityService.MODULES:
        bucket[name] = 0
    return bucket
