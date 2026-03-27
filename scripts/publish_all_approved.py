from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPROVED_DIR = ROOT / "submissions" / "approved"
PUBLISHED_ROSTER_PATH = ROOT / "generated" / "published_roster.json"
PUBLISH_SCRIPT = ROOT / "scripts" / "publish_fighter.py"


def load_published_ids() -> set[str]:
    if not PUBLISHED_ROSTER_PATH.exists():
        return set()
    try:
        data = json.loads(PUBLISHED_ROSTER_PATH.read_text(encoding="utf-8"))
    except Exception:
        return set()

    ids: set[str] = set()
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                ids.add(item.strip().lower())
            elif isinstance(item, dict):
                fighter_id = str(
                    item.get("id")
                    or item.get("fighter_id")
                    or item.get("slug")
                    or item.get("name")
                    or ""
                ).strip().lower()
                if fighter_id:
                    ids.add(fighter_id)
    elif isinstance(data, dict):
        for key, value in data.items():
            key_s = str(key).strip().lower()
            if key_s:
                ids.add(key_s)
            if isinstance(value, dict):
                fighter_id = str(
                    value.get("id")
                    or value.get("fighter_id")
                    or value.get("slug")
                    or value.get("name")
                    or ""
                ).strip().lower()
                if fighter_id:
                    ids.add(fighter_id)
    return ids


def discover_approved_ids() -> list[str]:
    if not APPROVED_DIR.exists():
        return []
    ids: list[str] = []
    for path in sorted(APPROVED_DIR.glob("*.json")):
        fighter_id = path.stem.strip().lower()
        if fighter_id:
            ids.append(fighter_id)
    return ids


def publish_missing() -> int:
    if not PUBLISH_SCRIPT.exists():
        print(f"[ERROR] Missing publish script: {PUBLISH_SCRIPT}")
        return 1

    approved_ids = discover_approved_ids()
    if not approved_ids:
        print("No approved fighters found.")
        return 0

    published_ids = load_published_ids()
    missing_ids = [fighter_id for fighter_id in approved_ids if fighter_id not in published_ids]

    print(f"Approved fighters: {len(approved_ids)}")
    print(f"Already live: {len(published_ids)}")
    print(f"Missing from live roster: {len(missing_ids)}")

    failures = 0
    for fighter_id in missing_ids:
        print(f"\n[PUBLISH] {fighter_id}")
        result = subprocess.run([sys.executable, str(PUBLISH_SCRIPT), fighter_id], cwd=str(ROOT))
        if result.returncode != 0:
            failures += 1
            print(f"[FAILED] {fighter_id} (exit code {result.returncode})")
        else:
            print(f"[OK] {fighter_id}")

    if failures:
        print(f"\nCompleted with {failures} failure(s).")
        return 1

    print("\nAll missing approved fighters were published successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(publish_missing())
