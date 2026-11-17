from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


Category = Literal["Sanitation", "Electricity", "Road", "Water", "Drainage", "Safety", "Other"]
Severity = Literal["Low", "Medium", "High"]
PriorityLabel = Literal["Low", "Medium", "High", "Critical"]
ComplaintStatus = Literal["Reported", "Verified", "Assigned", "Scheduled", "In Progress", "Resolved"]
AdminComplaintStatus = Literal["Reported", "Verified", "Assigned", "In Progress", "Resolved"]


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr | None
    phone_number: str | None
    role: str
    created_at: datetime


class ComplaintCreate(BaseModel):
    title: str = Field(max_length=150)
    description: str
    location: str = Field(max_length=100)
    severity: Severity
    category: Category | None = None


class ComplaintRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str
    category: Category
    category_note: str | None
    location: str
    severity: Severity
    priority_score: int
    priority_label: PriorityLabel
    status: ComplaintStatus
    photo_url_before: str | None
    photo_url_after: str | None
    is_duplicate_of: int | None
    duplicate_count: int
    sla_target_hours: int
    expected_resolution_at: datetime
    resolved_at: datetime | None
    is_overdue: bool
    feedback_rating: int | None
    feedback_comment: str | None
    created_at: datetime
    updated_at: datetime


class ComplaintUpdateCreate(BaseModel):
    new_status: ComplaintStatus
    comment: str | None = None


class ComplaintUpdateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    complaint_id: int
    old_status: ComplaintStatus
    new_status: ComplaintStatus
    comment: str | None
    updated_by: int
    updated_at: datetime


class AdminComplaintRead(ComplaintRead):
    citizen_name: str


class AdminQueueItem(BaseModel):
    id: int
    citizen_name: str
    title: str
    category: Category
    location: str
    severity: Severity
    priority_score: int
    priority_label: PriorityLabel
    status: ComplaintStatus
    days_pending: int
    duplicate_count: int
    expected_resolution_at: datetime


class AdminOverdueItem(AdminQueueItem):
    is_overdue: bool


class AdminStatusUpdate(BaseModel):
    status: AdminComplaintStatus
    comment: str | None = None


class ComplaintTimelineEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    complaint_id: int
    old_status: ComplaintStatus
    new_status: ComplaintStatus
    comment: str | None
    updated_by: int
    updated_by_name: str
    updated_at: datetime


class ComplaintFeedback(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    message: str
    complaint_id: int
    is_read: bool
    created_at: datetime


class NotificationsResponse(BaseModel):
    unread_count: int
    notifications: list[NotificationRead]


class AdminStats(BaseModel):
    total: int
    pending: int
    in_progress: int
    resolved: int
    overdue: int
    counts_by_priority_label: dict[str, int]
    counts_by_category: dict[str, int]
    average_resolution_hours_by_priority: dict[str, float | None]
