from pathlib import Path
import json
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DRAFTS_DIR = ROOT / "submissions" / "drafts"
APPROVED_DIR = ROOT / "submissions" / "approved"
GENERATED_DIR = ROOT / "generated" / "fighters"
GENERATED_META_DIR = ROOT / "generated" / "fighters_metadata"
AGGREGATE_META_FILE = ROOT / "fighters_metadata.json"


DEFAULT_ARCHETYPE_TEMPLATE_MAP = {
    "Rushdown": "template_rush_01",
    "Grappler": "template_grapple_01",
    "Zoner": "template_zone_01",
    "Balanced": "template_balanced_01",
    "Summoner": "template_wild_01",
    "Striker": "template_strike_01",
    "Tank": "template_tank_01",
    "Wildcard": "template_wild_01",
    "Counter Grappler": "template_counter_01",
    "counter_grappler": "template_counter_01",
    "rushdown": "template_rush_01",
    "grappler": "template_grapple_01",
    "zoner": "template_zone_01",
    "balanced": "template_balanced_01",
    "summoner": "template_wild_01",
    "striker": "template_strike_01",
    "tank": "template_tank_01",
    "wildcard": "template_wild_01",
}


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


CONFIG = {
    "fighter_schema": load_json(CONFIG_DIR / "fighter_schema.json", {}),
    "fighter_enums": load_json(CONFIG_DIR / "fighter_enums.json", {}),
    "fighter_asset_registry": load_json(CONFIG_DIR / "fighter_asset_registry.json", {}),
    "fighter_validation_rules": load_json(CONFIG_DIR / "fighter_validation_rules.json", {}),
}


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def normalize_key(value: str) -> str:
    return (value or "").strip().replace("-", "_").replace(" ", "_")


