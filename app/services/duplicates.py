from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Complaint
from app.services.priority import calculate_priority, days_pending_since, sla_target_hours


def find_and_link_duplicate(
    db: Session,
    new_complaint: Complaint,
    now: datetime | None = None,
) -> Complaint | None:
    """Link a new report to the oldest matching unresolved report from the last week."""
    current = now or datetime.now(timezone.utc)
    cutoff = current - timedelta(days=7)
    category = new_complaint.category.strip().casefold()
    location = new_complaint.location.strip().casefold()

    original = db.scalar(
        select(Complaint)
        .where(
            Complaint.id != new_complaint.id,
            Complaint.status != "Resolved",
            Complaint.created_at >= cutoff,
            func.lower(func.trim(Complaint.category)) == category,
            func.lower(func.trim(Complaint.location)) == location,
        )
        .order_by(Complaint.created_at.asc(), Complaint.id.asc())
        .with_for_update()
        .limit(1)
    )
    if original is None:
        return None

    new_complaint.is_duplicate_of = original.id
    original.duplicate_count += 1
    days_pending = days_pending_since(original.created_at, current)
    score, label = calculate_priority(original.severity, original.duplicate_count, days_pending)
    original.priority_score = score
    original.priority_label = label
    original.sla_target_hours = sla_target_hours(label)
    original.expected_resolution_at = current + timedelta(hours=original.sla_target_hours)
    original.is_overdue = original.expected_resolution_at <= current
    return original
