from datetime import datetime, timedelta, timezone

from app.models import Complaint, User
from app.services.duplicates import find_and_link_duplicate


def complaint(user_id, title, created_at, location="Central Park"):
    return Complaint(
        user_id=user_id, title=title, description="Broken street light", category="Electricity",
        location=location, severity="High", priority_score=60, priority_label="Medium",
        status="Reported", duplicate_count=0, sla_target_hours=168,
        expected_resolution_at=created_at + timedelta(hours=168), is_overdue=False,
        created_at=created_at,
    )


def test_duplicate_link_increments_and_recalculates_original(db_session):
    now = datetime(2026, 10, 4, tzinfo=timezone.utc)
    user = User(name="A", email="a@example.test", password_hash="x", role="citizen")
    db_session.add(user)
    db_session.flush()
    original = complaint(user.id, "Original", now - timedelta(days=2))
    db_session.add(original)
    db_session.flush()
    duplicate = complaint(user.id, "Similar", now, location=" central park ")
    db_session.add(duplicate)
    db_session.flush()

    matched = find_and_link_duplicate(db_session, duplicate, now)

    assert matched is original
    assert duplicate.is_duplicate_of == original.id
    assert original.duplicate_count == 1
    assert original.priority_score == 74
    assert original.priority_label == "High"
    assert original.sla_target_hours == 72
