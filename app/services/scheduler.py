from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

from app.database import get_session_factory
from app.models import Complaint
from app.services.priority import calculate_priority, days_pending_since

UNRESOLVED_STATUSES = ("Reported", "Verified", "Assigned", "Scheduled", "In Progress")

scheduler = BackgroundScheduler(timezone=timezone.utc)


def recalculate_unresolved() -> dict[str, int | str]:
    """Refresh age-based priority and overdue state for unresolved complaints."""
    session = get_session_factory()()
    now = datetime.now(timezone.utc)
    updated = 0
    try:
        complaints = session.scalars(
            select(Complaint).where(Complaint.status.in_(UNRESOLVED_STATUSES))
        ).all()
        for complaint in complaints:
            days_pending = days_pending_since(complaint.created_at, now)
            score, label = calculate_priority(complaint.severity, complaint.duplicate_count, days_pending)
            overdue = complaint.expected_resolution_at <= now
            if (
                complaint.priority_score != score
                or complaint.priority_label != label
                or complaint.is_overdue != overdue
            ):
                complaint.priority_score = score
                complaint.priority_label = label
                complaint.is_overdue = overdue
                updated += 1
        session.commit()
        return {"updated": updated, "checked": len(complaints), "run_at": now.isoformat()}
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(
        recalculate_unresolved,
        trigger="interval",
        minutes=15,
        id="recalculate_unresolved_complaints",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=True)
