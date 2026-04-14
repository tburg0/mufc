from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parent
CHARS_DIR = ROOT / "chars"
META_FILE = ROOT / "fighters_metadata.json"
VARIANT_POLICY_FILE = ROOT / "variant_roster_policy.json"

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


def slugify_key(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9']+", "_", str(text or "").strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "unknown_fighter"


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


def load_variant_policy() -> Dict[str, Any]:
    if not VARIANT_POLICY_FILE.exists():
        return {}
    return load_json(VARIANT_POLICY_FILE, {})


def main() -> None:
    meta_wrap = load_json(META_FILE, {})
    fighters = metadata_entries(meta_wrap)
    variant_policy = load_variant_policy()

    updated_authors = 0
    filled_paths = 0
    created_entries = 0

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

        if not matches:
            display_name = str(info.get("displayname") or info.get("name") or folder.name).strip()
            existing_exact = fighters.get(folder.name)
            if isinstance(existing_exact, dict) and not existing_exact.get("char_folder"):
                existing_exact.update({
                    "author": def_author or existing_exact.get("author") or "Unknown",
                    "archetype": existing_exact.get("archetype") or "Roster",
                    "power_index": existing_exact.get("power_index") or 50,
                    "source": "native",
                    "select_entry": folder.name,
                    "char_folder": folder.name,
                    "def_file": def_file.name,
                    "def_path": f"{folder.name}/{def_file.name}",
                })
                existing_exact.pop("alias_to", None)
                matches.append((folder.name, existing_exact))

        if not matches:
            preferred_keys = [
                folder.name,
                display_name,
                slugify_key(display_name),
                slugify_key(folder.name),
                f"{folder.name}_Roster",
                f"{slugify_key(folder.name)}_roster",
            ]
            new_key = next((candidate for candidate in preferred_keys if candidate and candidate not in fighters), None)
            if new_key:
                fighters[new_key] = {
                    "author": def_author or "Unknown",
                    "archetype": "Roster",
                    "power_index": 50,
                    "source": "native",
                    "select_entry": folder.name,
                    "char_folder": folder.name,
                    "def_file": def_file.name,
                    "def_path": f"{folder.name}/{def_file.name}",
                }
                matches.append((new_key, fighters[new_key]))
                created_entries += 1

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

        policy = variant_policy.get(folder.name) if isinstance(variant_policy, dict) else None
        if isinstance(policy, dict):
            for variant in policy.get("variants", []):
                if not isinstance(variant, dict) or not variant.get("public"):
                    continue
                def_name = str(variant.get("def_file") or "").strip()
                key = str(variant.get("key") or "").strip()
                variant_path = folder / def_name
                if not def_name or not key or not variant_path.exists():
                    continue
                variant_info = parse_def_info(variant_path)
                entry = fighters.get(key)
                if not isinstance(entry, dict):
                    fighters[key] = {
                        "author": str(variant_info.get("author") or def_author or "Unknown").strip(),
                        "archetype": "Roster",
                        "power_index": 50,
                        "source": "native",
                        "select_entry": f"{folder.name}/{def_name}",
                        "char_folder": folder.name,
                        "def_file": def_name,
                        "def_path": f"{folder.name}/{def_name}",
                    }
                    created_entries += 1
                else:
                    if str(entry.get("author") or "").strip().lower() in PLACEHOLDER_AUTHORS and variant_info.get("author"):
                        entry["author"] = str(variant_info.get("author")).strip()
                        updated_authors += 1
                    entry["source"] = "native"
                    entry["select_entry"] = f"{folder.name}/{def_name}"
                    entry["char_folder"] = folder.name
                    entry["def_file"] = def_name
                    entry["def_path"] = f"{folder.name}/{def_name}"
                    entry.setdefault("archetype", "Roster")
                    entry.setdefault("power_index", 50)

    save_json(META_FILE, meta_wrap)
    print(json.dumps({
        "updated_authors": updated_authors,
        "filled_paths": filled_paths,
        "created_entries": created_entries,
        "saved": str(META_FILE),
    }, indent=2))


if __name__ == "__main__":
    main()
