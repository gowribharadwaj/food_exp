from pydantic import BaseModel
from typing import Optional
from datetime import date

class PantryItemCreate(BaseModel):
    name: str
    category: str
    purchase_date: date
    expiry_date: date
    storage_type: str  # pantry, fridge, freezer
    high_risk: bool = False
    quantity: Optional[str] = None

class PantryItemResponse(PantryItemCreate):
    id: str
    days_remaining: int
    urgency: str  # red, yellow, green

class ProductLookupRequest(BaseModel):
    name: str
    storage_type: str = "fridge"
    purchase_date: Optional[date] = None

class ProductLookupResponse(BaseModel):
    name: str
    category: str
    shelf_life_days: Optional[int]
    high_risk: bool
    source: str

class RecipeRequest(BaseModel):
    expiring_items: list[str]

class RecipeResponse(BaseModel):
    recipes: list[str]