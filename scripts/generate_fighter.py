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
    "runtime_package_effects": load_json(CONFIG_DIR / "runtime_package_effects.json", {}),
    "runtime_move_loadouts": load_json(CONFIG_DIR / "runtime_move_loadouts.json", {}),
    "runtime_move_variants": load_json(CONFIG_DIR / "runtime_move_variants.json", {}),
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
REQUIRED_ASSEMBLY_FIELDS = [
    "body_class",
    "locomotion_package",
    "strike_package",
    "grapple_package",
    "special_package",
    "intro_package",
    "victory_package",
]


def slugify(value: str) -> str:
    value = (value or "").strip().lower().replace("-", "_").replace(" ", "_")
    return "".join(ch for ch in value if ch.isalnum() or ch == "_")


def palette_key_from_colors(appearance: Dict[str, Any]) -> str:
    return f'{appearance.get("primary_color","")}_{appearance.get("secondary_color","")}_{appearance.get("accent_color","")}'.strip("_").lower()


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def get_template_for_archetype(archetype: str) -> str:
    archetype_key = slugify(archetype)
    asset_registry = CONFIG["fighter_asset_registry"].get("compatibility_rules", {})
    compat = asset_registry.get("archetype_to_template", {})
    if archetype_key in compat and compat[archetype_key]:
        return compat[archetype_key][0]
    return DEFAULT_ARCHETYPE_TEMPLATE_MAP.get(archetype_key, "template_balanced_01")


def get_ai_package_for_archetype(archetype: str) -> str:
    return DEFAULT_ARCHETYPE_AI_PACKAGE.get(slugify(archetype), "balanced_v1")


def choose_template_option(options: List[str], archetype: str) -> str:
    if not options:
        raise ValueError("No template options were provided")

    compat = CONFIG["fighter_asset_registry"].get("compatibility_rules", {}).get("archetype_to_template", {})
    preferred = [slugify(value) for value in compat.get(slugify(archetype), [])]

    for option in options:
        if slugify(option) in preferred:
            return option

    return options[0]


def get_package_profile(axis: str, package_name: str) -> Dict[str, Any]:
    profiles = CONFIG["runtime_package_effects"].get("profiles", {}).get(axis, {})
    return profiles.get(slugify(package_name), {})


def derive_package_tuning(assembly: Dict[str, Any]) -> Dict[str, Any]:
    package_tuning: Dict[str, Any] = {}
    for axis in ("strike_package", "grapple_package", "special_package"):
        selected = assembly.get(axis, "")
        package_tuning[axis] = {
            "selected": slugify(selected),
            "profile": get_package_profile(axis, selected),
        }
    return package_tuning


def derive_move_loadout(template_folder: str, moveset: Dict[str, Any]) -> Dict[str, Any]:
    template_cfg = CONFIG["runtime_move_loadouts"].get("templates", {}).get(template_folder, {})
    if not template_cfg:
        return {"template": template_folder, "enabled_families": [], "enabled_states": [], "selections": {}}

    enabled_families: List[str] = []

    def add_families(names: List[str]) -> None:
        for name in names:
            if name and name not in enabled_families:
                enabled_families.append(name)

    selectors = {
        "signature_1": template_cfg.get("signatures", {}).get(moveset.get("signature_1", ""), []),
        "signature_2": template_cfg.get("signatures", {}).get(moveset.get("signature_2", ""), []),
        "signature_3": template_cfg.get("signatures", {}).get(moveset.get("signature_3", ""), []),
        "finisher": template_cfg.get("finishers", {}).get(moveset.get("finisher", ""), []),
        "super_finisher": template_cfg.get("super_finishers", {}).get(moveset.get("super_finisher", ""), []),
    }

    for names in selectors.values():
        add_families(list(names))

    if not enabled_families:
        add_families(list(template_cfg.get("defaults", [])))

    family_states = template_cfg.get("families", {})
    enabled_states: List[int] = []
    for family in enabled_families:
        for state_no in family_states.get(family, []):
            if int(state_no) not in enabled_states:
                enabled_states.append(int(state_no))

    return {
        "template": template_folder,
        "enabled_families": enabled_families,
        "enabled_states": enabled_states,
        "selections": {
            "signature_1": moveset.get("signature_1", ""),
            "signature_2": moveset.get("signature_2", ""),
            "signature_3": moveset.get("signature_3", ""),
            "finisher": moveset.get("finisher", ""),
            "super_finisher": moveset.get("super_finisher", ""),
        },
    }


