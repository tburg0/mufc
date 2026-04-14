from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent
CHARS_DIR = ROOT / "chars"
SELECT_FILE = ROOT / "data" / "select.def"
META_FILE = ROOT / "fighters_metadata.json"
PUBLISHED_ROSTER_FILE = ROOT / "generated" / "published_roster.json"
RUNTIME_MAPPING_FILE = ROOT / "generated" / "runtime_mapping.json"
BLACKLIST_FILE = ROOT / "generated" / "load_blacklist.json"
REPORT_JSON = ROOT / "generated" / "chars_audit_report.json"
REPORT_TXT = ROOT / "generated" / "chars_audit_report.txt"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def parse_select_entries() -> List[str]:
    if not SELECT_FILE.exists():
        return []

    entries: List[str] = []
    in_characters = False
    for raw in SELECT_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        lower = line.lower()
        if lower == "[characters]":
            in_characters = True
            continue
        if line.startswith("[") and lower != "[characters]":
            in_characters = False
            continue
        if not in_characters or lower.startswith("randomselect"):
            continue
        token = line.split(",", 1)[0].strip().replace("\\", "/")
        if token:
            entries.append(token)
    return entries


def resolve_select_entry(entry: str) -> Optional[Path]:
    token = entry.replace("\\", "/").strip()
    if not token:
        return None
    folder = token.split("/", 1)[0].strip()
    if folder and (CHARS_DIR / folder).is_dir():
        return CHARS_DIR / folder
    if (CHARS_DIR / token).is_dir():
        return CHARS_DIR / token
    return None


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1].strip()
    return value


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


def best_def(folder: Path) -> Optional[Path]:
    defs = sorted(folder.glob("*.def"))
    if not defs:
        return None
    folder_name = folder.name.lower()
    for candidate in defs:
        if candidate.stem.lower() == folder_name:
            return candidate
    return defs[0]


def build_metadata_indexes(meta_wrap: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, List[str]]]:
    fighters = meta_wrap.get("fighters", {}) if isinstance(meta_wrap, dict) and "fighters" in meta_wrap else meta_wrap
    by_folder: Dict[str, List[str]] = {}
    if isinstance(fighters, dict):
        for key, value in fighters.items():
            if not isinstance(value, dict):
                continue
            folder = str(value.get("char_folder") or "").strip()
            if folder:
                by_folder.setdefault(folder.lower(), []).append(key)
    return fighters if isinstance(fighters, dict) else {}, by_folder


