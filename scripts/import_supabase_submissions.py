from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

import requests

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env.local"
CONFIG_DIR = ROOT / "config"

DRAFTS_DIR = ROOT / "submissions" / "drafts"
APPROVED_DIR = ROOT / "submissions" / "approved"
REJECTED_DIR = ROOT / "submissions" / "rejected"

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


def load_config() -> Dict[str, Any]:
    return {
        "fighter_enums": load_json(CONFIG_DIR / "fighter_enums.json"),
        "fighter_validation_rules": load_json(CONFIG_DIR / "fighter_validation_rules.json"),
    }


def validate_required_sections(fighter: Dict[str, Any], errors: List[str]) -> None:
    required = ["identity", "classification", "appearance", "stats", "ai_profile", "moveset"]
    for section in required:
        if section not in fighter or not isinstance(fighter[section], dict):
            errors.append(f"Missing required section: {section}")


def validate_enums(fighter: Dict[str, Any], enums: Dict[str, Any], errors: List[str]) -> None:
    checks = [
        ("classification.archetype", fighter.get("classification", {}).get("archetype"), enums.get("classification", {}).get("archetype", [])),
        ("classification.weight_class", fighter.get("classification", {}).get("weight_class"), enums.get("classification", {}).get("weight_class", [])),
        ("classification.stance", fighter.get("classification", {}).get("stance"), enums.get("classification", {}).get("stance", [])),
        ("ai_profile.preferred_range", fighter.get("ai_profile", {}).get("preferred_range"), enums.get("ai_profile", {}).get("preferred_range", [])),
        ("moveset.template_base", fighter.get("moveset", {}).get("template_base"), enums.get("moveset", {}).get("template_base", [])),
        ("moveset.moveset_style", fighter.get("moveset", {}).get("moveset_style"), enums.get("moveset", {}).get("moveset_style", [])),
    ]
    for name, value, allowed in checks:
        if allowed and value not in allowed:
            errors.append(f"Invalid enum value for {name}: {value}")


def validate_stats(fighter: Dict[str, Any], rules: Dict[str, Any], errors: List[str]) -> None:
    stats = fighter.get("stats", {})
    fields = rules.get("stat_rules", {}).get("point_budget_fields", [])
    min_stat = int(rules.get("stat_rules", {}).get("minimum_per_stat", 35))
    max_stat = int(rules.get("stat_rules", {}).get("maximum_per_stat", 95))
    target_total = int(rules.get("stat_rules", {}).get("point_budget_total", 500))

    missing = [field for field in fields if field not in stats]
    if missing:
        errors.append(f"Missing stats: {', '.join(missing)}")
        return

    total = 0
    for field in fields:
        try:
            value = int(stats[field])
        except Exception:
            errors.append(f"Stat must be numeric: {field}")
            continue
        if value < min_stat or value > max_stat:
            errors.append(f"Stat out of range: {field}={value}")
        total += value

    if total != target_total:
        errors.append(f"Stat budget mismatch: expected {target_total}, got {total}")


def validate_ai(fighter: Dict[str, Any], errors: List[str]) -> None:
    ai = fighter.get("ai_profile", {})
    numeric_fields = [
        "aggression", "combo_rate", "grapple_rate", "strike_rate", "air_rate",
        "throw_escape_rate", "guard_rate", "counter_rate", "special_usage",
        "super_usage", "risk_tolerance", "ring_control", "finish_priority",
    ]
    for field in numeric_fields:
        if field not in ai:
            errors.append(f"Missing ai_profile.{field}")
            continue
        try:
            value = int(ai[field])
        except Exception:
            errors.append(f"AI value must be numeric: {field}")
            continue
        if value < 0 or value > 100:
            errors.append(f"AI value out of range: {field}={value}")

    if fighter.get("classification", {}).get("archetype") != ai.get("base_archetype"):
        errors.append("classification.archetype must match ai_profile.base_archetype")


def validate_submission(fighter: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not fighter.get("fighter_id"):
        errors.append("fighter_id missing")
    if not fighter.get("identity", {}).get("display_name"):
        errors.append("identity.display_name missing")

    validate_required_sections(fighter, errors)
    validate_enums(fighter, config["fighter_enums"], errors)
    validate_stats(fighter, config["fighter_validation_rules"], errors)
    validate_ai(fighter, errors)

    moveset = fighter.get("moveset", {})
    sigs = [moveset.get("signature_1"), moveset.get("signature_2"), moveset.get("signature_3")]
    compact = [s for s in sigs if s]
    if len(compact) != len(set(compact)):
        errors.append("Signature moves must be unique")

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
    config = load_config()
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

        errors = validate_submission(fighter, config)
        if errors:
            print(f"Rejected {fighter_id}")
            for err in errors:
                print(f" - {err}")
            write_rejected_copy(fighter_id, fighter, errors)
            patch_row(
                env["url"],
                env["key"],
                row_id,
                {"status": "rejected", "rejection_reason": "; ".join(errors)[:500]},
            )
            continue

        save_json(approved_path, fighter)
        print(f"Approved: {fighter_id}")

        try:
            auto_pipeline(fighter_id)
        except Exception as e:
            print(f"Pipeline failed for {fighter_id}: {e}")
            patch_row(
                env["url"],
                env["key"],
                row_id,
                {"status": "approved", "rejection_reason": f"Pipeline failed after approval: {e}"[:500]},
            )
            continue

        patch_row(env["url"], env["key"], row_id, {"status": "synced", "rejection_reason": None})

    print("\nImport + Validation + Auto-Publish complete")


if __name__ == "__main__":
    main()