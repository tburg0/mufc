from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
STATE_DIR = ROOT / "generated"
BLACKLIST_PATH = STATE_DIR / "load_blacklist.json"
RESULT_FILE = ROOT / "watchdog_result.json"
MATCH_CONTEXT = ROOT / "match_context.json"
MATCH_FILE = ROOT / "current_match.txt"
STAGE_FILE = ROOT / "current_stage.txt"

DEFAULT_TIMEOUT = 90
DEFAULT_POLL = 2.0


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


def load_blacklist() -> dict[str, Any]:
    return load_json(BLACKLIST_PATH, {"fighters": {}, "stages": {}, "history": []})


def append_history(bl: dict[str, Any], event: dict[str, Any]) -> None:
    hist = bl.setdefault("history", [])
    hist.append(event)
    # keep file bounded
    if len(hist) > 300:
        del hist[:-300]


def add_blacklist_entry(kind: str, key: str, reason: str, meta: dict[str, Any] | None = None) -> None:
    if not key:
        return
    bl = load_blacklist()
    bucket = bl.setdefault(kind, {})
    current = bucket.get(key, {"count": 0})
    current["count"] = int(current.get("count", 0)) + 1
    current["reason"] = reason
    current["updated_at"] = int(time.time())
    if meta:
        current.update(meta)
    bucket[key] = current
    append_history(bl, {
        "ts": int(time.time()),
        "type": kind,
        "key": key,
        "reason": reason,
        "meta": meta or {},
    })
    save_json(BLACKLIST_PATH, bl)


def read_match_details() -> dict[str, Any]:
    ctx = load_json(MATCH_CONTEXT, {})
    details: dict[str, Any] = {
        "fighter_1": ctx.get("fighter_1") or ctx.get("p1") or "",
        "fighter_2": ctx.get("fighter_2") or ctx.get("p2") or "",
        "runtime_p1": ctx.get("runtime_p1") or "",
        "runtime_p2": ctx.get("runtime_p2") or "",
        "stage": ctx.get("stage") or "",
    }
    if not details["fighter_1"] or not details["fighter_2"]:
        if MATCH_FILE.exists():
            txt = MATCH_FILE.read_text(encoding="utf-8", errors="ignore").strip()
            if " vs " in txt:
                p1, p2 = txt.split(" vs ", 1)
                details["fighter_1"] = details["fighter_1"] or p1.strip()
                details["fighter_2"] = details["fighter_2"] or p2.strip()
    if not details["stage"] and STAGE_FILE.exists():
        details["stage"] = STAGE_FILE.read_text(encoding="utf-8", errors="ignore").strip()
    return details


def terminate_process_tree(proc: subprocess.Popen[Any]) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            time.sleep(2)
            if proc.poll() is None:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: py watch_mugen_match.py <command...> [--timeout N]", file=sys.stderr)
        return 2

    args = sys.argv[1:]
    timeout = DEFAULT_TIMEOUT
    if "--timeout" in args:
        idx = args.index("--timeout")
        try:
            timeout = int(args[idx + 1])
        except Exception:
            print("Invalid --timeout value", file=sys.stderr)
            return 2
        del args[idx:idx + 2]

    details = read_match_details()
    start = time.time()
    RESULT_FILE.unlink(missing_ok=True)

    kwargs: dict[str, Any] = {}
    if os.name != "nt":
        kwargs["preexec_fn"] = os.setsid

    proc = subprocess.Popen(args, cwd=str(ROOT), **kwargs)
    timed_out = False

    while True:
        code = proc.poll()
        if code is not None:
            result = {
                "status": "ok" if code == 0 else "process_error",
                "exit_code": code,
                "elapsed_seconds": round(time.time() - start, 1),
                **details,
            }
            save_json(RESULT_FILE, result)
            print(json.dumps(result, indent=2))
            return 0 if code == 0 else 1

        elapsed = time.time() - start
        if elapsed >= timeout:
            timed_out = True
            break
        time.sleep(DEFAULT_POLL)

    if timed_out:
        terminate_process_tree(proc)
        result = {
            "status": "timeout_killed",
            "exit_code": -999,
            "elapsed_seconds": round(time.time() - start, 1),
            **details,
        }
        save_json(RESULT_FILE, result)
        print(json.dumps(result, indent=2))

        # blacklist likely bad load targets
        add_blacklist_entry(
            "fighters",
            str(details.get("fighter_1", "")).strip(),
            "Timed out while loading or running match",
            {"side": "p1", "other": details.get("fighter_2", "")},
        )
        add_blacklist_entry(
            "fighters",
            str(details.get("fighter_2", "")).strip(),
            "Timed out while loading or running match",
            {"side": "p2", "other": details.get("fighter_1", "")},
        )
        add_blacklist_entry(
            "stages",
            str(details.get("stage", "")).strip(),
            "Timed out while loading or running match",
            {"fighter_1": details.get("fighter_1", ""), "fighter_2": details.get("fighter_2", "")},
        )
        return 124

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