def audit() -> Dict[str, Any]:
    meta_wrap = load_json(META_FILE, {})
    meta, meta_by_folder = build_metadata_indexes(meta_wrap)
    roster = load_json(PUBLISHED_ROSTER_FILE, {"fighters": []})
    mapping = load_json(RUNTIME_MAPPING_FILE, {})
    blacklist = load_json(BLACKLIST_FILE, {"fighters": {}, "stages": {}, "history": []})

    report: Dict[str, Any] = {
        "scanned_at": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
        "counts": {},
        "broken_select_entries": [],
        "folders_missing_def": [],
        "folders_multiple_defs": [],
        "metadata_missing_for_folder": [],
        "metadata_placeholder_author_with_real_def_author": [],
        "metadata_duplicate_folder_entries": [],
        "published_custom_runtime_missing": [],
        "blacklisted_fighters": [],
    }

    broken_select_entries = []
    for entry in parse_select_entries():
        if resolve_select_entry(entry) is None:
            broken_select_entries.append(entry)
    report["broken_select_entries"] = broken_select_entries

    folders_missing_def = []
    folders_multiple_defs = []
    metadata_missing_for_folder = []
    metadata_placeholder_author_with_real_def_author = []
    metadata_duplicate_folder_entries = []

    for folder in sorted(CHARS_DIR.iterdir(), key=lambda p: p.name.lower()):
        if not folder.is_dir():
            continue
        if folder.name.startswith(".") or folder.name.lower() in {"sound", "stages", "__pycache__"}:
            continue

        defs = sorted(folder.glob("*.def"))
        if not defs:
            folders_missing_def.append(folder.name)
            continue
        if len(defs) > 1:
            folders_multiple_defs.append({
                "folder": folder.name,
                "defs": [item.name for item in defs],
            })

        primary = best_def(folder)
        info = parse_def_info(primary) if primary else {}
        def_author = str(info.get("author") or "").strip()
        names = meta_by_folder.get(folder.name.lower(), [])
        if not names:
            metadata_missing_for_folder.append({
                "folder": folder.name,
                "def_file": primary.name if primary else None,
                "def_name": info.get("displayname") or info.get("name"),
                "def_author": def_author or None,
            })
            continue

        if len(names) > 1:
            metadata_duplicate_folder_entries.append({
                "folder": folder.name,
                "entries": names,
            })

        for name in names:
            entry = meta.get(name, {})
            author = str(entry.get("author") or "").strip()
            if def_author and author.lower() in {"", "unknown", "legacy fighter"}:
                metadata_placeholder_author_with_real_def_author.append({
                    "folder": folder.name,
                    "metadata_name": name,
                    "metadata_author": author,
                    "def_author": def_author,
                    "def_file": primary.name if primary else None,
                })

    report["folders_missing_def"] = folders_missing_def
    report["folders_multiple_defs"] = folders_multiple_defs
    report["metadata_missing_for_folder"] = metadata_missing_for_folder
    report["metadata_placeholder_author_with_real_def_author"] = metadata_placeholder_author_with_real_def_author
    report["metadata_duplicate_folder_entries"] = metadata_duplicate_folder_entries

    published_missing = []
    for fighter in roster.get("fighters", []):
        if not isinstance(fighter, dict) or not fighter.get("live"):
            continue
        name = str(fighter.get("name") or "").strip()
        entry = mapping.get(name) or {}
        runtime = str(entry.get("runtime_character") or "").replace("\\", "/").strip()
        folder = runtime.split("/", 1)[0].strip()
        runtime_def = CHARS_DIR / folder / f"{folder}.def"
        if not runtime or not runtime_def.exists():
            published_missing.append({
                "name": name,
                "fighter_id": fighter.get("fighter_id"),
                "runtime_character": runtime,
                "expected_def": str(runtime_def),
            })
    report["published_custom_runtime_missing"] = published_missing

    report["blacklisted_fighters"] = sorted([
        {"name": key, **(value if isinstance(value, dict) else {})}
        for key, value in (blacklist.get("fighters") or {}).items()
    ], key=lambda item: (-int(item.get("count", 0)), item["name"].lower()))

    report["counts"] = {
        "chars_folders": len([p for p in CHARS_DIR.iterdir() if p.is_dir()]) if CHARS_DIR.exists() else 0,
        "broken_select_entries": len(report["broken_select_entries"]),
        "folders_missing_def": len(report["folders_missing_def"]),
        "folders_multiple_defs": len(report["folders_multiple_defs"]),
        "metadata_missing_for_folder": len(report["metadata_missing_for_folder"]),
        "metadata_placeholder_author_with_real_def_author": len(report["metadata_placeholder_author_with_real_def_author"]),
        "metadata_duplicate_folder_entries": len(report["metadata_duplicate_folder_entries"]),
        "published_custom_runtime_missing": len(report["published_custom_runtime_missing"]),
        "blacklisted_fighters": len(report["blacklisted_fighters"]),
    }
    return report


def write_report(report: Dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "=== CHARS AUDIT REPORT ===",
        f"Scanned: {report.get('scanned_at')}",
        "",
        "Counts:",
    ]
    for key, value in report.get("counts", {}).items():
        lines.append(f"- {key}: {value}")

    def add_section(title: str, items: List[Any], limit: int = 20) -> None:
        lines.append("")
        lines.append(title)
        if not items:
            lines.append("- none")
            return
        for item in items[:limit]:
            if isinstance(item, dict):
                lines.append(f"- {json.dumps(item, ensure_ascii=False)}")
            else:
                lines.append(f"- {item}")
        if len(items) > limit:
            lines.append(f"- ... and {len(items) - limit} more")

    add_section("Broken select.def entries", report["broken_select_entries"])
    add_section("Folders missing .def", report["folders_missing_def"])
    add_section("Folders with multiple .def files", report["folders_multiple_defs"])
    add_section("Metadata missing for folder", report["metadata_missing_for_folder"])
    add_section("Placeholder metadata author even though .def has real author", report["metadata_placeholder_author_with_real_def_author"])
    add_section("Duplicate metadata entries pointing to same folder", report["metadata_duplicate_folder_entries"])
    add_section("Published custom fighters with missing runtime .def", report["published_custom_runtime_missing"])
    add_section("Blacklisted fighters", report["blacklisted_fighters"])

    REPORT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = audit()
    write_report(report)
    print(json.dumps(report["counts"], indent=2))
    print(f"Saved JSON: {REPORT_JSON}")
    print(f"Saved TXT:  {REPORT_TXT}")


if __name__ == "__main__":
    main()
