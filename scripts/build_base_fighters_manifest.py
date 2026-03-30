import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META_PATH = ROOT / "fighters_metadata.json"
OUT_PATH = ROOT / "public" / "base_fighters.json"

DEFAULT_CUSTOMIZABLE = True


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    meta = load_json(META_PATH, {"fighters": {}})
    fighters = meta.get("fighters", {})

    base_fighters = []

    for display_name, data in fighters.items():
        if not isinstance(data, dict):
            continue

        # only expose native fighters by default
        if data.get("source") != "native":
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

    base_fighters.sort(key=lambda x: x["display_name"].lower())

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(base_fighters, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(base_fighters)} base fighters to {OUT_PATH}")


if __name__ == "__main__":
    main()