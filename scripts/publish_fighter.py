from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
APPROVED_DIR = ROOT / "submissions" / "approved"
GENERATED_DIR = ROOT / "generated" / "fighters"
CHARS_DIR = ROOT / "chars"
ROSTER_FILE = ROOT / "generated" / "published_roster.json"
MAPPING_FILE = ROOT / "generated" / "runtime_mapping.json"
STATE_FILE = ROOT / "league_state.json"

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


def load_json(path: Path, default=None):
    if default is None:
        default = {}
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


CONFIG = {
    "fighter_asset_registry": load_json(CONFIG_DIR / "fighter_asset_registry.json", {}),
}


def slugify(value: str) -> str:
    value = (value or "").strip().lower().replace("-", "_").replace(" ", "_")
    value = re.sub(r"[^a-z0-9_]", "", value)
    return value


def sanitize_runtime_name(fighter_id: str) -> str:
    return f"custom_{slugify(fighter_id)}"


def resolve_template_dir(template_name: str) -> Path:
    direct_dir = CHARS_DIR / template_name
    if direct_dir.exists():
        return direct_dir

    templates = CONFIG["fighter_asset_registry"].get("templates", {})
    template_cfg = templates.get(template_name, {})
    base_char_folder = template_cfg.get("base_char_folder")
    if base_char_folder:
        mapped_dir = CHARS_DIR / str(base_char_folder)
        if mapped_dir.exists():
            return mapped_dir

    raise FileNotFoundError(f"Template folder not found: {direct_dir}")


def find_template_def(template_dir: Path, template_name: str) -> Path:
    expected = template_dir / f"{template_name}.def"
    if expected.exists():
        return expected
    defs = list(template_dir.glob("*.def"))
    if not defs:
        raise FileNotFoundError(f"No .def file found in template folder: {template_dir}")
    if len(defs) == 1:
        return defs[0]
    for d in defs:
        if d.stem.lower() == template_name.lower():
            return d
    raise RuntimeError(f"Multiple .def files found in {template_dir}, cannot determine main def")


