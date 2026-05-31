from fastapi import APIRouter
from models.schemas import ProductLookupRequest, ProductLookupResponse
from services.product_lookup import lookup_product

router = APIRouter(prefix="/lookup", tags=["lookup"])


@router.post("/", response_model=ProductLookupResponse)
def lookup(request: ProductLookupRequest):
    result = lookup_product(request.name, request.storage_type)
    return ProductLookupResponse(**result)