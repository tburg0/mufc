from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
BLACKLIST_PATH = ROOT / "generated" / "load_blacklist.json"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: py mugen_blacklist_utils.py [show|clear|unblacklist-fighter NAME|unblacklist-stage NAME]")
        return 2
    cmd = sys.argv[1]
    data = load_json(BLACKLIST_PATH, {"fighters": {}, "stages": {}, "history": []})

    if cmd == "show":
        print(json.dumps(data, indent=2))
        return 0
    if cmd == "clear":
        save_json(BLACKLIST_PATH, {"fighters": {}, "stages": {}, "history": []})
        print("Cleared blacklist")
        return 0
    if cmd == "unblacklist-fighter" and len(sys.argv) >= 3:
        data.setdefault("fighters", {}).pop(sys.argv[2], None)
        save_json(BLACKLIST_PATH, data)
        print(f"Removed fighter: {sys.argv[2]}")
        return 0
    if cmd == "unblacklist-stage" and len(sys.argv) >= 3:
        data.setdefault("stages", {}).pop(sys.argv[2], None)
        save_json(BLACKLIST_PATH, data)
        print(f"Removed stage: {sys.argv[2]}")
        return 0

    print("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
