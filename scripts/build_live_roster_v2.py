import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
FIGHTERS_METADATA_FILE = ROOT / "fighters_metadata.json"
PUBLISHED_ROSTER_FILE = ROOT / "generated" / "published_roster.json"
RUNTIME_MAPPING_FILE = ROOT / "generated" / "runtime_mapping.json"
CHARS_DIR = ROOT / "chars"
OUTPUT_FILE = ROOT / "live_roster.json"

VARIANT_HINTS = (
    "pots",
    "p.o.t.s",
    "shotoman",
    "sf6",
    "cvs",
    "final",
    "dark ",
    "evil ",
    "agent",
)


def load_json(path: Path, default: Any):
    if not path.exists():
        return default
    raw = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not raw:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        repaired = raw.replace("\r", "").strip()
        while repaired.endswith("}") and repaired.count("{") < repaired.count("}"):
            repaired = repaired[:-1].rstrip()
        while repaired.endswith("]") and repaired.count("[") < repaired.count("]"):
            repaired = repaired[:-1].rstrip()
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            return default


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_display_name(name: str) -> str:
    return normalize_spaces(name.replace("_", " ").replace("-", " - "))


def slug_base(text: str) -> str:
    s = text.casefold()
    s = s.replace("_", " ").replace("-", " ").replace(".", " ")
    s = re.sub(r"\b(pots|shotoman|sf6|cvs|final|agent|dark|evil)\b", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return normalize_spaces(s)


def title_case_loose(text: str) -> str:
    return " ".join(part[:1].upper() + part[1:] for part in text.split() if part)


def alias_score(name: str, source: str, author: str) -> Tuple:
    folded = (name or "").casefold()
    author_folded = (author or "").casefold()
    return (
        any(hint in folded for hint in VARIANT_HINTS),
        "_" in (name or ""),
        (name or "").isupper(),
        source != "native",
        author_folded.startswith("legacy fighter"),
        len(name or ""),
        folded,
    )


def derive_base_character(name: str, runtime: str, char_folder: str) -> str:
    candidates = [name, runtime, char_folder]
    best = None
    best_score = None
    for cand in candidates:
        if not cand:
            continue
        cleaned = clean_display_name(cand)
        base_key = slug_base(cleaned)
        if not base_key:
            continue
        score = alias_score(cleaned, "native", "")
        if best is None or score < best_score:
            best = title_case_loose(base_key)
            best_score = score
    return best or clean_display_name(name or runtime or char_folder or "Unknown")


def parse_select_entries() -> List[str]:
    select_file = ROOT / "data" / "select.def"
    if not select_file.exists():
        return []

    entries: List[str] = []
    in_characters = False
    for raw in select_file.read_text(encoding="utf-8", errors="ignore").splitlines():
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
        if not in_characters:
            continue
        if lower.startswith("randomselect"):
            continue
        token = line.split(",", 1)[0].strip().replace("\\", "/")
        if token:
            entries.append(token)
    return entries


def resolve_runtime_to_folder(runtime: str) -> Optional[str]:
    token = (runtime or "").replace("\\", "/").strip()
    if not token:
        return None
    folder = token.split("/", 1)[0].strip()
    if folder and (CHARS_DIR / folder).is_dir():
        return folder
    if (CHARS_DIR / token).is_dir():
        return token
    return None


def scan_native_folders() -> List[str]:
    if not CHARS_DIR.exists():
        return []
    found: List[str] = []
    for child in sorted(CHARS_DIR.iterdir(), key=lambda p: p.name.casefold()):
        if not child.is_dir():
            continue
        if child.name.startswith(".") or child.name.casefold() in {"stages", "sound"}:
            continue
        if child.name.casefold().startswith("custom_"):
            continue
        if list(child.glob("*.def")):
            found.append(child.name)
    return found


def build_native_candidates() -> List[Dict[str, Any]]:
    metadata = load_json(FIGHTERS_METADATA_FILE, {})
    fighters = metadata.get("fighters", {}) if isinstance(metadata, dict) else {}
    candidates: List[Dict[str, Any]] = []

    if isinstance(fighters, dict):
        for meta_name, meta in fighters.items():
            if not isinstance(meta, dict):
                continue
            runtime = str(meta.get("select_entry") or meta_name).strip()
            char_folder = str(meta.get("char_folder") or resolve_runtime_to_folder(runtime) or "").strip()
            def_path = str(meta.get("def_path") or (f"{char_folder}/{meta.get('def_file')}" if char_folder and meta.get("def_file") else "")).strip()
            display_name = clean_display_name(meta_name)
            candidates.append({
                "id": display_name,
                "name": display_name,
                "runtime": runtime,
                "source": "native",
                "selectable_as_base": True,
                "char_folder": char_folder or None,
                "def_path": def_path or None,
                "author": meta.get("author"),
                "archetype": meta.get("archetype"),
                "power_index": meta.get("power_index"),
                "fighter_id": None,
                "from_metadata": True,
            })

    metadata_runtimes = {str(c["runtime"]).casefold() for c in candidates if c.get("runtime")}
    for entry in parse_select_entries():
        if entry.casefold() in metadata_runtimes:
            continue
        folder = resolve_runtime_to_folder(entry)
        candidates.append({
            "id": clean_display_name(entry),
            "name": clean_display_name(entry),
            "runtime": entry,
            "source": "native",
            "selectable_as_base": True,
            "char_folder": folder,
            "def_path": f"{folder}/{Path(entry).name}.def" if folder else None,
            "author": None,
            "archetype": None,
            "power_index": None,
            "fighter_id": None,
            "from_metadata": False,
        })

    represented_folders = {str(c.get("char_folder") or "").casefold() for c in candidates if c.get("char_folder")}
    for folder in scan_native_folders():
        if folder.casefold() in represented_folders:
            continue
        candidates.append({
            "id": clean_display_name(folder),
            "name": clean_display_name(folder),
            "runtime": folder,
            "source": "native",
            "selectable_as_base": True,
            "char_folder": folder,
            "def_path": f"{folder}/{folder}.def",
            "author": None,
            "archetype": None,
            "power_index": None,
            "fighter_id": None,
            "from_metadata": False,
        })

    return candidates


def build_submitted_candidates() -> List[Dict[str, Any]]:
    roster_blob = load_json(PUBLISHED_ROSTER_FILE, {"fighters": []})
    runtime_mapping = load_json(RUNTIME_MAPPING_FILE, {})
    fighters = roster_blob.get("fighters", []) if isinstance(roster_blob, dict) else []
    if not isinstance(fighters, list):
        return []

    out: List[Dict[str, Any]] = []
    for fighter in fighters:
        if not isinstance(fighter, dict) or not fighter.get("live"):
            continue
        display_name = str(fighter.get("name") or "").strip()
        if not display_name:
            continue
        mapping = runtime_mapping.get(display_name) or {}
        runtime = str(mapping.get("runtime_character") or "").strip()
        if not runtime:
            continue
        folder = resolve_runtime_to_folder(runtime)
        if not folder:
            continue
        out.append({
            "id": display_name,
            "name": clean_display_name(display_name),
            "runtime": runtime,
            "source": "submitted",
            "selectable_as_base": False,
            "char_folder": folder,
            "def_path": None,
            "author": fighter.get("author"),
            "archetype": fighter.get("archetype"),
            "power_index": fighter.get("power_index"),
            "fighter_id": fighter.get("fighter_id"),
            "from_metadata": False,
        })
    return out


def dedupe_native_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for c in candidates:
        key = str(c.get("char_folder") or c.get("def_path") or c.get("runtime") or c.get("name") or "").casefold()
        if not key:
            continue
        grouped.setdefault(key, []).append(c)

    deduped: List[Dict[str, Any]] = []
    for group in grouped.values():
        winner = min(
            group,
            key=lambda c: alias_score(str(c.get("name") or ""), str(c.get("source") or ""), str(c.get("author") or ""))
        )
        winner = dict(winner)
        winner["base_character"] = derive_base_character(
            str(winner.get("name") or ""),
            str(winner.get("runtime") or ""),
            str(winner.get("char_folder") or ""),
        )
        winner["is_variant"] = len(group) > 1
        winner["variants"] = [
            {
                "name": clean_display_name(str(item.get("name") or "")),
                "runtime": item.get("runtime"),
                "author": item.get("author"),
                "source": item.get("source"),
                "char_folder": item.get("char_folder"),
                "def_path": item.get("def_path"),
            }
            for item in sorted(group, key=lambda x: alias_score(str(x.get("name") or ""), str(x.get("source") or ""), str(x.get("author") or "")))
        ]
        deduped.append(winner)

    deduped.sort(key=lambda c: str(c.get("name") or "").casefold())
    return deduped


def build_grouped_base_fighters(base_fighters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for fighter in base_fighters:
        base = str(fighter.get("base_character") or fighter.get("name") or "").strip()
        if base:
            grouped.setdefault(base, []).append(fighter)

    results: List[Dict[str, Any]] = []
    for base, members in grouped.items():
        ordered = sorted(members, key=lambda c: alias_score(str(c.get("name") or ""), str(c.get("source") or ""), str(c.get("author") or "")))
        primary = ordered[0]
        results.append({
            "base_character": base,
            "primary_id": primary.get("id"),
            "primary_name": primary.get("name"),
            "members": [
                {
                    "id": m.get("id"),
                    "name": m.get("name"),
                    "runtime": m.get("runtime"),
                    "source": m.get("source"),
                    "is_variant": m.get("is_variant", False),
                    "char_folder": m.get("char_folder"),
                    "def_path": m.get("def_path"),
                    "author": m.get("author"),
                }
                for m in ordered
            ],
        })
    results.sort(key=lambda x: str(x["base_character"]).casefold())
    return results


def main() -> None:
    native_candidates = build_native_candidates()
    submitted_candidates = build_submitted_candidates()
    deduped_native = dedupe_native_candidates(native_candidates)

    for fighter in submitted_candidates:
        fighter["base_character"] = clean_display_name(str(fighter.get("name") or ""))
        fighter["is_variant"] = False
        fighter["variants"] = []

    live_roster = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "native_candidates_raw": len(native_candidates),
            "native_unique": len(deduped_native),
            "submitted": len(submitted_candidates),
            "total_live": len(deduped_native) + len(submitted_candidates),
            "base_selectable": len(deduped_native),
            "native_variant_groups": sum(1 for f in deduped_native if f.get("is_variant")),
        },
        "base_fighters": deduped_native,
        "submitted_fighters": sorted(submitted_candidates, key=lambda c: str(c.get("name") or "").casefold()),
        "base_fighter_groups": build_grouped_base_fighters(deduped_native),
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(live_roster, f, indent=2, ensure_ascii=False)

    print(f"Wrote {OUTPUT_FILE}")
    print(json.dumps(live_roster["counts"], indent=2))


if __name__ == "__main__":
    main()
