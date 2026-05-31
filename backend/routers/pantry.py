from fastapi import APIRouter, HTTPException
from models.schemas import PantryItemCreate, PantryItemResponse
from services.shelf_life import get_urgency
from datetime import date
import uuid

router = APIRouter(prefix="/pantry", tags=["pantry"])

# In-memory store for now — replace with Supabase later
PANTRY: dict = {}


@router.get("/", response_model=list[PantryItemResponse])
def get_pantry():
    items = []
    for item in PANTRY.values():
        urgency, days_remaining = get_urgency(item["expiry_date"])
        items.append(PantryItemResponse(
            **item,
            days_remaining=days_remaining,
            urgency=urgency
        ))
    # Sort by urgency: red first, then yellow, then green
    priority = {"red": 0, "yellow": 1, "green": 2}
    items.sort(key=lambda x: priority.get(x.urgency, 3))
    return items


@router.post("/", response_model=PantryItemResponse)
def add_item(item: PantryItemCreate):
    item_id = str(uuid.uuid4())
    PANTRY[item_id] = {"id": item_id, **item.model_dump()}
    urgency, days_remaining = get_urgency(item.expiry_date)
    return PantryItemResponse(
        **PANTRY[item_id],
        days_remaining=days_remaining,
        urgency=urgency
    )


@router.delete("/{item_id}")
def delete_item(item_id: str):
    if item_id not in PANTRY:
        raise HTTPException(status_code=404, detail="Item not found")
    del PANTRY[item_id]
    return {"message": "Item deleted"}