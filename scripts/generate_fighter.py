from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DRAFTS_DIR = ROOT / "submissions" / "drafts"
APPROVED_DIR = ROOT / "submissions" / "approved"
GENERATED_DIR = ROOT / "generated" / "fighters"
GENERATED_META_DIR = ROOT / "generated" / "fighters_metadata"
AGGREGATE_META_FILE = ROOT / "fighters_metadata.json"


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


CONFIG = {
    "fighter_enums": load_json(CONFIG_DIR / "fighter_enums.json", {}),
    "fighter_asset_registry": load_json(CONFIG_DIR / "fighter_asset_registry.json", {}),
    "fighter_validation_rules": load_json(CONFIG_DIR / "fighter_validation_rules.json", {}),
}

DEFAULT_ARCHETYPE_TEMPLATE_MAP = {
    "balanced": "template_balanced_01",
    "rushdown": "template_rush_01",
    "grappler": "template_grapple_01",
    "striker": "template_strike_01",
    "zoner": "template_zone_01",
    "counter_grappler": "template_counter_01",
    "tank": "template_tank_01",
    "wildcard": "template_wild_01",
}

DEFAULT_ARCHETYPE_AI_PACKAGE = {
    "balanced": "balanced_v1",
    "rushdown": "rushdown_v1",
    "grappler": "grappler_v1",
    "striker": "striker_v1",
    "zoner": "zoner_v1",
    "counter_grappler": "counter_v1",
    "tank": "tank_v1",
    "wildcard": "wildcard_v1",
}

REQUIRED_STATS = ["power", "speed", "defense", "grapple", "strike", "air", "stamina", "recovery"]
REQUIRED_AI = [
    "aggression", "combo_rate", "grapple_rate", "strike_rate", "air_rate",
    "throw_escape_rate", "guard_rate", "counter_rate", "special_usage",
    "super_usage", "risk_tolerance", "ring_control", "finish_priority"
]


def slugify(value: str) -> str:
    value = (value or "").strip().lower().replace("-", "_").replace(" ", "_")
    return "".join(ch for ch in value if ch.isalnum() or ch == "_")


def palette_key_from_colors(appearance: Dict[str, Any]) -> str:
    return f'{appearance.get("primary_color","")}_{appearance.get("secondary_color","")}_{appearance.get("accent_color","")}'.strip("_").lower()


def get_template_for_archetype(archetype: str) -> str:
    archetype_key = slugify(archetype)
    asset_registry = CONFIG["fighter_asset_registry"].get("compatibility_rules", {})
    compat = asset_registry.get("archetype_to_template", {})
    if archetype_key in compat and compat[archetype_key]:
        return compat[archetype_key][0]
    return DEFAULT_ARCHETYPE_TEMPLATE_MAP.get(archetype_key, "template_balanced_01")


def get_ai_package_for_archetype(archetype: str) -> str:
    return DEFAULT_ARCHETYPE_AI_PACKAGE.get(slugify(archetype), "balanced_v1")


def validate_stats(stats: Dict[str, Any]) -> None:
    missing = [k for k in REQUIRED_STATS if k not in stats]
    if missing:
        raise ValueError(f'Missing stats: {", ".join(missing)}')

    rules = CONFIG["fighter_validation_rules"].get("stat_rules", {})
    fields = rules.get("point_budget_fields", REQUIRED_STATS)
    min_stat = int(rules.get("minimum_per_stat", 35))
    max_stat = int(rules.get("maximum_per_stat", 95))
    target_total = int(rules.get("point_budget_total", 500))

    total = 0
    for field in fields:
        value = int(stats[field])
        if value < min_stat or value > max_stat:
            raise ValueError(f"Stat out of range: {field}={value}")
        total += value

    if total != target_total:
        raise ValueError(f"Stat budget mismatch: expected {target_total}, got {total}")

    stats["point_budget_total"] = target_total
    stats["point_budget_used"] = total


def validate_ai(ai_profile: Dict[str, Any], archetype: str) -> None:
    if ai_profile.get("base_archetype") and slugify(ai_profile["base_archetype"]) != slugify(archetype):
        raise ValueError("ai_profile.base_archetype must match classification.archetype")

    missing = [k for k in REQUIRED_AI if k not in ai_profile]
    if missing:
        raise ValueError(f'Missing ai_profile fields: {", ".join(missing)}')

    for field in REQUIRED_AI:
        value = int(ai_profile[field])
        if value < 0 or value > 100:
            raise ValueError(f"AI field out of range: {field}={value}")


def validate_required_sections(fighter: Dict[str, Any]) -> None:
    for section in ["identity", "classification", "appearance", "stats", "ai_profile", "moveset"]:
        if section not in fighter or not isinstance(fighter[section], dict):
            raise ValueError(f"Missing required section: {section}")

    display_name = fighter["identity"].get("display_name", "").strip()
    if not display_name:
        raise ValueError("identity.display_name is required")

    fighter_id = fighter.get("fighter_id", "").strip()
    if not fighter_id:
        raise ValueError("fighter_id is required")


