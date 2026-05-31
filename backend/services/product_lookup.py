import requests
from services.shelf_life import find_item, get_shelf_life

OFF_API = "https://world.openfoodfacts.org/cgi/search.pl"


def lookup_product(name: str, storage_type: str = "fridge") -> dict:
    """
    Decision tree:
    1. Check knowledge base (indian staples + foodkeeper)
    2. If not found, hit Open Food Facts API
    3. If still not found, return None and let LLM handle it
    """

    # Step 1: Local knowledge base
    result = get_shelf_life(name, storage_type)
    if result["days"] is not None:
        return {
            "name": name,
            "category": result["category"],
            "shelf_life_days": result["days"],
            "high_risk": result["high_risk"],
            "source": result["source"]
        }

    # Step 2: Open Food Facts
    try:
        response = requests.get(OFF_API, params={
            "search_terms": name,
            "json": 1,
            "page_size": 1,
            "fields": "product_name,categories_tags"
        }, timeout=5)

        if response.status_code == 200:
            products = response.json().get("products", [])
            if products:
                tags = products[0].get("categories_tags", [])
                en_tags = [t.replace("en:", "").replace("-", " ")
                           for t in tags if t.startswith("en:")]
                if en_tags:
                    # Try to find a match in KB using the OFF category
                    category_guess = en_tags[-1]
                    fallback = get_shelf_life(category_guess, storage_type)
                    if fallback["days"]:
                        return {
                            "name": name,
                            "category": category_guess,
                            "shelf_life_days": fallback["days"],
                            "high_risk": fallback["high_risk"],
                            "source": "open_food_facts"
                        }
    except Exception:
        pass  # Network issue — skip to fallback

    # Step 3: Not found anywhere
    return {
        "name": name,
        "category": "unknown",
        "shelf_life_days": None,
        "high_risk": False,
        "source": "not_found"
    }