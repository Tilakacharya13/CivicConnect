from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Complaint, ComplaintUpdate, User
from app.schemas import ComplaintCreate, ComplaintFeedback, ComplaintRead
from app.services.categorizer import categorize_complaint
from app.services.duplicates import find_and_link_duplicate
from app.services.priority import calculate_priority, sla_target_hours
from app.services.uploads import save_image

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.post("", response_model=ComplaintRead, status_code=status.HTTP_201_CREATED)
def create_complaint(
    payload: ComplaintCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Complaint:
    if current_user.role != "citizen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only citizens can submit complaints")

    category = categorize_complaint(payload.description, payload.category)
    duplicate_count = 0
    score, label = calculate_priority(payload.severity, duplicate_count=duplicate_count, days_pending=0)
    sla_hours = sla_target_hours(label)
    now = datetime.now(timezone.utc)

    complaint = Complaint(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        category=category,
        category_note=None,
        location=payload.location,
        severity=payload.severity,
        priority_score=score,
        priority_label=label,
        status="Reported",
        photo_url_before=None,
        photo_url_after=None,
        is_duplicate_of=None,
        duplicate_count=duplicate_count,
        sla_target_hours=sla_hours,
        expected_resolution_at=now + timedelta(hours=sla_hours),
        is_overdue=False,
    )
    db.add(complaint)
    db.flush()
    find_and_link_duplicate(db, complaint, now=now)
    db.add(
        ComplaintUpdate(
            complaint_id=complaint.id,
            old_status="Reported",
            new_status="Reported",
            comment="Complaint created with status Reported",
            updated_by=current_user.id,
        )
    )
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("/my", response_model=list[ComplaintRead])
def list_my_complaints(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Complaint]:
    return list(
        db.scalars(
            select(Complaint)
            .where(Complaint.user_id == current_user.id)
            .order_by(Complaint.created_at.desc())
        )
    )


@router.get("/{complaint_id}", response_model=ComplaintRead)
def get_complaint(
    complaint_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Complaint:
    complaint = db.get(Complaint, complaint_id)
    if complaint is None or (complaint.user_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    return complaint


@router.get("/{complaint_id}/timeline")
def complaint_timeline(
    complaint_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    from app.schemas import ComplaintTimelineEntry

    complaint = db.get(Complaint, complaint_id)
    if complaint is None or (complaint.user_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=404, detail="Complaint not found")
    rows = db.execute(
        select(ComplaintUpdate, User.name)
        .join(User, User.id == ComplaintUpdate.updated_by)
        .where(ComplaintUpdate.complaint_id == complaint_id)
        .order_by(ComplaintUpdate.updated_at.asc(), ComplaintUpdate.id.asc())
    ).all()
    return [
        ComplaintTimelineEntry(
            id=update.id,
            complaint_id=update.complaint_id,
            old_status=update.old_status,
            new_status=update.new_status,
            comment=update.comment,
            updated_by=update.updated_by,
            updated_by_name=name,
            updated_at=update.updated_at,
        )
        for update, name in rows
    ]


@router.post("/{complaint_id}/photo")
async def upload_before_photo(
    complaint_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
):
    complaint = db.get(Complaint, complaint_id)
    if complaint is None or complaint.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Complaint not found")
    photo_url = await save_image(file)
    complaint.photo_url_before = photo_url
    db.commit()
    return {"photo_url_before": photo_url}


@router.post("/{complaint_id}/feedback", response_model=ComplaintRead)
def submit_feedback(
    complaint_id: int,
    payload: ComplaintFeedback,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    complaint = db.get(Complaint, complaint_id)
    if complaint is None or complaint.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if complaint.status != "Resolved":
        raise HTTPException(status_code=409, detail="Feedback can only be submitted for resolved complaints")
    if complaint.feedback_rating is not None:
        raise HTTPException(status_code=409, detail="Feedback has already been submitted for this complaint")
    complaint.feedback_rating = payload.rating
    complaint.feedback_comment = payload.comment
    db.commit()
    db.refresh(complaint)
    return complaint
