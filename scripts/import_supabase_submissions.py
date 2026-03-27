import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env.local"
CONFIG_DIR = ROOT / "config"

DRAFTS_DIR = ROOT / "submissions" / "drafts"
APPROVED_DIR = ROOT / "submissions" / "approved"
REJECTED_DIR = ROOT / "submissions" / "rejected"
GENERATED_DIR = ROOT / "generated"

GENERATE_SCRIPT = ROOT / "scripts" / "generate_fighter.py"
PUBLISH_SCRIPT = ROOT / "scripts" / "publish_fighter.py"

TABLE_NAME = "fighter_submissions"


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_env() -> Dict[str, str]:
    if not ENV_PATH.exists():
        raise RuntimeError(f"Missing {ENV_PATH.name}")

    env: Dict[str, str] = {}
    with open(ENV_PATH, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

    url = env.get("SUPABASE_URL")
    key = env.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url:
        raise RuntimeError("Missing SUPABASE_URL")
    if not key:
        raise RuntimeError("Missing SUPABASE_SERVICE_ROLE_KEY")
    return {"url": url, "key": key}


def headers(key: str) -> Dict[str, str]:
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def fetch(url: str, key: str) -> List[Dict[str, Any]]:
    r = requests.get(
        f"{url}/rest/v1/{TABLE_NAME}",
        headers=headers(key),
        params={
            "select": "*",
            "status": "eq.submitted",
            "order": "created_at.asc",
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def patch_row(url: str, key: str, row_id: Any, payload: Dict[str, Any]) -> None:
    r = requests.patch(
        f"{url}/rest/v1/{TABLE_NAME}",
        headers=headers(key),
        params={"id": f"eq.{row_id}"},
        json=payload,
        timeout=30,
    )
    r.raise_for_status()


def load_config() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    schema = load_json(CONFIG_DIR / "fighter_schema.json")
    enums = load_json(CONFIG_DIR / "fighter_enums.json")
    rules = load_json(CONFIG_DIR / "fighter_validation_rules.json")
    return schema, enums, rules


def get_nested(data: Dict[str, Any], dotted_key: str, default=None):
    cur: Any = data
    for part in dotted_key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def validate_required_sections(fighter: Dict[str, Any], schema: Dict[str, Any], errors: List[str]) -> None:
    for key in schema.get("required", []):
        if key not in fighter:
            errors.append(f"Missing required top-level field: {key}")


def validate_identity(fighter: Dict[str, Any], rules: Dict[str, Any], errors: List[str]) -> None:
    identity = fighter.get("identity", {})
    fighter_id = fighter.get("fighter_id", "")
    display_name = identity.get("display_name", "")
    nickname = identity.get("nickname", "")
    bio_short = identity.get("bio_short", "")

    import re
    pattern = rules["identity_rules"]["fighter_id"]["pattern"]
    if not re.match(pattern, fighter_id or ""):
        errors.append("fighter_id must be 3-32 chars, lowercase letters/numbers/underscores only")

    if not display_name or len(display_name) > rules["identity_rules"]["display_name"]["max_length"]:
        errors.append("identity.display_name is required and must be 1-24 chars")

    if nickname and len(nickname) > rules["identity_rules"]["nickname"]["max_length"]:
        errors.append("identity.nickname exceeds max length")

    if bio_short and len(bio_short) > rules["identity_rules"]["bio_short"]["max_length"]:
        errors.append("identity.bio_short exceeds max length")


def validate_enum_block(block_name: str, fighter: Dict[str, Any], enums: Dict[str, Any], errors: List[str]) -> None:
    block = fighter.get(block_name, {})
    allowed_block = enums.get(block_name, {})
    for field, allowed_values in allowed_block.items():
        if field in block and block[field] not in allowed_values:
            errors.append(f"{block_name}.{field} has invalid value: {block[field]}")


def validate_color_fields(fighter: Dict[str, Any], enums: Dict[str, Any], errors: List[str]) -> None:
    appearance = fighter.get("appearance", {})
    color_enums = enums.get("colors", {})
    for field in ["primary_color", "secondary_color", "accent_color"]:
        value = appearance.get(field)
        if value is not None and value not in color_enums.get(field, []):
            errors.append(f"appearance.{field} has invalid value: {value}")


def validate_stats(fighter: Dict[str, Any], rules: Dict[str, Any], errors: List[str]) -> None:
    stats = fighter.get("stats", {})
    stat_rules = rules["stat_rules"]
    fields = stat_rules["point_budget_fields"]
    min_stat = stat_rules["minimum_per_stat"]
    max_stat = stat_rules["maximum_per_stat"]

    missing = [s for s in fields if s not in stats]
    if missing:
        errors.append(f"Missing stat fields: {', '.join(missing)}")
        return

    total = 0
    above_85 = 0
    below_40 = 0
    for stat in fields:
        value = stats.get(stat)
        if not isinstance(value, int):
            errors.append(f"stats.{stat} must be an integer")
            continue
        total += value
        if value < min_stat or value > max_stat:
            errors.append(f"stats.{stat} must be between {min_stat} and {max_stat}")
        if value > 85:
            above_85 += 1
        if value < 40:
            below_40 += 1

    expected_total = stat_rules["point_budget_total"]
    if total != expected_total:
        errors.append(f"Stat budget mismatch: expected {expected_total}, got {total}")

    if above_85 > stat_rules["max_stats_above_85"]:
        errors.append("Too many stats above 85")
    if below_40 > stat_rules["max_stats_below_40"]:
        errors.append("Too many stats below 40")


def validate_ai(fighter: Dict[str, Any], enums: Dict[str, Any], rules: Dict[str, Any], errors: List[str]) -> None:
    ai = fighter.get("ai_profile", {})
    ai_rules = rules["ai_rules"]
    if ai.get("profile_mode") not in enums.get("ai_profile", {}).get("profile_mode", []):
        errors.append("ai_profile.profile_mode is invalid")
    if ai.get("preferred_range") not in enums.get("ai_profile", {}).get("preferred_range", []):
        errors.append("ai_profile.preferred_range is invalid")

    for field in ai_rules["advanced_mode_allowed_fields"]:
        if field == "preferred_range":
            continue
        value = ai.get(field)
        if not isinstance(value, int):
            errors.append(f"ai_profile.{field} must be an integer")
            continue
        if value < ai_rules["all_slider_min"] or value > ai_rules["all_slider_max"]:
            errors.append(f"ai_profile.{field} must be between 0 and 100")


def validate_moveset(fighter: Dict[str, Any], enums: Dict[str, Any], errors: List[str]) -> None:
    moveset = fighter.get("moveset", {})
    template_base = moveset.get("template_base")
    moveset_style = moveset.get("moveset_style")

    if template_base not in enums.get("moveset", {}).get("template_base", []):
        errors.append("moveset.template_base is invalid")
    if moveset_style not in enums.get("moveset", {}).get("moveset_style", []):
        errors.append("moveset.moveset_style is invalid")

    signatures = [
        moveset.get("signature_1"),
        moveset.get("signature_2"),
        moveset.get("signature_3"),
    ]
    filtered = [s for s in signatures if s]
    if len(filtered) != len(set(filtered)):
        errors.append("Signature moves must be unique")


def validate_submission(fighter: Dict[str, Any], schema: Dict[str, Any], enums: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    validate_required_sections(fighter, schema, errors)
    validate_identity(fighter, rules, errors)
    validate_enum_block("classification", fighter, enums, errors)
    validate_enum_block("appearance", fighter, enums, errors)
    validate_color_fields(fighter, enums, errors)
    validate_stats(fighter, rules, errors)
    validate_ai(fighter, enums, rules, errors)
    validate_moveset(fighter, enums, errors)

    # Cross-check archetype alignment.
    classification = fighter.get("classification", {})
    ai_profile = fighter.get("ai_profile", {})
    if classification.get("archetype") and ai_profile.get("base_archetype"):
        if classification["archetype"] != ai_profile["base_archetype"]:
            errors.append("classification.archetype must match ai_profile.base_archetype")

    return errors


def auto_pipeline(fighter_id: str) -> None:
    print(f"⚙️ Running pipeline for {fighter_id}")
    subprocess.run(["py", str(GENERATE_SCRIPT), fighter_id], check=True)
    subprocess.run(["py", str(PUBLISH_SCRIPT), fighter_id], check=True)
    print(f"✅ Published {fighter_id}")


def write_rejected_copy(fighter_id: str, fighter: Dict[str, Any], errors: List[str]) -> None:
    payload = {
        "fighter": fighter,
        "validation_errors": errors,
    }
    save_json(REJECTED_DIR / f"{fighter_id}.json", payload)


def main() -> None:
    schema, enums, rules = load_config()
    env = load_env()
    rows = fetch(env["url"], env["key"])

    if not rows:
        print("No new submissions.")
        return

    for row in rows:
        fighter = row.get("fighter_data")
        row_id = row.get("id")

        if not fighter or "fighter_id" not in fighter:
            print(f"Skipping malformed row: {row_id}")
            continue

        fighter_id = fighter["fighter_id"]
        draft_path = DRAFTS_DIR / f"{fighter_id}.json"
        approved_path = APPROVED_DIR / f"{fighter_id}.json"

        save_json(draft_path, fighter)

        if approved_path.exists():
            print(f"Already processed: {fighter_id}")
            patch_row(env["url"], env["key"], row_id, {"status": "synced"})
            continue

        errors = validate_submission(fighter, schema, enums, rules)
        if errors:
            print(f"❌ Rejected {fighter_id}")
            for err in errors:
                print(f"   - {err}")
            write_rejected_copy(fighter_id, fighter, errors)
            patch_row(
                env["url"],
                env["key"],
                row_id,
                {
                    "status": "rejected",
                    "rejection_reason": "; ".join(errors)[:500],
                },
            )
            continue

        save_json(approved_path, fighter)
        print(f"✅ Approved: {fighter_id}")

        try:
            auto_pipeline(fighter_id)
        except Exception as e:
            print(f"❌ Pipeline failed for {fighter_id}: {e}")
            patch_row(
                env["url"],
                env["key"],
                row_id,
                {
                    "status": "approved",
                    "rejection_reason": f"Pipeline failed after approval: {e}"[:500],
                },
            )
            continue

        patch_row(env["url"], env["key"], row_id, {"status": "synced", "rejection_reason": None})

    print("\n🚀 Import + Validation + Auto-Publish complete")


if __name__ == "__main__":
    main()
