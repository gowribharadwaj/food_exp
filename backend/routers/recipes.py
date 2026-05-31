from fastapi import APIRouter
from models.schemas import RecipeRequest, RecipeResponse
from services.llm_service import suggest_recipes

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("/", response_model=RecipeResponse)
def get_recipes(request: RecipeRequest):
    recipes = suggest_recipes(request.expiring_items)
    return RecipeResponse(recipes=recipes)