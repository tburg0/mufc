import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META_PATH = ROOT / "fighters_metadata.json"
OUT_PATH = ROOT / "public" / "base_fighters.json"
CHARS_DIR = ROOT / "chars"
SELECT_PATH = ROOT / "data" / "select.def"

DEFAULT_CUSTOMIZABLE = True


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_select_def(select_path: Path) -> set[str]:
    """
    Returns a set of normalized select.def entries from [Characters].
    We use this as an optional 'live roster' signal.
    """
    if not select_path.exists():
        return set()

    in_characters = False
    entries = set()

    with select_path.open("r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()

            if not line:
                continue

            lower = line.lower()

            if lower.startswith("[characters]"):
                in_characters = True
                continue

            if lower.startswith("[") and lower != "[characters]":
                if in_characters:
                    break
                continue

            if not in_characters:
                continue

            if ";" in line:
                line = line.split(";", 1)[0].strip()

            if not line:
                continue

            first = line.split(",", 1)[0].strip()
            if not first:
                continue

            entries.add(normalize(first))

    return entries


def normalize(value: str) -> str:
    return (
        (value or "")
        .strip()
        .lower()
        .replace("\\", "/")
        .replace("_", " ")
        .replace("-", " ")
    )


def is_live_cloneable(data: dict, select_entries: set[str]) -> tuple[bool, str]:
    """
    Validate that the metadata entry points to a current live fighter source.
    """
    char_folder = (data.get("char_folder") or "").strip()
    def_file = (data.get("def_file") or "").strip()
    def_path = (data.get("def_path") or "").strip()

    if not char_folder:
        return False, "missing char_folder"

    folder_path = CHARS_DIR / char_folder
    if not folder_path.exists() or not folder_path.is_dir():
        return False, "char_folder missing on disk"

    if def_file:
        candidate_def = folder_path / def_file
        if not candidate_def.exists():
            return False, "def_file missing on disk"
    elif def_path:
        candidate_def = CHARS_DIR / def_path
        if not candidate_def.exists():
            return False, "def_path missing on disk"
    else:
        defs = list(folder_path.glob("*.def"))
        if not defs:
            return False, "no .def found in folder"

    # Optional live-roster check against select.def
    # We accept either the folder, def_path, or def stem appearing there.
    if select_entries:
        folder_norm = normalize(char_folder)
        def_path_norm = normalize(def_path)
        def_stem_norm = normalize(Path(def_file).stem if def_file else "")

        if not (
            folder_norm in select_entries
            or def_path_norm in select_entries
            or def_stem_norm in select_entries
        ):
            return False, "not present in select.def"

    return True, "ok"


def main():
    meta = load_json(META_PATH, {"fighters": {}})
    fighters = meta.get("fighters", {})
    select_entries = parse_select_def(SELECT_PATH)

    base_fighters = []
    rejected = []

    for display_name, data in fighters.items():
        if not isinstance(data, dict):
            continue

        # only expose native fighters by default
        if data.get("source") != "native":
            continue

        # page.tsx already filters customizable !== false, but keep that here too
        if data.get("customizable", DEFAULT_CUSTOMIZABLE) is False:
            rejected.append((display_name, "customizable false"))
            continue

        ok, reason = is_live_cloneable(data, select_entries)
        if not ok:
            rejected.append((display_name, reason))
            continue

        base_fighters.append({
            "id": display_name,
            "display_name": display_name,
            "archetype": data.get("archetype", "unknown"),
            "author": data.get("author", "Unknown"),
            "customizable": data.get("customizable", DEFAULT_CUSTOMIZABLE),
            "char_folder": data.get("char_folder", ""),
            "def_file": data.get("def_file", ""),
            "def_path": data.get("def_path", "")
        })

    # Deduplicate by char_folder + def_file, keeping the best display_name
    deduped = {}
    for fighter in base_fighters:
        key = (
            fighter.get("char_folder", "").strip().lower(),
            fighter.get("def_file", "").strip().lower()
        )
        existing = deduped.get(key)

        if existing is None:
            deduped[key] = fighter
            continue

        # Prefer non-unknown archetype, then shorter/cleaner display name
        existing_score = (
            0 if existing["archetype"] == "unknown" else 1,
            -len(existing["display_name"])
        )
        current_score = (
            0 if fighter["archetype"] == "unknown" else 1,
            -len(fighter["display_name"])
        )

        if current_score > existing_score:
            deduped[key] = fighter

    final_list = sorted(deduped.values(), key=lambda x: x["display_name"].lower())

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(final_list)} live cloneable base fighters to {OUT_PATH}")
    print(f"Rejected {len(rejected)} entries")
    for name, reason in rejected[:50]:
        print(f"  - {name}: {reason}")


if __name__ == "__main__":
    main()