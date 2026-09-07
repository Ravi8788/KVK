from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'staff')", name="chk_user_role"),
    )


class Farmer(Base):
    __tablename__ = "farmers"

    id: Mapped[int] = mapped_column(primary_key=True)
    farmer_name: Mapped[str] = mapped_column(String(150), nullable=False)
    village: Mapped[str] = mapped_column(String(150), nullable=False)
    contact_number: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    module_type: Mapped[str] = mapped_column(String(60), nullable=False)
    farmer_id: Mapped[int] = mapped_column(ForeignKey("farmers.id"), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    season: Mapped[str] = mapped_column(String(20), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(150), nullable=False)
    activity_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    visitor_scientist: Mapped[Optional[str]] = mapped_column(String(150))
    visitor_district: Mapped[Optional[str]] = mapped_column(String(100))
    visitor_tehsil: Mapped[Optional[str]] = mapped_column(String(100))
    oft_title: Mapped[Optional[str]] = mapped_column(String(255))
    oft_batch_key: Mapped[Optional[str]] = mapped_column(String(64))
    oft_crop_variety: Mapped[Optional[str]] = mapped_column(String(255))
    oft_farmer_count: Mapped[Optional[int]] = mapped_column(Integer)
    oft_technical_assessment: Mapped[Optional[str]] = mapped_column(Text)
    oft_area: Mapped[Optional[str]] = mapped_column(String(255))
    oft_farmer_scientist: Mapped[Optional[str]] = mapped_column(String(150))
    oft_farmer_purpose: Mapped[Optional[str]] = mapped_column(String(100))
    oft_farmer_district: Mapped[Optional[str]] = mapped_column(String(100))
    oft_farmer_tehsil: Mapped[Optional[str]] = mapped_column(String(100))
    oft_farmer_category: Mapped[Optional[str]] = mapped_column(String(50))
    training_title: Mapped[Optional[str]] = mapped_column(String(255))
    training_type: Mapped[Optional[str]] = mapped_column(String(50))
    training_end_date: Mapped[Optional[date]] = mapped_column(Date)
    clientele: Mapped[Optional[str]] = mapped_column(String(10))
    thematic_area: Mapped[Optional[str]] = mapped_column(String(255))
    venue: Mapped[Optional[str]] = mapped_column(String(255))
    venue_is_offline: Mapped[Optional[bool]] = mapped_column(Boolean)
    venue_village: Mapped[Optional[str]] = mapped_column(String(150))
    venue_taluka: Mapped[Optional[str]] = mapped_column(String(150))
    venue_district: Mapped[Optional[str]] = mapped_column(String(150))
    training_farmer_count: Mapped[Optional[int]] = mapped_column(Integer)
    training_farmer_category: Mapped[Optional[str]] = mapped_column(String(50))
    training_farmer_scientist: Mapped[Optional[str]] = mapped_column(String(150))
    training_farmer_purpose: Mapped[Optional[str]] = mapped_column(String(100))
    training_farmer_district: Mapped[Optional[str]] = mapped_column(String(100))
    training_farmer_tehsil: Mapped[Optional[str]] = mapped_column(String(100))
    extension_venue: Mapped[Optional[str]] = mapped_column(String(255))
    extension_location: Mapped[Optional[str]] = mapped_column(String(255))
    extension_department: Mapped[Optional[str]] = mapped_column(String(150))
    extension_purpose: Mapped[Optional[str]] = mapped_column(Text)
    extension_farmer_count: Mapped[Optional[int]] = mapped_column(Integer)
    other_extension_title: Mapped[Optional[str]] = mapped_column(String(255))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    farmer: Mapped[Farmer] = relationship()
    department: Mapped[Department] = relationship()
    creator: Mapped[User] = relationship()

    __table_args__ = (
        CheckConstraint("season IN ('Kharif', 'Rabi')", name="chk_activity_season"),
        CheckConstraint("clientele IS NULL OR clientele IN ('PF', 'RY', 'EF')", name="chk_activity_clientele"),
        Index("idx_activities_date", "activity_date"),
        Index("idx_activities_department", "department_id"),
        Index("idx_activities_module", "module_type"),
        Index("idx_activities_activity_type", "activity_type"),
    )


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_name: Mapped[str] = mapped_column(String(200), nullable=False)
    generated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    filter_json: Mapped[Optional[str]] = mapped_column(Text)
    file_path: Mapped[Optional[str]] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    module_type: Mapped[Optional[str]] = mapped_column(String(60))
    record_id: Mapped[Optional[int]] = mapped_column()
    details: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_audit_logs_created_at", "created_at"),
    )