def derive_move_variant_plan(template_folder: str, moveset: Dict[str, Any], move_loadout: Dict[str, Any]) -> Dict[str, Any]:
    template_cfg = CONFIG["runtime_move_variants"].get("templates", {}).get(template_folder, {})
    selectors = ("signature_1", "signature_2", "signature_3", "finisher", "super_finisher")
    selected_variants: Dict[str, Dict[str, Any]] = {}
    family_profiles: Dict[str, Dict[str, Any]] = {}

    for selector in selectors:
        move_name = moveset.get(selector, "")
        selector_cfg = template_cfg.get(selector, {})
        variant = selector_cfg.get(move_name)
        if not variant:
            continue
        family = variant.get("family")
        if not family or family not in move_loadout.get("enabled_families", []):
            continue

        selected_variants[selector] = {
            "move": move_name,
            "family": family,
            "label": variant.get("label", move_name),
            "summary": variant.get("summary", ""),
            "damage_scale": float(variant.get("damage_scale", 1.0) or 1.0),
            "velocity_scale": float(variant.get("velocity_scale", 1.0) or 1.0),
            "range_scale": float(variant.get("range_scale", 1.0) or 1.0),
        }

        family_profile = family_profiles.setdefault(
            family,
            {"damage_scale": 1.0, "velocity_scale": 1.0, "range_scale": 1.0, "sources": []},
        )
        family_profile["damage_scale"] *= selected_variants[selector]["damage_scale"]
        family_profile["velocity_scale"] *= selected_variants[selector]["velocity_scale"]
        family_profile["range_scale"] *= selected_variants[selector]["range_scale"]
        family_profile["sources"].append(selector)

    return {
        "template": template_folder,
        "selected_variants": selected_variants,
        "family_profiles": family_profiles,
    }


def validate_assembly(fighter: Dict[str, Any]) -> Dict[str, Any]:
    assembly = fighter.get("assembly")
    if not assembly:
        return {}
    if not isinstance(assembly, dict):
        raise ValueError("assembly must be an object when provided")

    rules = CONFIG["fighter_validation_rules"].get("assembly_rules", {})
    required_fields = rules.get("required_fields_when_present", REQUIRED_ASSEMBLY_FIELDS)
    missing = [field for field in required_fields if not assembly.get(field)]
    if missing:
        raise ValueError(f'Missing assembly fields: {", ".join(missing)}')

    registry = CONFIG["fighter_asset_registry"].get("assembly_modules", {})
    archetype = slugify(fighter["classification"]["archetype"])
    alignment = slugify(fighter["classification"].get("alignment", "tweener"))

    body_class = slugify(assembly["body_class"])
    body_cfg = registry.get("body_class", {}).get(body_class)
    if not body_cfg:
        raise ValueError(f"Unknown assembly body_class: {assembly['body_class']}")
    if archetype not in [slugify(v) for v in body_cfg.get("allowed_archetypes", [])]:
        raise ValueError(f"Body class {assembly['body_class']} is not allowed for archetype {fighter['classification']['archetype']}")

    def validate_module(name: str, rule_key: str, expected_value: str) -> None:
        key = slugify(assembly[name])
        cfg = registry.get(name, {}).get(key)
        if not cfg:
            raise ValueError(f"Unknown assembly {name}: {assembly[name]}")
        allowed = [slugify(v) for v in cfg.get(rule_key, [])]
        if allowed and expected_value not in allowed:
            raise ValueError(f"Assembly {name}={assembly[name]} is incompatible with {expected_value}")

    validate_module("locomotion_package", "allowed_body_classes", body_class)
    validate_module("strike_package", "allowed_archetypes", archetype)
    validate_module("grapple_package", "allowed_archetypes", archetype)
    validate_module("special_package", "allowed_archetypes", archetype)
    validate_module("intro_package", "allowed_alignments", alignment)
    validate_module("victory_package", "allowed_alignments", alignment)

    return assembly


