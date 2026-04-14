from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parent
CHARS_DIR = ROOT / "chars"
META_FILE = ROOT / "fighters_metadata.json"

PLACEHOLDER_AUTHORS = {"", "unknown", "legacy fighter"}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def normalize(text: str) -> str:
    return str(text or "").strip().lower().replace("_", " ").replace("-", " ")


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1].strip()
    return value


def best_def(folder: Path) -> Optional[Path]:
    defs = sorted(folder.glob("*.def"))
    if not defs:
        return None
    folder_name = folder.name.lower()
    for candidate in defs:
        if candidate.stem.lower() == folder_name:
            return candidate
    return defs[0]


def parse_def_info(def_path: Path) -> Dict[str, str]:
    info: Dict[str, str] = {}
    in_info = False
    for raw in def_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if ";" in line:
            line = line.split(";", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            in_info = line[1:-1].strip().lower() == "info"
            continue
        if not in_info or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().lower()
        if key in {"name", "displayname", "author"}:
            info[key] = strip_quotes(value)
    return info


def metadata_entries(meta_wrap: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    if isinstance(meta_wrap, dict) and "fighters" in meta_wrap and isinstance(meta_wrap["fighters"], dict):
        return meta_wrap["fighters"]
    if isinstance(meta_wrap, dict):
        return meta_wrap
    raise ValueError("fighters_metadata.json must contain an object")


def main() -> None:
    meta_wrap = load_json(META_FILE, {})
    fighters = metadata_entries(meta_wrap)

    updated_authors = 0
    filled_paths = 0

    for folder in sorted(CHARS_DIR.iterdir(), key=lambda p: p.name.lower()):
        if not folder.is_dir():
            continue
        if folder.name.startswith(".") or folder.name.lower() in {"stages", "sound", "__pycache__"}:
            continue

        def_file = best_def(folder)
        if not def_file:
            continue

        info = parse_def_info(def_file)
        def_author = str(info.get("author") or "").strip()
        matches = []
        for name, entry in fighters.items():
            if not isinstance(entry, dict):
                continue
            entry_folder = str(entry.get("char_folder") or "").strip()
            select_entry = str(entry.get("select_entry") or "").replace("\\", "/").split("/", 1)[0].strip()
            if entry_folder.lower() == folder.name.lower() or select_entry.lower() == folder.name.lower():
                matches.append((name, entry))

        for name, entry in matches:
            current_author = str(entry.get("author") or "").strip()
            if def_author and current_author.lower() in PLACEHOLDER_AUTHORS:
                entry["author"] = def_author
                updated_authors += 1

            if not entry.get("char_folder"):
                entry["char_folder"] = folder.name
                filled_paths += 1
            if not entry.get("def_file"):
                entry["def_file"] = def_file.name
                filled_paths += 1
            if not entry.get("def_path"):
                entry["def_path"] = f"{folder.name}/{def_file.name}"
                filled_paths += 1

            if str(entry.get("source") or "").strip().lower() != "native_alias":
                entry.setdefault("source", "native")

    save_json(META_FILE, meta_wrap)
    print(json.dumps({
        "updated_authors": updated_authors,
        "filled_paths": filled_paths,
        "saved": str(META_FILE),
    }, indent=2))


if __name__ == "__main__":
    main()
