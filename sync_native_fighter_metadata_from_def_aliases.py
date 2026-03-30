import json
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
    info = {}
    in_info = False

    with open(def_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue

            if ";" in line:
                line = line.split(";", 1)[0].strip()

            if not line:
                continue

            if line.startswith("[") and line.endswith("]"):
                section_name = line[1:-1].strip().lower()
                in_info = (section_name == "info")
                continue

            if not in_info or "=" not in line:
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
            "def_stem": def_file.stem,
            "def_path": f"{item.name}/{def_file.name}",
        })

    return fighters


def canonical_payload(fighter: dict):
    return {
        "author": fighter["author"],
        "archetype": DEFAULT_ARCHETYPE,
        "power_index": DEFAULT_POWER_INDEX,
        "source": "native",
        "char_folder": fighter["folder_name"],
        "def_file": fighter["def_file"],
        "def_path": fighter["def_path"],
    }


def alias_payload(canonical_name: str):
    return {
        "alias_to": canonical_name,
        "source": "native_alias",
    }


def ensure_main_entry(fighters_meta: dict, fighter: dict):
    name = fighter["display_name"]
    payload = canonical_payload(fighter)

    if name in fighters_meta and isinstance(fighters_meta[name], dict):
        meta = fighters_meta[name]

        old_author = meta.get("author")
        if not old_author or str(old_author).strip() in {"", "Unknown", "Legacy Fighter"}:
            meta["author"] = payload["author"]

        meta.setdefault("archetype", payload["archetype"])
        meta.setdefault("power_index", payload["power_index"])
        meta.setdefault("source", payload["source"])
        meta.setdefault("char_folder", payload["char_folder"])
        meta.setdefault("def_file", payload["def_file"])
        meta.setdefault("def_path", payload["def_path"])
        return False

    fighters_meta[name] = payload
    return True


def alias_candidates(fighter: dict):
    vals = [
        fighter["display_name"],
        fighter["folder_name"],
        fighter["def_stem"],
        fighter["display_name"].replace("_", " "),
        fighter["folder_name"].replace("_", " "),
        fighter["def_stem"].replace("_", " "),
    ]

    out = []
    seen = set()

    for v in vals:
        v = (v or "").strip()
        if not v:
            continue
        key = v.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(v)

    return out


def resolve_alias_chain(meta_dict: dict, name: str, max_hops: int = 5):
    current = name
    hops = 0

    while hops < max_hops:
        entry = meta_dict.get(current)
        if not isinstance(entry, dict):
            return current
        alias_to = entry.get("alias_to")
        if not alias_to:
            return current
        current = alias_to
        hops += 1

    return current


def ensure_aliases(fighters_meta: dict, fighter: dict):
    canonical_name = fighter["display_name"]
    added = 0

    for alias in alias_candidates(fighter):
        if alias == canonical_name:
            continue

        existing = fighters_meta.get(alias)

        if existing is None:
            fighters_meta[alias] = alias_payload(canonical_name)
            added += 1
            continue

        if isinstance(existing, dict) and existing.get("alias_to"):
            fighters_meta[alias]["alias_to"] = canonical_name
            continue

        # If a real entry already exists, leave it alone.
        # Real metadata beats alias metadata.
        continue

    return added


def main():
    data, wrapped = load_metadata()
    fighters_meta = data["fighters"] if wrapped else data

    native_fighters = discover_native_fighters()

    added_main = 0
    added_aliases = 0

    for fighter in native_fighters:
        if ensure_main_entry(fighters_meta, fighter):
            added_main += 1
        added_aliases += ensure_aliases(fighters_meta, fighter)

    save_metadata(data)

    print(f"Native char folders scanned: {len(native_fighters)}")
    print(f"Added/created main entries: {added_main}")
    print(f"Added alias entries: {added_aliases}")
    print(f"Saved: {META_PATH}")
    print("")
    print("Note:")
    print("- Main fighter entries include author/archetype/power_index.")
    print("- Alias entries look like: {\"alias_to\": \"Real Name\", \"source\": \"native_alias\"}")
    print("- Your overlay should resolve alias_to if you want full alias support.")


if __name__ == "__main__":
    main()