from datetime import date
from typing import Dict, List, Optional

from sqlalchemy import and_, case, cast, func, Integer, or_, String

from database.session import SessionLocal
from models.entities import Activity, Department, Farmer


class AnalyticsService:
    """Database-side analytics queries for the desktop dashboard and pivot view."""

    MODULES = [
        "Visitor Farmers",
        "On Farm Testing (OFT)",
        "Front Line Demonstrations (FLD)",
        "Training Programmes",
        "Vocational Training Programmes",
        "Extension Activities",
        "Other Extension Activities",
    ]

    ROW_FIELDS = {
        "Department": "department",
        "Village": "village",
        "District": "district",
        "Taluka / Tehsil": "tehsil",
        "Activity Type": "activity_type",
        "Season": "season",
        "Farmer Category": "farmer_category",
        "Year": "year",
        "Month": "month",
    }
    VALUE_FIELDS = {
        "Activity Count": "activity_count",
        "Farmer Count": "participant_count",
        "Training Count": "training_count",
        "OFT Count": "oft_count",
        "FLD Count": "fld_count",
    }

    @staticmethod
    def _location_expressions():
        district = func.coalesce(
            case(
                (Activity.module_type == "Visitor Farmers", Activity.visitor_district),
                (Activity.module_type.in_(["On Farm Testing (OFT)", "Front Line Demonstrations (FLD)"],), Activity.oft_farmer_district),
                (Activity.module_type.in_(["Training Programmes", "Vocational Training Programmes"],), Activity.training_farmer_district),
            ),
            "",
        )
        tehsil = func.coalesce(
            case(
                (Activity.module_type == "Visitor Farmers", Activity.visitor_tehsil),
                (Activity.module_type.in_(["On Farm Testing (OFT)", "Front Line Demonstrations (FLD)"],), Activity.oft_farmer_tehsil),
                (Activity.module_type.in_(["Training Programmes", "Vocational Training Programmes"],), Activity.training_farmer_tehsil),
            ),
            "",
        )
        # Older visitor/OFT rows stored location metadata in remarks.
        district = func.nullif(district, "")
        tehsil = func.nullif(tehsil, "")
        return district, tehsil

    @staticmethod
    def _participant_expression():
        return case(
            (Activity.module_type == "On Farm Testing (OFT)", func.coalesce(Activity.oft_farmer_count, 1)),
            (Activity.module_type == "Front Line Demonstrations (FLD)", func.coalesce(Activity.oft_farmer_count, 1)),
            (Activity.module_type.in_(["Training Programmes", "Vocational Training Programmes"],), func.coalesce(Activity.training_farmer_count, 1)),
            (Activity.module_type == "Extension Activities", func.coalesce(Activity.extension_farmer_count, 0)),
            (Activity.module_type == "Visitor Farmers", 1),
            else_=0,
        )

    @staticmethod
    def _category_expression():
        return func.coalesce(
            case(
                (Activity.module_type.in_(["On Farm Testing (OFT)", "Front Line Demonstrations (FLD)"],), Activity.oft_farmer_category),
                (Activity.module_type.in_(["Training Programmes", "Vocational Training Programmes"],), Activity.training_farmer_category),
            ),
            "Unspecified",
        )

    @staticmethod
    def _conditions(filters: Dict):
        conditions = []
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        if start_date:
            conditions.append(Activity.activity_date >= start_date)
        if end_date:
            conditions.append(Activity.activity_date <= end_date)
        if filters.get("department_id"):
            conditions.append(Activity.department_id == filters["department_id"])
        if filters.get("department"):
            conditions.append(Department.name == filters["department"])
        if filters.get("module_type") and filters["module_type"] != "All":
            conditions.append(Activity.module_type == filters["module_type"])
        if filters.get("season") and filters["season"] != "All":
            conditions.append(Activity.season == filters["season"])
        if filters.get("village") and filters["village"] != "All":
            conditions.append(Farmer.village == filters["village"])
        district, tehsil = AnalyticsService._location_expressions()
        if filters.get("district") and filters["district"] != "All":
            conditions.append(district == filters["district"])
        if filters.get("tehsil") and filters["tehsil"] != "All":
            conditions.append(tehsil == filters["tehsil"])
        if filters.get("farmer_category") and filters["farmer_category"] != "All":
            conditions.append(AnalyticsService._category_expression() == filters["farmer_category"])
        if filters.get("activity_type") and filters["activity_type"] != "All":
            conditions.append(Activity.activity_type == filters["activity_type"])
        if filters.get("year"):
            conditions.append(func.extract("year", Activity.activity_date) == int(filters["year"]))
        if filters.get("month"):
            conditions.append(func.to_char(Activity.activity_date, "YYYY-MM") == filters["month"])
        return conditions

    @staticmethod
    def _base_query(session):
        return session.query(Activity).join(Farmer, Activity.farmer_id == Farmer.id).join(Department, Activity.department_id == Department.id)

    @staticmethod
    def filter_options() -> Dict[str, List[str]]:
        session = SessionLocal()
        try:
            district, tehsil = AnalyticsService._location_expressions()
            queries = {
                "seasons": session.query(Activity.season).distinct().order_by(Activity.season),
                "activity_types": session.query(Activity.activity_type).distinct().order_by(Activity.activity_type),
                "villages": session.query(Farmer.village).distinct().order_by(Farmer.village),
                "districts": session.query(district).distinct().filter(district.isnot(None)).order_by(district),
                "tehsils": session.query(tehsil).distinct().filter(tehsil.isnot(None)).order_by(tehsil),
                "categories": session.query(AnalyticsService._category_expression()).distinct().order_by(AnalyticsService._category_expression()),
            }
            return {key: [str(value) for (value,) in query.all() if value not in (None, "")] for key, query in queries.items()}
        finally:
            session.close()

    @staticmethod
    def dashboard(filters: Dict) -> Dict:
        session = SessionLocal()
        try:
            conditions = AnalyticsService._conditions(filters)
            base = AnalyticsService._base_query(session)
            if conditions:
                base = base.filter(and_(*conditions))

            total_farmers = session.query(func.count(func.distinct(Activity.farmer_id))).join(Farmer, Activity.farmer_id == Farmer.id).join(Department, Activity.department_id == Department.id)
            if conditions:
                total_farmers = total_farmers.filter(and_(*conditions))
            total_departments = session.query(func.count(Department.id))

            count_for = lambda name: base.filter(Activity.module_type == name).with_entities(func.count(Activity.id)).scalar() or 0
            kpis = {
                "Total Farmers": total_farmers.scalar() or 0,
                "Total Activities": base.with_entities(func.count(Activity.id)).scalar() or 0,
                "Total OFT Activities": count_for("On Farm Testing (OFT)"),
                "Total FLD Activities": count_for("Front Line Demonstrations (FLD)"),
                "Total Training Programmes": base.filter(Activity.module_type.in_(["Training Programmes", "Vocational Training Programmes"])).with_entities(func.count(Activity.id)).scalar() or 0,
                "Total Extension Activities": base.filter(Activity.module_type.in_(["Extension Activities", "Other Extension Activities"])).with_entities(func.count(Activity.id)).scalar() or 0,
                "Total Farmers Participated": base.with_entities(func.coalesce(func.sum(AnalyticsService._participant_expression()), 0)).scalar() or 0,
                "Total Departments": total_departments.scalar() or 0,
            }

            by_department = AnalyticsService._grouped(session, base, Department.name, "department")
            by_module = AnalyticsService._grouped(session, base, Activity.module_type, "module")
            by_season = AnalyticsService._grouped(session, base, Activity.season, "season", participant=True)
            by_category = AnalyticsService._grouped(session, base, AnalyticsService._category_expression(), "category", participant=True)
            by_time = AnalyticsService._time_series(session, base)
            department_performance = AnalyticsService._department_performance(session, base)
            top_villages = AnalyticsService._top_villages(session, base, 10)
            return {
                "kpis": kpis,
                "by_department": by_department,
                "by_module": by_module,
                "by_season": by_season,
                "by_category": by_category,
                "by_time": by_time,
                "department_performance": department_performance,
                "top_villages": top_villages,
            }
        finally:
            session.close()

    @staticmethod
    def _grouped(session, base, expression, key, participant=False):
        query = base.with_entities(expression.label(key), func.count(Activity.id).label("count"))
        if participant:
            query = base.with_entities(expression.label(key), func.coalesce(func.sum(AnalyticsService._participant_expression()), 0).label("count"))
        return [{"label": str(label or "Unspecified"), "value": int(value or 0)} for label, value in query.group_by(expression).order_by(func.count(Activity.id).desc()).all()]

    @staticmethod
    def _time_series(session, base):
        month = func.to_char(Activity.activity_date, "YYYY-MM")
        return [{"label": str(label), "value": int(value or 0)} for label, value in base.with_entities(month, func.count(Activity.id)).group_by(month).order_by(month).all()]

    @staticmethod
    def _department_performance(session, base):
        query = base.with_entities(
            Department.name,
            func.count(Activity.id),
            func.coalesce(func.sum(AnalyticsService._participant_expression()), 0),
            func.sum(case((Activity.module_type.in_(["Training Programmes", "Vocational Training Programmes"],), 1), else_=0)),
            func.sum(case((Activity.module_type == "On Farm Testing (OFT)", 1), else_=0)),
            func.sum(case((Activity.module_type == "Front Line Demonstrations (FLD)", 1), else_=0)),
        ).group_by(Department.name).order_by(func.count(Activity.id).desc())
        return [{"department": name, "activities": int(a or 0), "participants": int(p or 0), "trainings": int(t or 0), "oft": int(o or 0), "fld": int(f or 0)} for name, a, p, t, o, f in query.all()]

    @staticmethod
    def _top_villages(session, base, limit):
        query = base.with_entities(Farmer.village, func.count(Activity.id)).filter(Farmer.village.isnot(None)).group_by(Farmer.village).order_by(func.count(Activity.id).desc()).limit(limit)
        return [{"label": village or "Unspecified", "value": int(count or 0)} for village, count in query.all()]

    @staticmethod
    def pivot(filters: Dict, row_field: str, column_field: str, value_field: str, aggregation: str) -> Dict:
        if row_field not in AnalyticsService.ROW_FIELDS or column_field not in AnalyticsService.ROW_FIELDS:
            raise ValueError("Unsupported pivot dimension")
        if value_field not in AnalyticsService.VALUE_FIELDS:
            raise ValueError("Unsupported pivot value")
        if aggregation not in {"Count", "Sum", "Average", "Minimum", "Maximum"}:
            raise ValueError("Unsupported aggregation")

        session = SessionLocal()
        try:
            district, tehsil = AnalyticsService._location_expressions()
            dimensions = {
                "department": Department.name,
                "village": Farmer.village,
                "district": func.coalesce(district, "Unspecified"),
                "tehsil": func.coalesce(tehsil, "Unspecified"),
                "activity_type": Activity.activity_type,
                "season": Activity.season,
                "farmer_category": AnalyticsService._category_expression(),
                "year": func.extract("year", Activity.activity_date),
                "month": func.to_char(Activity.activity_date, "YYYY-MM"),
            }
            row_expr = dimensions[AnalyticsService.ROW_FIELDS[row_field]]
            col_expr = dimensions[AnalyticsService.ROW_FIELDS[column_field]]
            value_expr = {
                "activity_count": Activity.id,
                "participant_count": AnalyticsService._participant_expression(),
                "training_count": case((Activity.module_type.in_(["Training Programmes", "Vocational Training Programmes"],), 1), else_=0),
                "oft_count": case((Activity.module_type == "On Farm Testing (OFT)", 1), else_=0),
                "fld_count": case((Activity.module_type == "Front Line Demonstrations (FLD)", 1), else_=0),
            }[AnalyticsService.VALUE_FIELDS[value_field]]
            aggregate = {"Count": func.count, "Sum": func.sum, "Average": func.avg, "Minimum": func.min, "Maximum": func.max}[aggregation](value_expr)
            query = AnalyticsService._base_query(session).with_entities(row_expr, col_expr, aggregate).filter(and_(*AnalyticsService._conditions(filters))).group_by(row_expr, col_expr).order_by(row_expr, col_expr)
            rows = query.all()
            row_labels = sorted({str(row or "Unspecified") for row, _, _ in rows})
            col_labels = sorted({str(col or "Unspecified") for _, col, _ in rows})
            matrix = {row: {col: 0 for col in col_labels} for row in row_labels}
            for row, col, value in rows:
                matrix[str(row or "Unspecified")][str(col or "Unspecified")] = round(float(value or 0), 2)
            return {"rows": row_labels, "columns": col_labels, "matrix": matrix}
        finally:
            session.close()

    @staticmethod
    def detail_records(filters: Dict, limit: int = 500) -> List[Dict]:
        session = SessionLocal()
        try:
            query = AnalyticsService._base_query(session).with_entities(Activity.id, Activity.activity_date, Activity.module_type, Activity.activity_type, Department.name, Farmer.farmer_name, Farmer.village)
            conditions = AnalyticsService._conditions(filters)
            if conditions:
                query = query.filter(and_(*conditions))
            return [{"id": i, "date": str(d), "module": m, "activity": a, "department": dept, "farmer": farmer, "village": village} for i, d, m, a, dept, farmer, village in query.order_by(Activity.activity_date.desc()).limit(limit).all()]
        finally:
            session.close()
