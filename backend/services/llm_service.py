import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"


def ask_ollama(prompt: str) -> str:
    """Send a prompt to local Ollama and return the response text."""
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=60)

        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return ""
    except Exception as e:
        print(f"Ollama error: {e}")
        return ""


def parse_receipt_text(raw_text: str) -> list[str]:
    """
    Takes messy OCR text from a receipt.
    Returns a clean list of product names.
    """
    prompt = f"""
You are a grocery receipt parser.
Extract only the product/item names from this receipt text.
Ignore prices, quantities, totals, store name, date, and tax.
Return only a plain list, one item per line, nothing else.

Receipt text:
{raw_text}

Product names:
"""
    response = ask_ollama(prompt)
    if not response:
        return []

    lines = [line.strip("•-– ").strip()
             for line in response.split("\n")
             if line.strip()]
    return [l for l in lines if l and len(l) > 1]


def suggest_recipes(expiring_items: list[str]) -> list[str]:
    """
    Takes a list of expiring items.
    Returns 2-3 recipe suggestions as strings.
    """
    items_str = ", ".join(expiring_items)
    prompt = f"""
You are a helpful Indian cooking assistant.
I have these ingredients expiring soon: {items_str}
Suggest 2 simple Indian recipes I can make using some or all of these.
For each recipe give: name and 3-line method. Keep it brief.
"""
    response = ask_ollama(prompt)
    if not response:
        return ["Could not generate recipes. Make sure Ollama is running."]

    # Split into individual recipes roughly
    recipes = [r.strip() for r in response.split("\n\n") if r.strip()]
    return recipes[:3]


def classify_product_category(product_name: str) -> str:
    """
    When product is not found in KB or OFF,
    ask LLM to classify it into a food category.
    """
    prompt = f"""
Classify this grocery item into one food category.
Item: {product_name}
Choose from: dairy, produce, grains, lentils, meat, seafood, snacks, beverages, condiments, frozen
Reply with only the single category word, nothing else.
"""
    response = ask_ollama(prompt)
    return response.lower().strip() if response else "unknown"