def derive_runtime_and_league(fighter: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    archetype = fighter["classification"]["archetype"]
    appearance = fighter["appearance"]
    stats = fighter["stats"]
    ai = fighter["ai_profile"]

    base_fighter = fighter.get("base_fighter") or {}

    if base_fighter and base_fighter.get("char_folder"):
        template_folder = base_fighter["char_folder"]
        template_source = "base_fighter"
    else:
        template_folder = fighter["moveset"].get("template_base") or get_template_for_archetype(archetype)
        template_source = "archetype_template"

    runtime_character_id = f'custom_{slugify(fighter["fighter_id"])}'

    palette_key = palette_key_from_colors(appearance)
    palette_id = CONFIG["fighter_asset_registry"].get("palette_map", {}).get(
        palette_key, "palette_black_white_red_01.act"
    )
    ai_package = get_ai_package_for_archetype(archetype)

    power_index = round(
        (
            stats["power"] * 1.15 +
            stats["speed"] * 0.95 +
            stats["defense"] * 1.00 +
            stats["grapple"] * 1.05 +
            stats["strike"] * 1.05 +
            stats["air"] * 0.75 +
            stats["stamina"] * 0.95 +
            stats["recovery"] * 0.85
        ) / 8,
        2,
    )

    life = int(800 + stats["stamina"] * 4 + stats["defense"] * 2)
    attack = int(60 + ((stats["power"] + stats["strike"] + stats["grapple"]) / 3) * 0.8)
    defence = int(60 + ((stats["defense"] + stats["recovery"]) / 2) * 0.6)

    derived_stats = {
        "life": life,
        "attack": attack,
        "defence": defence,
        "ai_profile": slugify(ai.get("base_archetype") or archetype),
        "preferred_ai_level": max(1, min(8, round(4 + (ai["aggression"] + ai["risk_tolerance"] + ai["finish_priority"]) / 75))),
    }

    runtime = {
        "template_folder": template_folder,
        "template_source": template_source,
        "base_fighter_id": base_fighter.get("id", ""),
        "base_fighter_name": base_fighter.get("display_name", ""),
        "base_fighter_char_folder": base_fighter.get("char_folder", ""),
        "base_fighter_def_file": base_fighter.get("def_file", ""),
        "base_fighter_def_path": base_fighter.get("def_path", ""),
        "runtime_character_id": runtime_character_id,
        "runtime_display_name": fighter["identity"]["display_name"],
        "palette_id": palette_id,
        "portrait_asset": fighter["appearance"].get("portrait_style", "portrait_serious_base.png"),
        "ai_package": ai_package,
        "generator_version": "base-fighter-enabled-1.1",
    }

    league_metadata = {
        "power_index": power_index,
        "archetype": slugify(archetype),
        "weight_class": fighter["classification"].get("weight_class", "middleweight"),
    }
    return runtime, derived_stats, league_metadata


def build_generated_payload(fighter: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_sections(fighter)
    validate_stats(fighter["stats"])
    validate_ai(fighter["ai_profile"], fighter["classification"]["archetype"])

    runtime, derived_stats, league_metadata = derive_runtime_and_league(fighter)

    return {
        "fighter_id": fighter["fighter_id"],
        "schema_version": fighter.get("schema_version", "1.0.0"),
        "status": "generated",
        "live": False,
        "base_fighter": fighter.get("base_fighter"),
        "identity": {
            "name": fighter["identity"]["display_name"],
            "display_name": fighter["identity"]["display_name"],
            "creator_name": fighter["identity"].get("creator_name", ""),
            "nickname": fighter["identity"].get("nickname", ""),
            "hometown": fighter["identity"].get("hometown", ""),
        },
        "classification": fighter["classification"],
        "appearance": fighter["appearance"],
        "stats": fighter["stats"],
        "ai_profile": fighter["ai_profile"],
        "moveset": fighter["moveset"],
        "league_settings": fighter.get("league_settings", {}),
        "runtime": runtime,
        "derived_stats": derived_stats,
        "league_metadata": league_metadata,
    }


def load_source_fighter(fighter_id: str) -> Tuple[Path, Dict[str, Any]]:
    for path in [APPROVED_DIR / f"{fighter_id}.json", DRAFTS_DIR / f"{fighter_id}.json"]:
        if path.exists():
            return path, load_json(path, {})
    raise FileNotFoundError(f"Could not find fighter JSON for {fighter_id}")


def generate_one(fighter_id: str) -> Dict[str, Any]:
    _, fighter = load_source_fighter(fighter_id)
    generated = build_generated_payload(fighter)
    fid = generated["fighter_id"]

    generated_meta = {
        "fighter_id": fid,
        "name": generated["identity"]["name"],
        "author": generated["identity"]["creator_name"],
        "power_index": generated["league_metadata"]["power_index"],
        "archetype": generated["league_metadata"]["archetype"],
    }

    save_json(GENERATED_DIR / f"{fid}.json", generated)
    save_json(GENERATED_META_DIR / f"{fid}.json", generated_meta)
    return generated_meta


def rebuild_aggregate_metadata() -> None:
    fighters: Dict[str, Any] = {}
    GENERATED_META_DIR.mkdir(parents=True, exist_ok=True)

    for path in GENERATED_META_DIR.glob("*.json"):
        data = load_json(path, {})
        if not data:
            continue
        fighters[data["name"]] = {
            "author": data.get("author", ""),
            "power_index": data.get("power_index", 0),
            "archetype": data.get("archetype", "balanced"),
        }

    save_json(AGGREGATE_META_FILE, {"fighters": fighters})


def iter_ids_without_arg() -> Iterable[str]:
    ids: List[str] = []
    for path in APPROVED_DIR.glob("*.json"):
        ids.append(path.stem)
    return sorted(set(ids))


def main() -> None:
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_META_DIR.mkdir(parents=True, exist_ok=True)

    ids = [sys.argv[1]] if len(sys.argv) > 1 else list(iter_ids_without_arg())
    if not ids:
        print("No fighters found to generate.")
        return

    processed = 0
    for fighter_id in ids:
        meta = generate_one(fighter_id)
        processed += 1
        print(f"[GENERATED] {meta['fighter_id']} ({meta['name']})")

    rebuild_aggregate_metadata()
    print(f"Generated {processed} fighter(s).")


if __name__ == "__main__":
    main()