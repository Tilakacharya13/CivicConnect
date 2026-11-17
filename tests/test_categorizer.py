from app.services.categorizer import categorize_complaint


def test_keyword_categories_and_explicit_category():
    assert categorize_complaint("Overflowing garbage bins by the park") == "Sanitation"
    assert categorize_complaint("Power outage on the block") == "Electricity"
    assert categorize_complaint("Unrecognized concern", "Road") == "Road"
    assert categorize_complaint("Unrecognized concern") == "Other"
