from datetime import datetime, timezone
from typing import Literal

Severity = Literal["Low", "Medium", "High"]
PriorityLabel = Literal["Low", "Medium", "High", "Critical"]

SEVERITY_WEIGHT: dict[Severity, int] = {"Low": 1, "Medium": 2, "High": 3}
SLA_TARGET_HOURS: dict[PriorityLabel, int] = {
    "Critical": 24,
    "High": 72,
    "Medium": 168,
    "Low": 336,
}


def calculate_priority(
    severity: Severity,
    duplicate_count: int = 0,
    days_pending: int = 0,
) -> tuple[int, PriorityLabel]:
    """Return the capped priority score and its label."""
    raw_score = SEVERITY_WEIGHT[severity] * 20 + duplicate_count * 10 + days_pending * 2
    score = min(100, max(0, raw_score))
    if score <= 30:
        label: PriorityLabel = "Low"
    elif score <= 60:
        label = "Medium"
    elif score <= 85:
        label = "High"
    else:
        label = "Critical"
    return score, label


def sla_target_hours(priority_label: PriorityLabel) -> int:
    return SLA_TARGET_HOURS[priority_label]


def days_pending_since(created_at: datetime, now: datetime | None = None) -> int:
    current = now or datetime.now(timezone.utc)
    created = created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return max(0, int((current - created).total_seconds() // 86_400))
