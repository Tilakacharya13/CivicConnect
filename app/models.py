from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('citizen', 'admin')", name="ck_users_role"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    firebase_uid: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="citizen", server_default="citizen")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    complaints: Mapped[list["Complaint"]] = relationship(back_populates="user", foreign_keys="Complaint.user_id")
    complaint_updates: Mapped[list["ComplaintUpdate"]] = relationship(back_populates="updated_by_user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Complaint(Base):
    __tablename__ = "complaints"
    __table_args__ = (
        CheckConstraint("category IN ('Sanitation', 'Electricity', 'Road', 'Water', 'Drainage', 'Safety', 'Other')", name="ck_complaints_category"),
        CheckConstraint("severity IN ('Low', 'Medium', 'High')", name="ck_complaints_severity"),
        CheckConstraint("priority_score BETWEEN 0 AND 100", name="ck_complaints_priority_score"),
        CheckConstraint("priority_label IN ('Low', 'Medium', 'High', 'Critical')", name="ck_complaints_priority_label"),
        CheckConstraint("status IN ('Reported', 'Verified', 'Assigned', 'Scheduled', 'In Progress', 'Resolved')", name="ck_complaints_status"),
        CheckConstraint("feedback_rating IS NULL OR feedback_rating BETWEEN 1 AND 5", name="ck_complaints_feedback_rating"),
        CheckConstraint("category = 'Other' OR category_note IS NULL", name="ck_complaints_category_note"),
        CheckConstraint("status = 'Resolved' OR photo_url_after IS NULL", name="ck_complaints_after_photo_resolved"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    category_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    priority_score: Mapped[int] = mapped_column(Integer, nullable=False)
    priority_label: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    photo_url_before: Mapped[str | None] = mapped_column(String(255), nullable=True)
    photo_url_after: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_duplicate_of: Mapped[int | None] = mapped_column(ForeignKey("complaints.id"), nullable=True)
    duplicate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    sla_target_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    expected_resolution_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_overdue: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    feedback_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feedback_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship(back_populates="complaints", foreign_keys=[user_id])
    duplicate_of: Mapped["Complaint | None"] = relationship(remote_side=[id], back_populates="duplicates")
    duplicates: Mapped[list["Complaint"]] = relationship(back_populates="duplicate_of")
    updates: Mapped[list["ComplaintUpdate"]] = relationship(back_populates="complaint", cascade="all, delete-orphan")


class ComplaintUpdate(Base):
    __tablename__ = "complaint_updates"
    __table_args__ = (
        CheckConstraint("old_status IN ('Reported', 'Verified', 'Assigned', 'Scheduled', 'In Progress', 'Resolved')", name="ck_complaint_updates_old_status"),
        CheckConstraint("new_status IN ('Reported', 'Verified', 'Assigned', 'Scheduled', 'In Progress', 'Resolved')", name="ck_complaint_updates_new_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), nullable=False)
    old_status: Mapped[str] = mapped_column(String(20), nullable=False)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    complaint: Mapped[Complaint] = relationship(back_populates="updates")
    updated_by_user: Mapped[User] = relationship(back_populates="complaint_updates")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="notifications")
    complaint: Mapped[Complaint] = relationship()
