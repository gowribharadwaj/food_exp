# build_dataset.py
# Produces pantry_knowledge_base.json from three sources.
# Run from inside the pantry_dataset/ folder:
#   python scripts/build_dataset.py

import json
import re
import os
import xlrd

# ─────────────────────────────────────────────────────────────────
# HELPER: Convert a number + metric unit into integer days
# ─────────────────────────────────────────────────────────────────

def to_days(number, metric):
    """
    number : a float like 3.0
    metric : a string like "Months", "Weeks", "Days", etc.
    Returns: integer days, or None if not applicable
    """
    if not number or not metric:
        return None

    metric = str(metric).strip().lower()
    number = float(number)

    if metric in ("not recommended", "package use-by date",
                  "when ripe", "", "nan"):
        return None
    if metric in ("indefinitely", "indefinite"):
        return 1095          # 3 years as a safe cap
    if metric == "hours":
        return max(1, int(number / 24))   # convert hours → days
    if metric == "days":
        return int(number)
    if metric == "weeks":
        return int(number * 7)
    if metric in ("month", "months"):
        return int(number * 30)
    if metric in ("year", "years"):
        return int(number * 365)

    return None              # unknown unit → treat as missing


# ─────────────────────────────────────────────────────────────────
# SOURCE 1: Load FoodKeeper .xls → list of entry dicts
# ─────────────────────────────────────────────────────────────────

def load_foodkeeper(path):
    """
    Reads the FoodKeeper XLS file.
    Uses the 'Product' sheet (661 rows) and 'Category' sheet for names.
    Each product row becomes one JSON entry.
    """
    print(f"  Reading: {path}")
    wb = xlrd.open_workbook(path)

    # ── Step A: Build a category ID → name lookup from Category sheet ──
    cat_sheet = wb.sheet_by_name('Category')
    category_map = {}   # e.g. {7.0: "Dairy Products & Eggs"}
    for r in range(1, cat_sheet.nrows):
        cat_id   = cat_sheet.cell_value(r, 0)   # column 0 = ID
        cat_name = str(cat_sheet.cell_value(r, 1)).strip()  # column 1 = Category_Name
        sub_name = str(cat_sheet.cell_value(r, 2)).strip()  # column 2 = Subcategory_Name
        if sub_name and sub_name != 'nan' and sub_name != '':
            category_map[cat_id] = f"{cat_name} - {sub_name}"
        else:
            category_map[cat_id] = cat_name

    # ── Step B: Read the Product sheet ──
    prod_sheet = wb.sheet_by_name('Product')

    # These category IDs are high-risk (food poisoning risk)
    # 7=Dairy, 10-13=Meat, 14-17=Poultry, 20-22=Seafood, 25=Deli
    high_risk_cat_ids = {7.0, 10.0, 11.0, 12.0, 13.0,
                         14.0, 15.0, 16.0, 17.0,
                         20.0, 21.0, 22.0, 25.0}

    all_entries = []

    for r in range(1, prod_sheet.nrows):

        # Column index reference (from the headers we found):
        # [0]=ID [1]=Category_ID [2]=Name [3]=Name_subtitle [4]=Keywords
        # [5]=Pantry_Min [6]=Pantry_Max [7]=Pantry_Metric
        # [16]=Refrigerate_Min [17]=Refrigerate_Max [18]=Refrigerate_Metric
        # [30]=Freeze_Min [31]=Freeze_Max [32]=Freeze_Metric

        name = str(prod_sheet.cell_value(r, 2)).strip()
        if not name or name == 'nan':
            continue

        subtitle = str(prod_sheet.cell_value(r, 3)).strip()
        if subtitle and subtitle != 'nan':
            full_name = f"{name.lower()} ({subtitle.lower()})"
        else:
            full_name = name.lower()

        cat_id    = prod_sheet.cell_value(r, 1)
        cat_name  = category_map.get(cat_id, "unknown")
        # Make a clean category code: lowercase, spaces→underscores
        cat_code  = re.sub(r'[^a-z0-9]', '_',
                           cat_name.lower().replace(' ', '_'))
        cat_code  = re.sub(r'_+', '_', cat_code).strip('_')

        # Keywords column → aliases list
        keywords_raw = str(prod_sheet.cell_value(r, 4)).strip()
        if keywords_raw and keywords_raw != 'nan':
            aliases = [k.strip().lower()
                       for k in keywords_raw.split(',')
                       if k.strip()]
        else:
            aliases = []
        # PANTRY — try all pantry columns in order, use first non-None
        pantry = (
            to_days(prod_sheet.cell_value(r, 5),  prod_sheet.cell_value(r, 7))   # Pantry_Min
            or to_days(prod_sheet.cell_value(r, 9),  prod_sheet.cell_value(r, 11))  # DOP_Pantry_Min
            or to_days(prod_sheet.cell_value(r, 13), prod_sheet.cell_value(r, 15))  # Pantry_After_Opening_Min
        )

        # FRIDGE — try all fridge columns in order
        fridge = (
            to_days(prod_sheet.cell_value(r, 16), prod_sheet.cell_value(r, 18))  # Refrigerate_Min
            or to_days(prod_sheet.cell_value(r, 20), prod_sheet.cell_value(r, 22))  # DOP_Refrigerate_Min
            or to_days(prod_sheet.cell_value(r, 24), prod_sheet.cell_value(r, 26))  # Refrigerate_After_Opening_Min
            or to_days(prod_sheet.cell_value(r, 27), prod_sheet.cell_value(r, 29))  # Refrigerate_After_Thawing_Min
        )

        # FREEZER — try all freezer columns in order
        freezer = (
            to_days(prod_sheet.cell_value(r, 30), prod_sheet.cell_value(r, 32))  # Freeze_Min
            or to_days(prod_sheet.cell_value(r, 34), prod_sheet.cell_value(r, 36))  # DOP_Freeze_Min
        )

        # SKIP this entry entirely if ALL three storage values are still None
        # (means FoodKeeper genuinely has no data for this item)
        if pantry is None and fridge is None and freezer is None:
            continue

        is_high_risk = cat_id in high_risk_cat_ids

        entry_id = f"fk_{int(prod_sheet.cell_value(r, 0)):03d}"

        entry = {
            "id":    entry_id,
            "name":  full_name,
            "aliases": aliases,
            "category": cat_code,
            "shelf_life": {
                "pantry_days":  pantry,
                "fridge_days":  fridge,
                "freezer_days": freezer
            },
            "high_risk": is_high_risk,
            "source": "foodkeeper"
        }

        all_entries.append(entry)

    print(f"  → {len(all_entries)} FoodKeeper entries loaded")
    return all_entries


