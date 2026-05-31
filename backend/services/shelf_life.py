import json
import os
from datetime import date, timedelta

KB_PATH = os.path.join(os.path.dirname(__file__), "../data/pantry_knowledge_base.json")

# Load once at startup
with open(KB_PATH, "r", encoding="utf-8") as f:
    KNOWLEDGE_BASE = json.load(f)

# Build a flat name+alias lookup dict for fast search
LOOKUP = {}
for item in KNOWLEDGE_BASE:
    LOOKUP[item["name"].lower()] = item
    for alias in item.get("aliases", []):
        LOOKUP[alias.lower()] = item


def find_item(product_name: str):
    """Find an item in the knowledge base by name or alias."""
    return LOOKUP.get(product_name.strip().lower())


def get_shelf_life(product_name: str, storage_type: str = "fridge") -> dict:
    """
    Returns shelf life in days for a product given storage type.
    storage_type: 'fridge', 'freezer', 'pantry'
    """
    item = find_item(product_name)
    if not item:
        return {"days": None, "source": "not_found", "high_risk": False, "category": "unknown"}

    sl = item.get("shelf_life", {})
    key = f"{storage_type}_days"
    days = sl.get(key)

    # Fallback: if requested storage has no data, try fridge
    if days is None and storage_type != "fridge":
        days = sl.get("fridge_days")

    return {
        "days": days,
        "source": item.get("source", "unknown"),
        "high_risk": item.get("high_risk", False),
        "category": item.get("category", "unknown")
    }


def calculate_expiry(purchase_date: date, shelf_life_days: int) -> date:
    return purchase_date + timedelta(days=shelf_life_days)


def get_urgency(expiry_date: date) -> tuple[str, int]:
    """Returns (color, days_remaining)"""
    today = date.today()
    days_remaining = (expiry_date - today).days

    if days_remaining <= 1:
        return "red", days_remaining
    elif days_remaining <= 4:
        return "yellow", days_remaining
    else:
        return "green", days_remaining