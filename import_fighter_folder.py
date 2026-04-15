from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
CHARS_DIR = ROOT / "chars"
SELECT_FILE = ROOT / "data" / "select.def"
META_FILE = ROOT / "fighters_metadata.json"

ENGINE_FILE_ALLOWLIST = {
    "common1.cns",
    "common.snd",
    "common.air",
}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1].strip()
    return value


def normalize_token(value: str) -> str:
    return "".join(ch.lower() for ch in str(value or "") if ch.isalnum())


def detect_source_folder(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Source path does not exist: {path}")
    if path.is_file():
        return path.parent
    return path


def find_def_files(folder: Path) -> List[Path]:
    return sorted(folder.glob("*.def"))


def best_def(folder: Path) -> Optional[Path]:
    defs = find_def_files(folder)
    if not defs:
        return None
    folder_name = folder.name.lower()
    for candidate in defs:
        if candidate.stem.lower() == folder_name:
            return candidate
    return defs[0]


def parse_def_sections(def_path: Path) -> Dict[str, Dict[str, str]]:
    sections: Dict[str, Dict[str, str]] = {}
    current: Optional[str] = None
    for raw in def_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if ";" in line:
            line = line.split(";", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1].strip().lower()
            sections.setdefault(current, {})
            continue
        if current and "=" in line:
            key, value = line.split("=", 1)
            sections[current][key.strip().lower()] = strip_quotes(value)
    return sections


def parse_def_info(def_path: Path) -> Dict[str, str]:
    sections = parse_def_sections(def_path)
    info = sections.get("info", {})
    return {
        "name": info.get("name", ""),
        "displayname": info.get("displayname", ""),
        "author": info.get("author", ""),
    }


def validate_package_files(folder: Path, def_path: Path) -> List[str]:
    sections = parse_def_sections(def_path)
    files = sections.get("files", {})
    issues: List[str] = []
    for _, raw_value in files.items():
        value = str(raw_value or "").strip().replace("\\", "/")
        if not value:
            continue
        if value.lower() in ENGINE_FILE_ALLOWLIST:
            continue
        candidate = folder / value
        if candidate.exists():
            continue
        if "/" not in value and (folder / Path(value).name).exists():
            continue
        issues.append(f"Missing referenced file: {value}")
    return issues


def metadata_entries(meta_wrap: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    if isinstance(meta_wrap, dict) and "fighters" in meta_wrap and isinstance(meta_wrap["fighters"], dict):
        return meta_wrap["fighters"]
    if isinstance(meta_wrap, dict):
        return meta_wrap
    raise ValueError("fighters_metadata.json must contain an object")


def parse_select_entries_with_lines() -> Tuple[List[str], int, int, List[str]]:
    lines = SELECT_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
    entries: List[str] = []
    in_characters = False
    start = -1
    end = len(lines)
    for index, raw in enumerate(lines):
        stripped = raw.strip()
        lower = stripped.lower()
        if lower == "[characters]":
            in_characters = True
            start = index
            continue
        if in_characters and stripped.startswith("[") and lower != "[characters]":
            end = index
            break
        if not in_characters:
            continue
        token = stripped.split(";", 1)[0].strip()
        if not token or token.lower().startswith("randomselect"):
            continue
        entry = token.split(",", 1)[0].strip().replace("\\", "/")
        if entry:
            entries.append(entry)
    return entries, start, end, lines


def select_insert_index(lines: List[str], start: int, end: int, new_entry: str) -> int:
    new_key = normalize_token(new_entry.split("/", 1)[0])
    last_randomselect = start
    for index in range(start + 1, end):
        stripped = lines[index].strip()
        lower = stripped.lower()
        if not stripped or stripped.startswith(";"):
            continue
        token = stripped.split(";", 1)[0].strip()
        if not token:
            continue
        if lower.startswith("randomselect"):
            last_randomselect = index
            continue
        entry = token.split(",", 1)[0].strip().replace("\\", "/")
        entry_key = normalize_token(entry.split("/", 1)[0])
        if entry_key and entry_key > new_key:
            return index
    return max(last_randomselect + 1, end)


def detect_duplicates(
    source_folder_name: str,
    display_name: str,
    select_entry: str,
    meta: Dict[str, Dict[str, Any]],
    select_entries: List[str],
) -> List[str]:
    issues: List[str] = []
    source_norm = normalize_token(source_folder_name)
    display_norm = normalize_token(display_name)
    select_norm = normalize_token(select_entry)

    if (CHARS_DIR / source_folder_name).exists():
        issues.append(f"chars/{source_folder_name} already exists")

    for entry in select_entries:
        token = entry.split("/", 1)[0]
        entry_norm = normalize_token(token)
        full_norm = normalize_token(entry)
        if source_norm and entry_norm == source_norm:
            issues.append(f"select.def already contains folder match: {entry}")
            break
        if select_norm and full_norm == select_norm:
            issues.append(f"select.def already contains exact entry: {entry}")
            break

    for key, value in meta.items():
        key_norm = normalize_token(key)
        folder_norm = normalize_token(str(value.get("char_folder") or ""))
        select_existing = str(value.get("select_entry") or value.get("def_path") or "").replace("\\", "/")
        select_existing_norm = normalize_token(select_existing)
        if display_norm and key_norm == display_norm:
            issues.append(f"metadata already has display-name match: {key}")
            break
        if source_norm and folder_norm == source_norm:
            issues.append(f"metadata already points at folder match: {key}")
            break
        if select_norm and select_existing_norm == select_norm:
            issues.append(f"metadata already points at select entry match: {key}")
            break

    return issues


def build_metadata_entry(folder_name: str, def_path: Path, info: Dict[str, str], select_entry: str) -> Dict[str, Any]:
    return {
        "author": info.get("author") or "Unknown",
        "archetype": "Roster",
        "power_index": 50,
        "source": "native",
        "select_entry": select_entry,
        "char_folder": folder_name,
        "def_file": def_path.name,
        "def_path": f"{folder_name}/{def_path.name}",
    }


def import_fighter(source_path: Path, apply_changes: bool) -> Dict[str, Any]:
    source_folder = detect_source_folder(source_path)
    def_path = best_def(source_folder)
    if not def_path:
        raise RuntimeError(f"No .def file found in {source_folder}")

    info = parse_def_info(def_path)
    display_name = info.get("displayname") or info.get("name") or source_folder.name
    folder_name = source_folder.name
    select_entry = folder_name if def_path.stem.lower() == folder_name.lower() else f"{folder_name}/{def_path.name}"

    validation_issues = validate_package_files(source_folder, def_path)
    meta_wrap = load_json(META_FILE, {})
    meta = metadata_entries(meta_wrap)
    select_entries, start, end, lines = parse_select_entries_with_lines()
    duplicate_issues = detect_duplicates(folder_name, display_name, select_entry, meta, select_entries)

    report: Dict[str, Any] = {
        "source_folder": str(source_folder),
        "folder_name": folder_name,
        "def_file": def_path.name,
        "display_name": display_name,
        "author": info.get("author") or "Unknown",
        "select_entry": select_entry,
        "target_folder": str(CHARS_DIR / folder_name),
        "validation_issues": validation_issues,
        "duplicate_issues": duplicate_issues,
        "would_import": not validation_issues and not duplicate_issues,
        "applied": False,
    }

    if validation_issues or duplicate_issues or not apply_changes:
        return report

    target_folder = CHARS_DIR / folder_name
    shutil.copytree(source_folder, target_folder)

    insert_at = select_insert_index(lines, start, end, select_entry)
    lines.insert(insert_at, f"{select_entry}, random")
    SELECT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    meta[display_name] = build_metadata_entry(folder_name, def_path, info, select_entry)
    save_json(META_FILE, meta_wrap)

    report["applied"] = True
    report["select_insert_line"] = insert_at + 1
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a native fighter folder into the live MUGEN roster.")
    parser.add_argument("source", help="Path to the incoming fighter folder")
    parser.add_argument("--apply", action="store_true", help="Actually copy files and update select.def/metadata")
    args = parser.parse_args()

    report = import_fighter(Path(args.source), apply_changes=args.apply)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["would_import"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