# ─────────────────────────────────────────────────────────────────
# SOURCE 2: Load Indian staples JSON
# ─────────────────────────────────────────────────────────────────

def load_indian_staples(path):
    print(f"  Reading: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Safety check: shelf_life values must be int or None, never strings
    for item in data:
        sl = item.get("shelf_life", {})
        for key in ["pantry_days", "fridge_days", "freezer_days"]:
            val = sl.get(key)
            if val is not None and not isinstance(val, int):
                raise ValueError(
                    f"BAD DATA: '{item['name']}' → "
                    f"shelf_life.{key} = '{val}' must be an integer"
                )

    print(f"  → {len(data)} Indian staple entries loaded")
    return data


# ─────────────────────────────────────────────────────────────────
# SOURCE 3: Load category mapping JSON
# ─────────────────────────────────────────────────────────────────

def load_category_mapping(path):
    print(f"  Reading: {path}")
    with open(path, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    print(f"  → Category mapping loaded")
    return mapping


# ─────────────────────────────────────────────────────────────────
# MERGE: Combine all three sources
# ─────────────────────────────────────────────────────────────────

def merge_all(foodkeeper_entries, indian_entries, mapping):
    """
    Rules:
    1. FoodKeeper is the base (~661 entries).
    2. Indian staples override FoodKeeper on name matches.
    3. Deduplicate by name.
    4. Re-assign clean IDs.
    """
    # Start with FoodKeeper as base
    merged = {}
    for entry in foodkeeper_entries:
        merged[entry["name"]] = entry

    # Indian staples override
    for item in indian_entries:
        name = item["name"]
        # Also check aliases — if an alias matches a FoodKeeper name, replace it
        for alias in item.get("aliases", []):
            if alias in merged:
                del merged[alias]
        merged[name] = item  # Indian entry always wins

    result = list(merged.values())

    # Re-assign sequential IDs grouped by category
    cat_counters = {}
    for entry in result:
        cat = entry.get("category", "unknown")
        prefix = re.sub(r'[^a-z0-9]', '', cat[:8])
        cat_counters[prefix] = cat_counters.get(prefix, 0) + 1
        entry["id"] = f"{prefix}_{cat_counters[prefix]:03d}"

    return result


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n========================================")
    print(" Building pantry_knowledge_base.json")
    print("========================================\n")

    foodkeeper_path = "data/foodkeeper_raw.xls"   # NOTE: .xls not .xlsx
    indian_path     = "data/indian_staples.json"
    mapping_path    = "data/category_mapping.json"
    output_path     = "data/pantry_knowledge_base.json"

    # Check all files exist
    for path in [foodkeeper_path, indian_path, mapping_path]:
        if not os.path.exists(path):
            print(f"ERROR: File not found → {path}")
            print("Make sure you are running this from inside pantry_dataset/")
            exit(1)

    print("Step 1: Loading FoodKeeper XLS...")
    fk = load_foodkeeper(foodkeeper_path)

    print("\nStep 2: Loading Indian staples...")
    indian = load_indian_staples(indian_path)

    print("\nStep 3: Loading category mapping...")
    mapping = load_category_mapping(mapping_path)

    print("\nStep 4: Merging all sources...")
    final = merge_all(fk, indian, mapping)
    print(f"  → {len(final)} total entries after merge")

    print(f"\nStep 5: Saving to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    high_risk = len([x for x in final if x["high_risk"]])
    indian_ct = len([x for x in final if x["source"] == "manual_indian"])

    print("\n========================================")
    print(" DONE")
    print("========================================")
    print(f"  Total entries   : {len(final)}")
    print(f"  Indian staples  : {indian_ct}")
    print(f"  High-risk items : {high_risk}")
    print(f"  Output saved to : {output_path}")