def resolve_template_folder(fighter: Dict[str, Any], assembly: Dict[str, Any], archetype: str) -> Tuple[str, str]:
    base_fighter = fighter.get("base_fighter") or {}

    if assembly:
        body_class = slugify(assembly["body_class"])
        body_map = CONFIG["fighter_asset_registry"].get("compatibility_rules", {}).get("body_class_to_template", {})
        options = body_map.get(body_class, [])
        if options:
            return choose_template_option(options, archetype), "assembly_body_class"
        body_cfg = CONFIG["fighter_asset_registry"].get("assembly_modules", {}).get("body_class", {}).get(body_class, {})
        runtime_template = body_cfg.get("runtime_template")
        if runtime_template:
            return runtime_template, "assembly_body_class"

    if base_fighter and base_fighter.get("char_folder"):
        return base_fighter["char_folder"], "base_fighter"

    return fighter["moveset"].get("template_base") or get_template_for_archetype(archetype), "archetype_template"


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
    assembly = validate_assembly(fighter)
    template_folder, template_source = resolve_template_folder(fighter, assembly, archetype)
    package_tuning = derive_package_tuning(assembly)
    move_loadout = derive_move_loadout(template_folder, fighter.get("moveset", {}))
    move_variant_plan = derive_move_variant_plan(template_folder, fighter.get("moveset", {}), move_loadout)

    runtime_character_id = f'custom_{slugify(fighter["fighter_id"])}'

    palette_key = palette_key_from_colors(appearance)
    palette_id = CONFIG["fighter_asset_registry"].get("palette_map", {}).get(
        palette_key, "palette_black_white_red_01.act"
    )
    ai_package = get_ai_package_for_archetype(archetype)
    body_class = slugify(assembly.get("body_class", "balanced_midweight"))
    locomotion = slugify(assembly.get("locomotion_package", "measured_step"))
    preferred_range = slugify(ai.get("preferred_range", "mid"))
    global_walk_scale = 1.0
    global_run_scale = 1.0
    global_jump_scale = 1.0
    global_attack_dist_delta = 0
    for package_data in package_tuning.values():
        profile = package_data.get("profile", {})
        global_walk_scale *= float(profile.get("walk_scale", 1.0) or 1.0)
        global_run_scale *= float(profile.get("run_scale", 1.0) or 1.0)
        global_jump_scale *= float(profile.get("jump_scale", 1.0) or 1.0)
        global_attack_dist_delta += int(profile.get("attack_dist_delta", 0) or 0)

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

    speed_factor = stats["speed"] / 65.0
    air_factor = stats["air"] / 65.0
    body_speed_mod = {
        "lightweight_striker": 1.08,
        "balanced_midweight": 1.0,
        "heavy_grappler": 0.93,
    }.get(body_class, 1.0)
    locomotion_mod = {
        "measured_step": 0.98,
        "pressure_walk": 1.03,
        "ring_cutter": 1.08,
        "juggernaut_stride": 0.92,
    }.get(locomotion, 1.0)

    base_walk = clamp(2.7 * speed_factor * body_speed_mod * locomotion_mod * global_walk_scale, 2.1, 3.9)
    base_run = clamp(base_walk * 1.7 * global_run_scale, 3.9, 7.2)
    base_jump_x = clamp(3.1 * speed_factor * body_speed_mod * global_jump_scale, 2.4, 4.6)
    base_jump_y = clamp(-8.5 - ((stats["air"] - 50) / 18.0), -11.6, -7.8)
    y_accel = clamp(0.60 - ((stats["air"] - 50) / 500.0), 0.50, 0.68)

    attack_dist = 160
    if preferred_range == "close":
        attack_dist = 145
    elif preferred_range == "far":
        attack_dist = 178
    elif preferred_range == "adaptive":
        attack_dist = 166
    attack_dist += global_attack_dist_delta

    x_scale = 1.0
    y_scale = 1.0
    x_scale += {"small": -0.06, "athletic": 0.0, "large": 0.05, "giant": 0.12}.get(slugify(appearance.get("body_type", "")), 0.0)
    y_scale += {"short": -0.06, "average": 0.0, "tall": 0.05}.get(slugify(appearance.get("height_class", "")), 0.0)
    y_scale += {"lean": -0.02, "defined": 0.0, "bulky": 0.04}.get(slugify(appearance.get("physique", "")), 0.0)

    runtime_tuning = {
        "size": {
            "xscale": round(clamp(x_scale, 0.86, 1.18), 3),
            "yscale": round(clamp(y_scale, 0.88, 1.2), 3),
            "attack_dist": int(attack_dist),
        },
        "velocity": {
            "walk_fwd": round(base_walk, 3),
            "walk_back": round(-base_walk * 0.72, 3),
            "run_fwd_x": round(base_run, 3),
            "run_fwd_y": 0.0,
            "run_back_x": round(-base_walk * 1.55, 3),
            "run_back_y": round(-2.2 - max(0.0, (speed_factor - 1.0) * 2.2), 3),
            "jump_neu_x": 0.0,
            "jump_neu_y": round(base_jump_y, 3),
            "jump_fwd": round(base_jump_x, 3),
            "jump_back": round(-base_jump_x * 1.04, 3),
            "runjump_fwd_x": round(base_run * 1.18, 3),
            "runjump_fwd_y": round(base_jump_y - 1.1, 3),
            "runjump_back_x": round(-base_run * 1.12, 3),
            "runjump_back_y": round(base_jump_y - 1.1, 3),
            "airjump_neu_x": 0.0,
            "airjump_neu_y": round(clamp(base_jump_y + 2.0, -9.0, -6.0), 3),
            "airjump_back": round(-2.3 * air_factor, 3),
            "airjump_fwd": round(2.3 * air_factor, 3),
        },
        "movement": {
            "airjump_num": 1 if stats["air"] >= 78 and body_class != "heavy_grappler" else 0,
            "airjump_height": 34 if stats["air"] >= 78 and body_class != "heavy_grappler" else 0,
            "yaccel": round(y_accel, 3),
        },
    }

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
        "assembly": assembly,
        "runtime_character_id": runtime_character_id,
        "runtime_display_name": fighter["identity"]["display_name"],
        "palette_id": palette_id,
        "portrait_asset": fighter["appearance"].get("portrait_style", "portrait_serious_base.png"),
        "ai_package": ai_package,
        "runtime_tuning": runtime_tuning,
        "package_tuning": package_tuning,
        "move_loadout": move_loadout,
        "move_variant_plan": move_variant_plan,
        "generator_version": "package-tuning-1.2",
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
        "assembly": fighter.get("assembly", {}),
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
    existing = load_json(AGGREGATE_META_FILE, {"fighters": {}})
    fighters: Dict[str, Any] = existing.get("fighters", {}).copy()

    # Keep only native fighters in aggregate metadata. Generated CAFs live in
    # generated/fighters_metadata and should not re-enter the native roster pool.
    preserved_native = {
        name: data
        for name, data in fighters.items()
        if isinstance(data, dict) and data.get("source") == "native"
    }

    save_json(AGGREGATE_META_FILE, {"fighters": preserved_native})


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
