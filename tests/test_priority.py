from app.services.priority import calculate_priority, sla_target_hours


def test_priority_formula_and_label_boundaries():
    assert calculate_priority("Low", 0, 0) == (20, "Low")
    assert calculate_priority("Medium", 1, 0) == (50, "Medium")
    assert calculate_priority("High", 1, 1) == (72, "High")
    assert calculate_priority("High", 10, 20) == (100, "Critical")
    assert sla_target_hours("Critical") == 24
