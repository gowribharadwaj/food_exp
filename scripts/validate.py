# validate.py
# Run this after build_dataset.py to check for errors.
# Zero errors = your dataset is ready.
# Run from inside pantry_dataset/:
#   python scripts/validate.py

import json
import sys

def validate(kb):
    errors = []
    seen_ids   = set()
    seen_names = set()

    for i, item in enumerate(kb):
        label = f"Entry {i} (name: '{item.get('name', 'MISSING')}')"

        # ── Check 1: All required fields exist ──
        required = ["id", "name", "aliases", "category",
                    "shelf_life", "high_risk", "source"]
        for field in required:
            if field not in item:
                errors.append(f"{label}: Missing field '{field}'")

        # ── Check 2: No duplicate IDs ──
        item_id = item.get("id", "")
        if item_id in seen_ids:
            errors.append(f"{label}: Duplicate id '{item_id}'")
        seen_ids.add(item_id)

        # ── Check 3: No duplicate names ──
        item_name = item.get("name", "")
        if item_name in seen_names:
            errors.append(f"{label}: Duplicate name '{item_name}'")
        seen_names.add(item_name)

        # ── Check 4: shelf_life values must be int or null ──
        sl = item.get("shelf_life", {})
        if not isinstance(sl, dict):
            errors.append(f"{label}: shelf_life must be an object/dict")
        else:
            for key in ["pantry_days", "fridge_days", "freezer_days"]:
                val = sl.get(key)
                if val is not None and not isinstance(val, int):
                    errors.append(
                        f"{label}: shelf_life.{key} = '{val}' "
                        f"(type: {type(val).__name__}) — must be int or null"
                    )

        # ── Check 5: At least one shelf_life value must be set ──
        if isinstance(sl, dict):
            if all(v is None for v in sl.values()):
                # Only flag as error for manual_indian entries
                # FoodKeeper entries with no data were already skipped at load time
                if item.get("source") == "manual_indian":
                    errors.append(
                        f"{label}: All shelf_life values are null — "
                        f"at least one must have a number"
                    )

        # ── Check 6: high_risk must be true or false ──
        if not isinstance(item.get("high_risk"), bool):
            errors.append(
                f"{label}: high_risk = '{item.get('high_risk')}' — "
                f"must be true or false (boolean)"
            )

        # ── Check 7: source must be one of the three allowed values ──
        valid_sources = ("foodkeeper", "open_food_facts", "manual_indian")
        if item.get("source") not in valid_sources:
            errors.append(
                f"{label}: source = '{item.get('source')}' — "
                f"must be one of: {valid_sources}"
            )

        # ── Check 8: aliases must be a list ──
        if not isinstance(item.get("aliases"), list):
            errors.append(f"{label}: aliases must be a list [ ]")

    # ── Check 9: Minimum total count ──
    total = len(kb)
    if total < 200:
        errors.append(
            f"TOTAL COUNT: {total} entries — minimum required is 200"
        )

    # ── Check 10: Minimum Indian staples count ──
    indian_count = len([x for x in kb if x.get("source") == "manual_indian"])
    if indian_count < 120:
        errors.append(
            f"INDIAN STAPLES COUNT: {indian_count} — minimum required is 120"
        )

    return errors, total, indian_count


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    path = "data/pantry_knowledge_base.json"

    print("\n========================================")
    print(" Validating pantry_knowledge_base.json")
    print("========================================\n")

    try:
        with open(path, "r", encoding="utf-8") as f:
            kb = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found → {path}")
        print("Run build_dataset.py first.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: File is not valid JSON → {e}")
        sys.exit(1)

    errors, total, indian_count = validate(kb)

    if errors:
        print(f"❌  {len(errors)} error(s) found:\n")
        for e in errors:
            print(f"  • {e}")
        print(f"\nFix all errors above, re-run build_dataset.py, then run this again.")
        sys.exit(1)
    else:
        print(f"✅  All checks passed!\n")
        print(f"  Total entries   : {total}")
        print(f"  Indian staples  : {indian_count}")
        hr = len([x for x in kb if x.get("high_risk")])
        print(f"  High-risk items : {hr}")
        print(f"\n  Dataset is ready to submit.")