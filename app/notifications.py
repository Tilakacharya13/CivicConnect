from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Notification, User
from app.schemas import NotificationsResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])
DbDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=NotificationsResponse)
def list_notifications(db: DbDep, current_user: UserDep):
    items = list(db.scalars(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
    ))
    unread_count = sum(not item.is_read for item in items)
    return {"unread_count": unread_count, "notifications": items}


@router.patch("/{notification_id}/read", response_model=NotificationsResponse)
def mark_notification_read(notification_id: int, db: DbDep, current_user: UserDep):
    notification = db.get(Notification, notification_id)
    if notification is None or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    db.commit()
    return list_notifications(db, current_user)


@router.patch("/read-all", response_model=NotificationsResponse)
def mark_all_notifications_read(db: DbDep, current_user: UserDep):
    db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    db.commit()
    return list_notifications(db, current_user)
