import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHARS_DIR = ROOT / "chars"
META_PATH = ROOT / "fighters_metadata.json"

DEFAULT_AUTHOR = "Legacy Fighter"
DEFAULT_ARCHETYPE = "Roster"
DEFAULT_POWER_INDEX = 50

CAPCOM_NAMES = {
    "ryu", "ken", "chunli", "chun-li", "guile", "blanka", "zangief", "dhalsim",
    "cammy", "vega", "balrog", "mbison", "m. bison", "sagat", "akuma",
    "dan", "sakura", "ibuki", "juri", "rashid", "ehonda", "e honda", "honda",
    "cody", "guy", "hugo", "poison", "rolento", "lucia"
}

SNK_NAMES = {
    "kyo", "kyo kusanagi", "iori", "iori yagami", "terry", "terry bogard",
    "andy", "andy bogard", "joe higashi", "mai", "mai shiranui", "athena",
    "kensou", "ralf", "clark", "leona", "kim", "kim dong hwan", "geese",
    "rock howard", "ryo", "robert", "takuma", "yuri", "benimaru", "shingo",
    "rugal", "goenitz", "oswald"
}

MARVEL_NAMES = {
    "thor", "hulk", "iron man", "spider-man", "spiderman", "wolverine",
    "captain america", "magneto", "storm", "cyclops", "venom", "thanos",
    "doctor doom", "doom", "deadpool", "loki", "black panther"
}

DC_NAMES = {
    "batman", "superman", "wonder woman", "flash", "green lantern",
    "aquaman", "joker", "harley quinn", "catwoman", "bane", "darkseid"
}

SKIP_FOLDERS = {
    "stages",
    "data",
    "__pycache__"
}


def norm(text: str) -> str:
    return (
        (text or "")
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


def guess_author(name: str) -> str:
    n = norm(name)

    if n in SNK_NAMES:
        return "SNK"
    if n in CAPCOM_NAMES:
        return "Capcom"
    if n in MARVEL_NAMES:
        return "Marvel"
    if n in DC_NAMES:
        return "DC"

    if any(x in n for x in ("kusanagi", "yagami", "bogard", "shiranui", "kensou", "rugal", "goenitz")):
        return "SNK"
    if any(x in n for x in ("blanka", "chun", "dhalsim", "zangief", "cammy", "akuma", "sagat", "guile")):
        return "Capcom"
    if any(x in n for x in ("thor", "wolverine", "spider", "magneto", "venom", "doom", "deadpool")):
        return "Marvel"
    if any(x in n for x in ("batman", "superman", "joker", "harley", "darkseid")):
        return "DC"

    return DEFAULT_AUTHOR


def guess_archetype(name: str) -> str:
    n = norm(name)

    if any(x in n for x in ("zangief", "hulk", "thor", "bane", "juggernaut")):
        return "Power"
    if any(x in n for x in ("ryu", "ken", "kyo", "iori", "terry", "guile")):
        return "Striker"
    if any(x in n for x in ("chun", "cammy", "mai", "ibuki", "sakura")):
        return "Agile"
    if any(x in n for x in ("doom", "magneto", "venom", "akuma")):
        return "Hybrid"

    return DEFAULT_ARCHETYPE


def guess_power_index(name: str) -> int:
    n = norm(name)

    if any(x in n for x in ("hulk", "thor", "akuma", "magneto", "doom", "juggernaut")):
        return 85
    if any(x in n for x in ("ryu", "ken", "kyo", "iori", "terry", "guile", "cammy", "chun")):
        return 72
    if any(x in n for x in ("sakura", "dan", "kensou", "athena")):
        return 62

    return DEFAULT_POWER_INDEX


def load_metadata() -> tuple[dict, bool]:
    if not META_PATH.exists():
        return {"fighters": {}}, True

    with open(META_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "fighters" in data and isinstance(data["fighters"], dict):
        return data, True

    if isinstance(data, dict):
        return data, False

    raise ValueError("fighters_metadata.json must be a JSON object")


def save_metadata(data: dict):
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_best_def_file(folder: Path) -> Path | None:
    defs = sorted(folder.glob("*.def"))

    if not defs:
        return None

    # Prefer a def matching the folder name
    folder_name_norm = norm(folder.name)
    for d in defs:
        if norm(d.stem) == folder_name_norm:
            return d

    # Otherwise prefer the first .def alphabetically
    return defs[0]


def discover_native_fighters():
    if not CHARS_DIR.exists():
        raise FileNotFoundError(f"chars folder not found: {CHARS_DIR}")

    fighters = []

    for item in sorted(CHARS_DIR.iterdir()):
        if not item.is_dir():
            continue

        if item.name.lower() in SKIP_FOLDERS:
            continue

        def_file = find_best_def_file(item)
        if not def_file:
            continue

        display_name = def_file.stem.strip() or item.name.strip()

        fighters.append({
            "display_name": display_name,
            "folder_name": item.name,
            "def_file": def_file.name,
            "def_path": f"{item.name}/{def_file.name}"
        })

    return fighters


def main():
    data, wrapped = load_metadata()
    fighters_meta = data["fighters"] if wrapped else data

    native_fighters = discover_native_fighters()

    added = 0
    already_present = 0

    for fighter in native_fighters:
        display_name = fighter["display_name"]

        if display_name in fighters_meta:
            already_present += 1

            # backfill missing native fields on existing entry
            meta = fighters_meta[display_name]
            if isinstance(meta, dict):
                meta.setdefault("char_folder", fighter["folder_name"])
                meta.setdefault("def_file", fighter["def_file"])
                meta.setdefault("def_path", fighter["def_path"])
                meta.setdefault("source", "native")
            continue

        fighters_meta[display_name] = {
            "author": guess_author(display_name),
            "archetype": guess_archetype(display_name),
            "power_index": guess_power_index(display_name),
            "source": "native",
            "char_folder": fighter["folder_name"],
            "def_file": fighter["def_file"],
            "def_path": fighter["def_path"]
        }
        added += 1

    save_metadata(data)

    print(f"Native char folders scanned: {len(native_fighters)}")
    print(f"Added metadata entries: {added}")
    print(f"Already present: {already_present}")
    print(f"Saved: {META_PATH}")


if __name__ == "__main__":
    main()