def patch_info_names(def_path: Path, display_name: str):
    with def_path.open("r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    out = []
    in_info = False
    saw_name = False
    saw_displayname = False
    info_inserted = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_info and not info_inserted:
                if not saw_name:
                    out.append(f'name = "{display_name}"\n')
                if not saw_displayname:
                    out.append(f'displayname = "{display_name}"\n')
                info_inserted = True
            in_info = stripped.lower() == "[info]"
            out.append(line)
            continue
        if in_info:
            lowered = stripped.lower()
            if lowered.startswith("name"):
                out.append(f'name = "{display_name}"\n')
                saw_name = True
                continue
            if lowered.startswith("displayname"):
                out.append(f'displayname = "{display_name}"\n')
                saw_displayname = True
                continue
        out.append(line)

    if in_info and not info_inserted:
        if not saw_name:
            out.append(f'name = "{display_name}"\n')
        if not saw_displayname:
            out.append(f'displayname = "{display_name}"\n')

    if not any(l.strip().lower() == "[info]" for l in lines):
        out = ["[Info]\n", f'name = "{display_name}"\n', f'displayname = "{display_name}"\n', "\n"] + out

    with def_path.open("w", encoding="utf-8") as f:
        f.writelines(out)


def patch_palette_defaults(def_path: Path, palette_slot: int):
    with def_path.open("r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    out = []
    in_info = False
    inserted = False
    desired = f"pal.defaults = {palette_slot}\n"

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_info and not inserted:
                out.append(desired)
                inserted = True
            in_info = stripped.lower() == "[info]"
            out.append(line)
            continue
        if in_info and stripped.lower().startswith("pal.defaults"):
            out.append(desired)
            inserted = True
            continue
        out.append(line)

    if in_info and not inserted:
        out.append(desired)

    with def_path.open("w", encoding="utf-8") as f:
        f.writelines(out)


def patch_data_stats(runtime_dir: Path, life: int, attack: int, defence: int):
    candidate_files = list(runtime_dir.glob("*.cns")) + list(runtime_dir.glob("*.st"))
    for path in candidate_files:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        out = []
        in_data = False
        touched = False
        for line in lines:
            stripped = line.strip()
            lower = stripped.lower()
            if stripped.startswith("[") and stripped.endswith("]"):
                in_data = stripped.lower() == "[data]"
                out.append(line)
                continue
            if in_data:
                if lower.startswith("life"):
                    out.append(f"life = {life}\n")
                    touched = True
                    continue
                if lower.startswith("attack"):
                    out.append(f"attack = {attack}\n")
                    touched = True
                    continue
                if lower.startswith("defence"):
                    out.append(f"defence = {defence}\n")
                    touched = True
                    continue
            out.append(line)
        if touched:
            with path.open("w", encoding="utf-8") as f:
                f.writelines(out)


def patch_runtime_constants(runtime_dir: Path, tuning: Dict[str, Any]):
    size_cfg = tuning.get("size", {})
    vel_cfg = tuning.get("velocity", {})
    move_cfg = tuning.get("movement", {})
    candidate_files = list(runtime_dir.glob("*.cns")) + list(runtime_dir.glob("*.st"))
    if not candidate_files:
        return

    section_map = {
        "data": {},
        "size": {
            "xscale": size_cfg.get("xscale"),
            "yscale": size_cfg.get("yscale"),
            "attack.dist": size_cfg.get("attack_dist"),
        },
        "velocity": {
            "walk.fwd": vel_cfg.get("walk_fwd"),
            "walk.back": vel_cfg.get("walk_back"),
            "run.fwd": f"{vel_cfg.get('run_fwd_x')}, {vel_cfg.get('run_fwd_y')}",
            "run.back": f"{vel_cfg.get('run_back_x')}, {vel_cfg.get('run_back_y')}",
            "jump.neu": f"{vel_cfg.get('jump_neu_x')}, {vel_cfg.get('jump_neu_y')}",
            "jump.fwd": vel_cfg.get("jump_fwd"),
            "jump.back": vel_cfg.get("jump_back"),
            "runjump.fwd": f"{vel_cfg.get('runjump_fwd_x')}, {vel_cfg.get('runjump_fwd_y')}",
            "runjump.back": f"{vel_cfg.get('runjump_back_x')}, {vel_cfg.get('runjump_back_y')}",
            "airjump.neu": f"{vel_cfg.get('airjump_neu_x')}, {vel_cfg.get('airjump_neu_y')}",
            "airjump.back": vel_cfg.get("airjump_back"),
            "airjump.fwd": vel_cfg.get("airjump_fwd"),
        },
        "movement": {
            "airjump.num": move_cfg.get("airjump_num"),
            "airjump.height": move_cfg.get("airjump_height"),
            "yaccel": move_cfg.get("yaccel"),
        },
    }

    for path in candidate_files:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        out = []
        current_section = None
        touched = False
        seen = {key: set() for key in section_map}

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                section_name = stripped[1:-1].strip().lower()
                if current_section in section_map:
                    pending = {
                        key: value
                        for key, value in section_map[current_section].items()
                        if value is not None and key not in seen[current_section]
                    }
                    for key, value in pending.items():
                        out.append(f"{key} = {value}\n")
                        touched = True
                current_section = section_name
                out.append(line)
                continue

            if current_section in section_map:
                line_key = stripped.split("=", 1)[0].strip().lower() if "=" in stripped else None
                if line_key and line_key in section_map[current_section] and section_map[current_section][line_key] is not None:
                    out.append(f"{line_key} = {section_map[current_section][line_key]}\n")
                    seen[current_section].add(line_key)
                    touched = True
                    continue

            out.append(line)

        if current_section in section_map:
            pending = {
                key: value
                for key, value in section_map[current_section].items()
                if value is not None and key not in seen[current_section]
            }
            for key, value in pending.items():
                out.append(f"{key} = {value}\n")
                touched = True

        if touched:
            with path.open("w", encoding="utf-8") as f:
                f.writelines(out)


def palette_slot_from_appearance(appearance: Dict[str, Any], runtime: Dict[str, Any]) -> int:
    palette_id = str(runtime.get("palette_id", ""))
    palette_map = CONFIG["fighter_asset_registry"].get("palette_map", {})
    ordered_keys = list(palette_map.keys())
    for idx, key in enumerate(ordered_keys, start=1):
        if palette_map[key] == palette_id:
            return idx
    # fallback slot
    return 1


def preferred_ai_level(ai_profile: Dict[str, Any]) -> int:
    aggression = int(ai_profile.get("aggression", 50))
    risk = int(ai_profile.get("risk_tolerance", 50))
    finish = int(ai_profile.get("finish_priority", 50))
    return max(1, min(8, round(4 + (aggression + risk + finish) / 75)))


def generate_runtime_character(fighter_id: str) -> dict:
    approved_path = APPROVED_DIR / f"{fighter_id}.json"
    generated_path = GENERATED_DIR / f"{fighter_id}.json"
    if not approved_path.exists():
        raise FileNotFoundError(f"Approved fighter not found: {approved_path}")
    if not generated_path.exists():
        raise FileNotFoundError(f"Generated fighter not found: {generated_path}")

    approved = load_json(approved_path)
    generated = load_json(generated_path)
    identity = approved.get("identity", {})
    classification = approved.get("classification", {})
    appearance = approved.get("appearance", {})
    assembly = approved.get("assembly", {})
    runtime_cfg = generated.get("runtime", {})
    derived_stats = generated.get("derived_stats", {})

    fighter_name = identity.get("display_name")
    creator = identity.get("creator_name")
    archetype = classification.get("archetype")
    if not fighter_name:
        raise ValueError("Approved fighter missing identity.display_name")
    if not archetype:
        raise ValueError("Approved fighter missing classification.archetype")

    template_name = runtime_cfg.get("template_folder") or DEFAULT_ARCHETYPE_TEMPLATE_MAP.get(slugify(archetype), "template_balanced_01")
    template_dir = resolve_template_dir(template_name)

    runtime_character = runtime_cfg.get("runtime_character_id") or sanitize_runtime_name(fighter_id)
    runtime_dir = CHARS_DIR / runtime_character
    if runtime_dir.exists():
        shutil.rmtree(runtime_dir)
    shutil.copytree(template_dir, runtime_dir)

    template_def = find_template_def(runtime_dir, template_name)
    runtime_def = runtime_dir / f"{runtime_character}.def"
    if template_def.resolve() != runtime_def.resolve():
        template_def.rename(runtime_def)
    patch_info_names(runtime_def, fighter_name)

    life = int(derived_stats.get("life", 1000))
    attack = int(derived_stats.get("attack", 100))
    defence = int(derived_stats.get("defence", 100))
    palette_slot = palette_slot_from_appearance(appearance, runtime_cfg)
    patch_palette_defaults(runtime_def, palette_slot)
    patch_data_stats(runtime_dir, life, attack, defence)
    patch_runtime_constants(runtime_dir, runtime_cfg.get("runtime_tuning", {}))

    runtime_meta = {
        "fighter_id": fighter_id,
        "runtime_character": runtime_character,
        "display_name": fighter_name,
        "creator": creator,
        "archetype": archetype,
        "base_template": template_name,
        "assembly": assembly,
        "appearance": appearance,
        "palette_slot": palette_slot,
        "generated_stats": {
            "life": life,
            "attack": attack,
            "defence": defence,
            "preferred_ai_level": preferred_ai_level(approved.get("ai_profile", {})),
        },
        "runtime_tuning": runtime_cfg.get("runtime_tuning", {}),
        "league_metadata": generated.get("league_metadata", {}),
    }
    save_json(runtime_dir / "fighter_meta.json", runtime_meta)
    return runtime_meta


def publish_fighter(fighter_id: str):
    approved = load_json(APPROVED_DIR / f"{fighter_id}.json")
    generated_path = GENERATED_DIR / f"{fighter_id}.json"
    generated = load_json(generated_path)
    runtime_meta = generate_runtime_character(fighter_id)

    fighter_name = approved.get("identity", {}).get("display_name")
    creator = approved.get("identity", {}).get("creator_name")
    archetype = approved.get("classification", {}).get("archetype")
    power_index = generated.get("league_metadata", {}).get("power_index", 0)

    generated["live"] = True
    save_json(generated_path, generated)

    roster = load_json(ROSTER_FILE, {"fighters": []})
    fighters = roster.get("fighters", [])
    new_entry = {
        "fighter_id": fighter_id,
        "name": fighter_name,
        "creator": creator,
        "archetype": archetype,
        "runtime_template": runtime_meta["runtime_character"],
        "live": True,
    }
    replaced = False
    for i, f in enumerate(fighters):
        if f.get("fighter_id") == fighter_id or f.get("name") == fighter_name:
            fighters[i] = new_entry
            replaced = True
            break
    if not replaced:
        fighters.append(new_entry)
    roster["fighters"] = fighters
    save_json(ROSTER_FILE, roster)

    mapping = load_json(MAPPING_FILE, {})
    mapping[fighter_name] = {
        "fighter_id": fighter_id,
        "runtime_character": runtime_meta["runtime_character"],
        "creator": creator,
        "power_index": power_index,
        "archetype": archetype,
        "published": True,
        "palette_slot": runtime_meta["palette_slot"],
        "preferred_ai_level": runtime_meta["generated_stats"]["preferred_ai_level"],
        "runtime_tuning": runtime_meta.get("runtime_tuning", {}),
    }
    save_json(MAPPING_FILE, mapping)

    state = load_json(STATE_FILE, {
        "champion": None,
        "debut_queue": [],
        "match_count": 0,
    })
    debut_queue = state.get("debut_queue", [])
    if fighter_name not in debut_queue:
        debut_queue.append(fighter_name)
    state["debut_queue"] = debut_queue
    save_json(STATE_FILE, state)

    return {
        "fighter_id": fighter_id,
        "name": fighter_name,
        "runtime_character": runtime_meta["runtime_character"],
        "queued_for_debut": True,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: py scripts\\publish_fighter.py <fighter_id>")
        sys.exit(1)
    fighter_id = sys.argv[1]
    result = publish_fighter(fighter_id)
    print(f"Published {result['name']} ({result['fighter_id']})")
    print(f"Runtime character: {result['runtime_character']}")
    print("Queued for debut: yes")


if __name__ == "__main__":
    main()
