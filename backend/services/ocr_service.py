import pytesseract
from PIL import Image
import io


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Takes raw image bytes from an uploaded file.
    Returns extracted text string.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if needed (handles PNG with alpha channel)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Tesseract config: assume sparse text (receipt layout)
        custom_config = r"--oem 3 --psm 6"
        text = pytesseract.image_to_string(image, config=custom_config)
        return text.strip()

    except Exception as e:
        print(f"OCR error: {e}")
        return ""