from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent
META_FILE = ROOT / "fighters_metadata.json"
VARIANT_POLICY_FILE = ROOT / "variant_roster_policy.json"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def fighters_dict(meta_wrap: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    if isinstance(meta_wrap, dict) and "fighters" in meta_wrap and isinstance(meta_wrap["fighters"], dict):
        return meta_wrap["fighters"]
    if isinstance(meta_wrap, dict):
        return meta_wrap
    raise ValueError("fighters_metadata.json must contain an object")


def build_by_folder(fighters: Dict[str, Dict[str, Any]]) -> Dict[str, List[Tuple[str, Dict[str, Any]]]]:
    by_folder: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
    for key, entry in fighters.items():
        if not isinstance(entry, dict):
            continue
        folder = str(entry.get("char_folder") or "").strip()
        if not folder:
            continue
        by_folder.setdefault(folder, []).append((key, entry))
    return by_folder


def score_key(key: str, entry: Dict[str, Any], folder: str, preferred_key: str | None = None) -> int:
    score = 0
    if preferred_key and key == preferred_key:
        score += 100
    if key == folder:
        score += 40
    if key.lower() == folder.lower():
        score += 30
    if str(entry.get("select_entry") or "").split("/", 1)[0].strip() == folder:
        score += 20
    if not key.startswith("custom_"):
        score += 10
    if entry.get("customizable"):
        score += 12
    archetype = str(entry.get("archetype") or "").strip().lower()
    if archetype and archetype not in {"roster", "unknown"}:
        score += 12
    try:
        if float(entry.get("power_index", 50)) != 50:
            score += 10
    except Exception:
        pass
    if " " in key:
        score += 8
    if "_" not in key:
        score += 4
    if "-" not in key:
        score += 2
    score -= len(key)
    return score


def alias_entry(target: str) -> Dict[str, Any]:
    return {
        "alias_to": target,
        "source": "native_alias",
    }


def main() -> None:
    meta_wrap = load_json(META_FILE, {})
    fighters = fighters_dict(meta_wrap)
    variant_policy = load_json(VARIANT_POLICY_FILE, {})

    converted = 0
    preserved_variant_entries = 0

    for folder, items in sorted(build_by_folder(fighters).items()):
        groups: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
        for key, entry in items:
            signature = str(entry.get("def_path") or entry.get("def_file") or entry.get("select_entry") or key)
            groups.setdefault(signature, []).append((key, entry))

        policy = variant_policy.get(folder, {}) if isinstance(variant_policy, dict) else {}
        preferred_by_signature: Dict[str, str] = {}
        if isinstance(policy, dict):
            for variant in policy.get("variants", []):
                if not isinstance(variant, dict):
                    continue
                def_file = str(variant.get("def_file") or "").strip()
                key = str(variant.get("key") or "").strip()
                if def_file and key:
                    preferred_by_signature[f"{folder}/{def_file}"] = key
                    preferred_by_signature[def_file] = key

        for signature, group in groups.items():
            if len(group) <= 1:
                continue

            preferred_key = preferred_by_signature.get(signature)
            canonical_key, canonical_entry = max(
                group,
                key=lambda item: score_key(item[0], item[1], folder, preferred_key),
            )

            for key, entry in group:
                if key == canonical_key:
                    continue
                fighters[key] = alias_entry(canonical_key)
                converted += 1

            if preferred_key and canonical_key == preferred_key:
                preserved_variant_entries += 1

    swapped_custom_canonicals = 0
    alias_items = [
        (key, entry) for key, entry in fighters.items()
        if isinstance(entry, dict) and entry.get("alias_to")
    ]
    for alias_key, alias_meta in alias_items:
        target_key = str(alias_meta.get("alias_to") or "").strip()
        target_entry = fighters.get(target_key)
        if (
            not target_key.startswith("custom_")
            or alias_key.startswith("custom_")
            or not isinstance(target_entry, dict)
            or target_entry.get("alias_to")
        ):
            continue
        if str(target_entry.get("char_folder") or "").strip() != target_key:
            continue
        promoted = dict(target_entry)
        fighters[alias_key] = promoted
        fighters[target_key] = alias_entry(alias_key)
        swapped_custom_canonicals += 1

    save_json(META_FILE, meta_wrap)
    print(json.dumps({
        "converted_to_aliases": converted,
        "policy_preferred_groups_preserved": preserved_variant_entries,
        "swapped_custom_canonicals": swapped_custom_canonicals,
        "saved": str(META_FILE),
    }, indent=2))


if __name__ == "__main__":
    main()
