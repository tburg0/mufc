import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

APPROVED_DIR = ROOT / "submissions" / "approved"
GENERATED_DIR = ROOT / "generated" / "fighters"
CHARS_DIR = ROOT / "chars"

ARCHETYPE_TEMPLATE_MAP = {
    "Rushdown": "template_rush_01",
    "Grappler": "template_grapple_01",
    "Zoner": "template_zone_01",
    "Balanced": "template_balance_01",
    "Summoner": "template_summon_01",
}

PALETTE_SLOT_MAP = {
    "red_black": 1,
    "blue_white": 2,
    "green_black": 3,
    "purple_gold": 4,
    "silver_blue": 5,
    "orange_black": 6,
    "crimson_white": 7,
    "shadow_gray": 8,
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def sanitize_runtime_name(fighter_id: str) -> str:
    safe = fighter_id.lower().strip()
    safe = safe.replace("-", "_").replace(" ", "_")
    safe = re.sub(r"[^a-z0-9_]", "", safe)
    return f"custom_{safe}"


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
        out = [
            "[Info]\n",
            f'name = "{display_name}"\n',
            f'displayname = "{display_name}"\n',
            "\n",
        ] + out

    with def_path.open("w", encoding="utf-8") as f:
        f.writelines(out)


def palette_slot_from_visuals(visuals: dict) -> int:
    palette_name = (visuals.get("palette") or "").strip()
    return PALETTE_SLOT_MAP.get(palette_name, 1)


def preferred_ai_level(ai_profile: str) -> int:
    profile = (ai_profile or "").strip().lower()
    if profile == "berserker":
        return 8
    if profile == "aggressive":
        return 7
    if profile == "balanced":
        return 6
    if profile == "patient":
        return 5
    return 6


def patch_data_stats(runtime_dir: Path, life: int, attack: int, defence: int):
    """
    Best-effort patch of [Data] section values in CNS/ST files.
    This works well for templates that define life/attack/defence
    in a standard [Data] block.
    """
    candidate_files = list(runtime_dir.glob("*.cns")) + list(runtime_dir.glob("*.st"))
    if not candidate_files:
        return

    patched_any = False

    for path in candidate_files:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        out = []
        in_data = False
        touched_file = False

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
                    touched_file = True
                    continue
                if lower.startswith("attack"):
                    out.append(f"attack = {attack}\n")
                    touched_file = True
                    continue
                if lower.startswith("defence"):
                    out.append(f"defence = {defence}\n")
                    touched_file = True
                    continue

            out.append(line)

        if touched_file:
            with path.open("w", encoding="utf-8") as f:
                f.writelines(out)
            patched_any = True

    if not patched_any:
        print(f"Warning: no [Data] stats patched in {runtime_dir.name}")


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
    build = approved.get("build", {})
    visuals = approved.get("visuals", {})
    derived_stats = generated.get("derived_stats", {})

    fighter_name = identity.get("name")
    creator = identity.get("creator_name")
    archetype = build.get("archetype")

    if not fighter_name:
        raise ValueError("Approved fighter missing identity.name")
    if not archetype:
        raise ValueError("Approved fighter missing build.archetype")

    template_name = ARCHETYPE_TEMPLATE_MAP.get(archetype)
    if not template_name:
        raise ValueError(f"No template mapping for archetype: {archetype}")

    template_dir = CHARS_DIR / template_name
    if not template_dir.exists():
        raise FileNotFoundError(f"Template folder not found: {template_dir}")

    runtime_character = sanitize_runtime_name(fighter_id)
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
    ai_profile = str(derived_stats.get("ai_profile", "balanced"))

    patch_data_stats(runtime_dir, life=life, attack=attack, defence=defence)

    runtime_meta = {
        "fighter_id": fighter_id,
        "runtime_character": runtime_character,
        "display_name": fighter_name,
        "creator": creator,
        "archetype": archetype,
        "base_template": template_name,
        "visuals": visuals,
        "palette_slot": palette_slot_from_visuals(visuals),
        "generated_stats": {
            "life": life,
            "attack": attack,
            "defence": defence,
            "ai_profile": ai_profile,
            "preferred_ai_level": preferred_ai_level(ai_profile),
        },
        "league_metadata": generated.get("league_metadata", {}),
    }
    save_json(runtime_dir / "fighter_meta.json", runtime_meta)

    return {
        "fighter_id": fighter_id,
        "runtime_character": runtime_character,
        "runtime_def": str(runtime_def),
        "base_template": template_name,
        "display_name": fighter_name,
        "palette_slot": runtime_meta["palette_slot"],
        "life": life,
        "attack": attack,
        "defence": defence,
        "ai_profile": ai_profile,
        "preferred_ai_level": runtime_meta["generated_stats"]["preferred_ai_level"],
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_runtime_character.py <fighter_id>")
        sys.exit(1)

    fighter_id = sys.argv[1]
    result = generate_runtime_character(fighter_id)

    print(f"Generated runtime character for {result['fighter_id']}")
    print(f"Display name: {result['display_name']}")
    print(f"Base template: {result['base_template']}")
    print(f"Runtime character: {result['runtime_character']}")
    print(f"Runtime def: {result['runtime_def']}")
    print(f"Palette slot: {result['palette_slot']}")
    print(f"Life/Attack/Defence: {result['life']}/{result['attack']}/{result['defence']}")
    print(f"AI profile: {result['ai_profile']} | Preferred AI: {result['preferred_ai_level']}")


if __name__ == "__main__":
    main()