def get_nested(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def stat_fields() -> List[str]:
    rules = CONFIG["fighter_validation_rules"].get("stat_rules", {})
    fields = rules.get("point_budget_fields") or [
        "power",
        "speed",
        "defense",
        "grapple",
        "strike",
        "air",
        "stamina",
        "recovery",
    ]
    return fields


def validate_stats(stats: Dict[str, int]) -> None:
    rules = CONFIG["fighter_validation_rules"].get("stat_rules", {})
    fields = stat_fields()
    minimum = int(rules.get("minimum_per_stat", 35))
    maximum = int(rules.get("maximum_per_stat", 95))
    max_above_85 = int(rules.get("max_stats_above_85", 2))
    max_below_40 = int(rules.get("max_stats_below_40", 1))
    expected_budget = int(rules.get("point_budget_total", 500))
    exact_budget = bool(rules.get("exact_budget_match_required", True))

    missing = [field for field in fields if field not in stats]
    if missing:
        raise ValueError(f"Missing stats: {', '.join(missing)}")

    total = 0
    above_85 = 0
    below_40 = 0
    for field in fields:
        value = int(stats[field])
        if value < minimum or value > maximum:
            raise ValueError(f"{field} out of bounds: {value} (expected {minimum}-{maximum})")
        total += value
        if value > 85:
            above_85 += 1
        if value < 40:
            below_40 += 1

    if exact_budget and total != expected_budget:
        raise ValueError(f"Stat budget mismatch: {total} (expected {expected_budget})")
    if above_85 > max_above_85:
        raise ValueError(f"Too many stats above 85: {above_85} (max {max_above_85})")
    if below_40 > max_below_40:
        raise ValueError(f"Too many stats below 40: {below_40} (max {max_below_40})")


def resolve_template(archetype: str, template_base: str | None = None) -> str:
    registry = CONFIG["fighter_asset_registry"].get("compatibility_rules", {})
    template_map = registry.get("archetype_to_template", {})

    archetype_norm = normalize_key(archetype)
    allowed = (
        template_map.get(archetype)
        or template_map.get(archetype_norm)
        or DEFAULT_ARCHETYPE_TEMPLATE_MAP.get(archetype)
        or DEFAULT_ARCHETYPE_TEMPLATE_MAP.get(archetype_norm)
    )

    if isinstance(allowed, str):
        allowed_list = [allowed]
    else:
        allowed_list = list(allowed or [])

    if template_base:
        if allowed_list and template_base not in allowed_list:
            raise ValueError(f"Template {template_base} is not allowed for archetype {archetype}")
        return template_base

    if allowed_list:
        return allowed_list[0]

    return "template_balanced_01"


def compute_power_index(stats: Dict[str, int]) -> float:
    weighted = (
        stats["power"] * 0.20
        + stats["speed"] * 0.12
        + stats["defense"] * 0.16
        + stats["grapple"] * 0.14
        + stats["strike"] * 0.14
        + stats["air"] * 0.06
        + stats["stamina"] * 0.10
        + stats["recovery"] * 0.08
    )
    return round(weighted, 1)


def derive_engine_stats(stats: Dict[str, int], ai_profile: Dict[str, Any]) -> Dict[str, Any]:
    power = int(stats["power"])
    speed = int(stats["speed"])
    defense = int(stats["defense"])
    stamina = int(stats["stamina"])
    recovery = int(stats["recovery"])
    aggression = int(ai_profile.get("aggression", 50))
    counter_rate = int(ai_profile.get("counter_rate", 50))

    life = int(900 + ((stamina - 50) * 7) + ((defense - 50) * 3))
    attack = int(85 + ((power - 50) * 0.75))
    defence = int(85 + ((defense - 50) * 0.75))
    fall_defence_up = int(45 + ((recovery - 50) * 0.8))

    if speed >= 90:
        speed_class = "very_fast"
    elif speed >= 75:
        speed_class = "fast"
    elif speed >= 55:
        speed_class = "normal"
    else:
        speed_class = "slow"

    if aggression >= 80:
        ai_style = "berserker"
    elif aggression >= 65:
        ai_style = "aggressive"
    elif counter_rate >= 70:
        ai_style = "patient"
    else:
        ai_style = "balanced"

    return {
        "life": max(650, life),
        "attack": max(60, attack),
        "defence": max(60, defence),
        "fall_defence_up": max(0, fall_defence_up),
        "speed_class": speed_class,
        "ai_profile": ai_style,
    }


def tier_seed(stats: Dict[str, int]) -> str:
    total = sum(int(stats[field]) for field in stat_fields())
    if total >= 520:
        return "Elite Prospect"
    if total >= 500:
        return "Contender Prospect"
    return "Prospect"


def build_generated_payload(fighter: Dict[str, Any]) -> Dict[str, Any]:
    identity = fighter.get("identity", {})
    classification = fighter.get("classification", {})
    appearance = fighter.get("appearance", {})
    stats = fighter.get("stats", {})
    ai_profile = fighter.get("ai_profile", {})
    moveset = fighter.get("moveset", {})

    validate_stats(stats)

    fid = fighter["fighter_id"]
    display_name = identity.get("display_name") or identity.get("name") or fid
    creator = identity.get("creator_name", "")
    archetype = classification.get("archetype") or ai_profile.get("base_archetype") or "balanced"
    template_base = resolve_template(archetype, moveset.get("template_base"))
    template_meta = CONFIG["fighter_asset_registry"].get("templates", {}).get(template_base, {})

    power_index = compute_power_index(stats)
    engine_stats = derive_engine_stats(stats, ai_profile)

    primary = appearance.get("primary_color", "black")
    secondary = appearance.get("secondary_color", "white")
    accent = appearance.get("accent_color", "red")
    palette_key = f"{primary}_{secondary}_{accent}"
    palette_id = CONFIG["fighter_asset_registry"].get("palette_map", {}).get(palette_key)
    portrait_style = appearance.get("portrait_style", "serious")
    portrait_asset = CONFIG["fighter_asset_registry"].get("portraits", {}).get(portrait_style)

    return {
        "fighter_id": fid,
        "live": False,
        "schema_version": fighter.get("schema_version", "1.0.0"),
        "identity": {
            "name": display_name,
            "display_name": display_name,
            "nickname": identity.get("nickname", ""),
            "creator_name": creator,
            "hometown": identity.get("hometown", ""),
            "country": identity.get("country", ""),
            "bio_short": identity.get("bio_short", ""),
        },
        "classification": classification,
        "template_assignment": {
            "base_template": template_base,
            "archetype": archetype,
            "moveset_style": moveset.get("moveset_style", ""),
            "finisher": moveset.get("finisher", ""),
            "signature_1": moveset.get("signature_1", ""),
            "signature_2": moveset.get("signature_2", ""),
            "signature_3": moveset.get("signature_3", ""),
            "default_ai_package": template_meta.get("default_ai_package", "balanced_v1"),
        },
        "stats": stats,
        "derived_stats": engine_stats,
        "ai_profile": ai_profile,
        "visuals": appearance,
        "moveset": moveset,
        "runtime": {
            "template_folder": template_meta.get("base_char_folder", template_base),
            "runtime_character_id": f"custom_{normalize_key(fid)}",
            "runtime_display_name": display_name,
            "palette_id": palette_id,
            "portrait_asset": portrait_asset,
            "ai_package": template_meta.get("default_ai_package", "balanced_v1"),
        },
        "league_metadata": {
            "power_index": power_index,
            "tier_seed": tier_seed(stats),
            "archetype": archetype,
            "author_credit": creator,
        },
    }


def generate_one(draft_path: Path) -> Dict[str, Any]:
    fighter = load_json(draft_path)
    if fighter.get("status") not in ("submitted", "draft", "approved"):
        raise ValueError("Unexpected fighter status")

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


def main() -> None:
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_META_DIR.mkdir(parents=True, exist_ok=True)

    processed = 0
    for draft_path in DRAFTS_DIR.glob("*.json"):
        fighter = load_json(draft_path, {})
        if fighter.get("status") != "submitted":
            continue

        generate_one(draft_path)

        fighter["status"] = "approved"
        approved_path = APPROVED_DIR / draft_path.name
        save_json(approved_path, fighter)
        processed += 1

    rebuild_aggregate_metadata()
    print(f"Generated {processed} fighter(s).")


if __name__ == "__main__":
    main()
