from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Complaint, ComplaintUpdate, Notification, User
from app.schemas import AdminComplaintRead, AdminOverdueItem, AdminQueueItem, AdminStats, AdminStatusUpdate
from app.services.priority import days_pending_since
from app.services.scheduler import recalculate_unresolved
from app.services.uploads import save_image

router = APIRouter(prefix="/admin", tags=["admin"])
_optional_bearer = HTTPBearer(auto_error=False)
UNRESOLVED = ("Reported", "Verified", "Assigned", "Scheduled", "In Progress")
PENDING = ("Reported", "Verified", "Assigned")
PRIORITIES = ("Critical", "High", "Medium", "Low")
CATEGORIES = ("Sanitation", "Electricity", "Road", "Water", "Drainage", "Safety", "Other")


def get_admin_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_optional_bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise HTTPException(401, "Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    user = get_current_user(credentials, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


AdminDep = Annotated[User, Depends(get_admin_user)]
DbDep = Annotated[Session, Depends(get_db)]


def _with_name(complaint: Complaint, name: str) -> dict:
    result = {column.name: getattr(complaint, column.name) for column in Complaint.__table__.columns}
    result["citizen_name"] = name
    return result


@router.get("/complaints", response_model=list[AdminComplaintRead])
def list_all_complaints(
    db: DbDep,
    _admin: AdminDep,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    priority_label: str | None = None,
    category: str | None = None,
    is_overdue: bool | None = None,
    search: str | None = None,
):
    query = select(Complaint, User.name).join(User, User.id == Complaint.user_id)
    if status_filter is not None:
        query = query.where(Complaint.status == status_filter)
    if priority_label is not None:
        query = query.where(Complaint.priority_label == priority_label)
    if category is not None:
        query = query.where(Complaint.category == category)
    if is_overdue is not None:
        query = query.where(Complaint.is_overdue == is_overdue)
    if search:
        query = query.where(Complaint.title.ilike(f"%{search}%"))
    rows = db.execute(query.order_by(Complaint.created_at.desc())).all()
    return [_with_name(complaint, name) for complaint, name in rows]


@router.get("/queue")
def queue(db: DbDep, _admin: AdminDep):
    grouped = {label: [] for label in PRIORITIES}
    rows = db.execute(
        select(Complaint, User.name)
        .join(User, User.id == Complaint.user_id)
        .where(Complaint.status.in_(UNRESOLVED))
    ).all()
    for complaint, name in rows:
        item = AdminQueueItem(
            id=complaint.id, citizen_name=name, title=complaint.title,
            category=complaint.category, location=complaint.location,
            severity=complaint.severity, priority_score=complaint.priority_score,
            priority_label=complaint.priority_label, status=complaint.status,
            days_pending=days_pending_since(complaint.created_at),
            duplicate_count=complaint.duplicate_count,
            expected_resolution_at=complaint.expected_resolution_at,
        )
        grouped.setdefault(complaint.priority_label, []).append(item.model_dump())
    for items in grouped.values():
        items.sort(key=lambda item: item["priority_score"], reverse=True)
    return grouped


@router.get("/overdue", response_model=list[AdminOverdueItem])
def overdue(db: DbDep, _admin: AdminDep):
    now = datetime.now(timezone.utc)
    rows = db.execute(
        select(Complaint, User.name)
        .join(User, User.id == Complaint.user_id)
        .where(Complaint.status.in_(UNRESOLVED), Complaint.expected_resolution_at < now)
        .order_by(Complaint.expected_resolution_at.asc())
    ).all()
    result = []
    for complaint, name in rows:
        result.append({
            "id": complaint.id, "citizen_name": name, "title": complaint.title,
            "category": complaint.category, "location": complaint.location,
            "severity": complaint.severity, "priority_score": complaint.priority_score,
            "priority_label": complaint.priority_label, "status": complaint.status,
            "days_pending": days_pending_since(complaint.created_at),
            "duplicate_count": complaint.duplicate_count,
            "expected_resolution_at": complaint.expected_resolution_at,
            "is_overdue": True,
        })
    return result


@router.get("/stats", response_model=AdminStats)
def stats(db: DbDep, _admin: AdminDep):
    complaints = list(db.scalars(select(Complaint)))
    now = datetime.now(timezone.utc)
    averages: dict[str, list[float]] = {label: [] for label in PRIORITIES}
    for complaint in complaints:
        if complaint.status == "Resolved" and complaint.resolved_at is not None:
            created = complaint.created_at
            resolved = complaint.resolved_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            if resolved.tzinfo is None:
                resolved = resolved.replace(tzinfo=timezone.utc)
            averages.setdefault(complaint.priority_label, []).append((resolved - created).total_seconds() / 3600)
    return AdminStats(
        total=len(complaints),
        pending=sum(c.status in PENDING for c in complaints),
        in_progress=sum(c.status == "In Progress" for c in complaints),
        resolved=sum(c.status == "Resolved" for c in complaints),
        overdue=sum(c.status in UNRESOLVED and c.expected_resolution_at < now for c in complaints),
        counts_by_priority_label={label: sum(c.priority_label == label for c in complaints) for label in PRIORITIES},
        counts_by_category={category: sum(c.category == category for c in complaints) for category in CATEGORIES},
        average_resolution_hours_by_priority={label: (sum(values) / len(values) if values else None) for label, values in averages.items()},
    )


@router.patch("/complaints/{complaint_id}/status")
def update_status(complaint_id: int, payload: AdminStatusUpdate, db: DbDep, admin: AdminDep):
    complaint = db.get(Complaint, complaint_id)
    if complaint is None:
        raise HTTPException(404, "Complaint not found")
    old_status = complaint.status
    complaint.status = payload.status
    now = datetime.now(timezone.utc)
    complaint.resolved_at = now if payload.status == "Resolved" else None
    complaint.is_overdue = False if payload.status == "Resolved" else complaint.is_overdue
    db.add(ComplaintUpdate(
        complaint_id=complaint.id, old_status=old_status, new_status=payload.status,
        comment=payload.comment, updated_by=admin.id,
    ))
    if old_status != payload.status:
        db.add(Notification(
            user_id=complaint.user_id,
            complaint_id=complaint.id,
            message=f"Your complaint '{complaint.title}' is now {payload.status}",
        ))
    db.commit()
    db.refresh(complaint)
    return complaint


@router.post("/complaints/{complaint_id}/after-photo")
async def upload_after_photo(
    complaint_id: int,
    db: DbDep,
    _admin: AdminDep,
    file: UploadFile = File(...),
):
    complaint = db.get(Complaint, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if complaint.status != "Resolved":
        raise HTTPException(status_code=409, detail="An after photo can only be added to a resolved complaint")
    photo_url = await save_image(file)
    complaint.photo_url_after = photo_url
    db.commit()
    return {"photo_url_after": photo_url}


@router.post("/recalculate")
def recalculate(_admin: AdminDep):
    return recalculate_unresolved()
