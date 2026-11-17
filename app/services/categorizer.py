from app.schemas import Category


KEYWORDS: dict[str, tuple[str, ...]] = {
    "Safety": ("unsafe", "danger", "security", "harassment", "accident", "crime", "exposed wire", "open manhole"),
    "Drainage": ("drainage", "drain", "sewer", "clogged", "stormwater", "waterlogging", "flooded", "flooding"),
    "Sanitation": ("garbage", "trash", "waste", "litter", "rubbish", "refuse", "overflowing bin", "cleaning"),
    "Electricity": ("electricity", "electric", "power outage", "power cut", "transformer", "streetlight", "street light", "light pole"),
    "Road": ("road", "pothole", "street", "sidewalk", "pavement", "traffic"),
    "Water": ("water", "tap", "water supply", "pipeline", "leak", "burst pipe"),
}


def categorize_complaint(description: str, category: Category | None = None) -> Category:
    """Use the supplied category, or infer one from description keywords."""
    if category is not None:
        return category

    normalized = description.casefold()
    for matched_category, keywords in KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return matched_category  # type: ignore[return-value]
    return "Other"
