# fetch_off.py
# Pulls Indian product → category mappings from Open Food Facts API.
# No API key needed. Free to use.
# Run from inside pantry_dataset/:
#   python scripts/fetch_off.py

import json
import time
import requests
import os

# ─────────────────────────────────────────────────────────────────
# The 50 Indian brand searches from the PDF
# ─────────────────────────────────────────────────────────────────

SEARCHES = [
    "amul milk",
    "amul butter",
    "amul paneer",
    "amul ghee",
    "amul cream",
    "amul cheese",
    "amul lassi",
    "britannia bread",
    "britannia cheese",
    "britannia biscuit",
    "parle g biscuit",
    "parle biscuits",
    "maggi noodles",
    "maggi masala",
    "maggi ketchup",
    "tata salt",
    "tata tea",
    "fortune oil",
    "mtr masala",
    "mtr ready to eat",
    "everest masala",
    "kissan jam",
    "kissan ketchup",
    "tropicana juice",
    "real juice",
    "dabur honey",
    "dabur juice",
    "haldiram namkeen",
    "haldiram bhujia",
    "lijjat papad",
    "mothers recipe pickle",
    "priya pickle",
    "nestle milkmaid",
    "nestle kit kat",
    "cadbury dairy milk",
    "cadbury bournvita",
    "horlicks",
    "complan",
    "saffola oil",
    "sundrop oil",
    "patanjali atta",
    "patanjali ghee",
    "aashirvaad atta",
    "pillsbury maida",
    "good day biscuit",
    "hide and seek biscuit",
    "yippee noodles",
    "top ramen",
    "bru coffee",
    "nescafe coffee"
]

# ─────────────────────────────────────────────────────────────────
# Fetch one search from Open Food Facts API
# ─────────────────────────────────────────────────────────────────

def fetch_off(search_term):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": search_term,
        "json": 1,
        "page_size": 5,      # only top 5 results per search
        "fields": "product_name,brands,categories_tags,categories"
    }
    headers = {
        "User-Agent": "PantryDatasetProject/1.0 (student project)"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  HTTP {response.status_code} for '{search_term}'")
            return None
    except requests.exceptions.Timeout:
        print(f"  TIMEOUT for '{search_term}' — skipping")
        return None
    except requests.exceptions.ConnectionError:
        print(f"  CONNECTION ERROR for '{search_term}' — skipping")
        return None

# ─────────────────────────────────────────────────────────────────
# Extract clean info from one product result
# ─────────────────────────────────────────────────────────────────

def extract_product(product, search_term):
    name = product.get("product_name", "").strip()
    brand = product.get("brands", "").strip()
    categories = product.get("categories", "").strip()

    # categories_tags looks like: ["en:milk", "en:dairy-products"]
    # We take the last tag as it's usually the most specific
    tags = product.get("categories_tags", [])
    specific_tag = ""
    if tags:
        # Filter to English tags and take the most specific one
        en_tags = [t for t in tags if t.startswith("en:")]
        if en_tags:
            specific_tag = en_tags[-1].replace("en:", "").replace("-", " ")

    # Only keep if we have at least a name and some category info
    if not name or (not categories and not specific_tag):
        return None

    return {
        "search_term": search_term,
        "product_name": name,
        "brand": brand,
        "off_category": categories.split(",")[0].strip() if categories else "",
        "specific_category": specific_tag,
    }

# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n========================================")
    print(" Fetching Open Food Facts product data")
    print("========================================\n")

    all_products = []
    failed = []

    for i, search_term in enumerate(SEARCHES):
        print(f"[{i+1}/{len(SEARCHES)}] Searching: '{search_term}'")

        data = fetch_off(search_term)

        if data and "products" in data:
            products = data["products"]
            count = 0
            for product in products:
                extracted = extract_product(product, search_term)
                if extracted:
                    all_products.append(extracted)
                    count += 1
            print(f"  → {count} products found")
        else:
            print(f"  → No results")
            failed.append(search_term)

        # Wait 1 second between requests — be polite to the API
        time.sleep(1)

    # Save results
    output_path = "data/off_indian_products.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)

    print("\n========================================")
    print(" DONE")
    print("========================================")
    print(f"  Total products fetched : {len(all_products)}")
    print(f"  Failed searches        : {len(failed)}")
    if failed:
        print(f"  Failed: {failed}")
    print(f"  Saved to               : {output_path}")
    print("\n  Next: run python scripts/build_dataset.py")
    print("  Then: run python scripts/validate.py")