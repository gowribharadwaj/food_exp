from fastapi import APIRouter, UploadFile, File
from services.ocr_service import extract_text_from_image
from services.llm_service import parse_receipt_text

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/parse-receipt")
async def parse_receipt(file: UploadFile = File(...)):
    image_bytes = await file.read()
    raw_text = extract_text_from_image(image_bytes)

    if not raw_text:
        return {"products": [], "error": "Could not extract text from image"}

    products = parse_receipt_text(raw_text)
    return {
        "raw_text": raw_text,
        "products": products,
        "count": len(products)
    }