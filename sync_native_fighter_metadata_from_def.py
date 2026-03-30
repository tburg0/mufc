import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHARS_DIR = ROOT / "chars"
META_PATH = ROOT / "fighters_metadata.json"

DEFAULT_AUTHOR = "Legacy Fighter"
DEFAULT_ARCHETYPE = "Roster"
DEFAULT_POWER_INDEX = 50

SKIP_FOLDERS = {
    "__pycache__",
}


def norm(text: str) -> str:
    return (
        (text or "")
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


def load_metadata():
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


def find_best_def_file(folder: Path):
    defs = sorted(folder.glob("*.def"))
    if not defs:
        return None

    folder_name_norm = norm(folder.name)

    for d in defs:
        if norm(d.stem) == folder_name_norm:
            return d

    return defs[0]


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1].strip()
    return value


def parse_def_info(def_path: Path):
    """
    Parse a MUGEN character .def and extract [Info] section values like:
      name = "Blanka"
      author = "SomeAuthor"
    """
    info = {}
    in_info = False

    with open(def_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue

            # remove inline comments
            if ";" in line:
                line = line.split(";", 1)[0].strip()

            if not line:
                continue

            # section start
            if line.startswith("[") and line.endswith("]"):
                section_name = line[1:-1].strip().lower()
                in_info = (section_name == "info")
                continue

            if not in_info:
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip().lower()
            value = strip_quotes(value)

            if key in {"name", "author", "displayname"}:
                info[key] = value

    return info


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

        info = parse_def_info(def_file)

        display_name = (
            info.get("name")
            or info.get("displayname")
            or def_file.stem.strip()
            or item.name.strip()
        )

        author = info.get("author") or DEFAULT_AUTHOR

        fighters.append({
            "display_name": display_name,
            "author": author,
            "folder_name": item.name,
            "def_file": def_file.name,
            "def_path": f"{item.name}/{def_file.name}",
        })

    return fighters


def main():
    data, wrapped = load_metadata()
    fighters_meta = data["fighters"] if wrapped else data

    native_fighters = discover_native_fighters()

    added = 0
    updated = 0
    already_present = 0

    for fighter in native_fighters:
        display_name = fighter["display_name"]

        if display_name in fighters_meta and isinstance(fighters_meta[display_name], dict):
            meta = fighters_meta[display_name]

            old_author = meta.get("author")
            if not old_author or str(old_author).strip() in {"", "Unknown", "Legacy Fighter"}:
                meta["author"] = fighter["author"]
                updated += 1
            else:
                already_present += 1

            meta.setdefault("archetype", DEFAULT_ARCHETYPE)
            meta.setdefault("power_index", DEFAULT_POWER_INDEX)
            meta.setdefault("source", "native")
            meta.setdefault("char_folder", fighter["folder_name"])
            meta.setdefault("def_file", fighter["def_file"])
            meta.setdefault("def_path", fighter["def_path"])
            continue

        fighters_meta[display_name] = {
            "author": fighter["author"],
            "archetype": DEFAULT_ARCHETYPE,
            "power_index": DEFAULT_POWER_INDEX,
            "source": "native",
            "char_folder": fighter["folder_name"],
            "def_file": fighter["def_file"],
            "def_path": fighter["def_path"],
        }
        added += 1

    save_metadata(data)

    print(f"Native char folders scanned: {len(native_fighters)}")
    print(f"Added metadata entries: {added}")
    print(f"Updated author from .def: {updated}")
    print(f"Already had good author: {already_present}")
    print(f"Saved: {META_PATH}")


if __name__ == "__main__":
    main()