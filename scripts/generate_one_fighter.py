import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DRAFTS_DIR = ROOT / "submissions" / "drafts"
APPROVED_DIR = ROOT / "submissions" / "approved"
GENERATED_DIR = ROOT / "generated" / "fighters"
GENERATED_META_DIR = ROOT / "generated" / "fighters_metadata"
AGGREGATE_META_FILE = ROOT / "fighters_metadata.json"

ARCHETYPE_TEMPLATE_MAP = {
    "Rushdown": "base_rush_01",
    "Grappler": "base_grapple_01",
    "Zoner": "base_zone_01",
    "Balanced": "base_balance_01",
    "Summoner": "base_summon_01",
}

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def compute_power_index(stats: dict) -> float:
    health = stats["health"]
    power = stats["power"]
    defense = stats["defense"]
    return round((health * 0.5 + power * 0.35 + defense * 0.15) / 10, 1)

def derive_engine_stats(stats: dict) -> dict:
    health = stats["health"]
    power = stats["power"]
    defense = stats["defense"]
    aggression = stats["aggression"]
    speed = stats["speed"]

    life = int(700 + (health - 50) * 6)
    attack = int(80 + (power - 50) * 0.8)
    defence = int(80 + (defense - 50) * 0.8)

    if speed >= 90:
        speed_class = "very_fast"
    elif speed >= 75:
        speed_class = "fast"
    elif speed >= 60:
        speed_class = "normal"
    else:
        speed_class = "slow"

    if aggression >= 85:
        ai_profile = "berserker"
    elif aggression >= 70:
        ai_profile = "aggressive"
    elif aggression >= 55:
        ai_profile = "balanced"
    else:
        ai_profile = "patient"

    return {
        "life": life,
        "attack": attack,
        "defence": defence,
        "speed_class": speed_class,
        "ai_profile": ai_profile,
    }

def tier_seed(stats: dict) -> str:
    total = sum(stats.values())
    if total >= 395:
        return "Elite Prospect"
    if total >= 385:
        return "Contender Prospect"
    return "Prospect"

def rebuild_aggregate_metadata():
    fighters = {}
    GENERATED_META_DIR.mkdir(parents=True, exist_ok=True)

    for path in GENERATED_META_DIR.glob("*.json"):
        data = load_json(path)
        fighters[data["name"]] = {
            "author": data["author"],
            "power_index": data["power_index"],
            "archetype": data["archetype"],
        }

    save_json(AGGREGATE_META_FILE, {"fighters": fighters})

def generate_one_file(path: Path):
    fighter = load_json(path)

    fid = fighter["fighter_id"]
    name = fighter["identity"]["name"]
    creator = fighter["identity"]["creator_name"]
    archetype = fighter["build"]["archetype"]
    stats = fighter["build"]["stats"]

    if archetype not in ARCHETYPE_TEMPLATE_MAP:
        raise ValueError(f"Unknown archetype: {archetype}")

    base_template = ARCHETYPE_TEMPLATE_MAP[archetype]
    power_index = compute_power_index(stats)
    engine_stats = derive_engine_stats(stats)

    generated = {
        "fighter_id": fid,
        "live": True,
        "identity": {
            "name": name,
            "nickname": fighter["identity"]["nickname"],
            "creator_name": creator,
            "hometown": fighter["identity"]["hometown"],
        },
        "template_assignment": {
            "base_template": base_template,
            "archetype": archetype,
            "move_package": fighter["build"]["move_package"],
            "trait": fighter["build"]["trait"],
            "super_style": fighter["build"]["super_style"],
        },
        "derived_stats": engine_stats,
        "visuals": fighter["visuals"],
        "league_metadata": {
            "power_index": power_index,
            "tier_seed": tier_seed(stats),
            "archetype": archetype,
            "author_credit": creator,
        },
    }

    generated_meta = {
        "fighter_id": fid,
        "name": name,
        "author": creator,
        "power_index": power_index,
        "archetype": archetype,
    }

    save_json(GENERATED_DIR / f"{fid}.json", generated)
    save_json(GENERATED_META_DIR / f"{fid}.json", generated_meta)
    rebuild_aggregate_metadata()

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_one_fighter.py <fighter_id>")
        sys.exit(1)

    fighter_id = sys.argv[1]

    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_META_DIR.mkdir(parents=True, exist_ok=True)

    source = DRAFTS_DIR / f"{fighter_id}.json"

    if not source.exists():
        print(f"Draft not found: {source}")
        sys.exit(1)

    fighter = load_json(source)
    fighter["status"] = "approved"

    approved_path = APPROVED_DIR / source.name
    save_json(approved_path, fighter)

    generate_one_file(approved_path)
    print(f"Approved and generated: {fighter_id}")

if __name__ == "__main__":
    main()