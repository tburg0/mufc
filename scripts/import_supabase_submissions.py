import json
import subprocess
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = ROOT / "submissions" / "drafts"
APPROVED_DIR = ROOT / "submissions" / "approved"
REJECTED_DIR = ROOT / "submissions" / "rejected"

DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
APPROVED_DIR.mkdir(parents=True, exist_ok=True)
REJECTED_DIR.mkdir(parents=True, exist_ok=True)

SUPABASE_URL = "https://kolzcksldqxlrfvvynkd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtvbHpja3NsZHF4bHJmdnZ5bmtkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDIxOTE5MCwiZXhwIjoyMDg5Nzk1MTkwfQ.H0syho5RGjmTxdxHplaBD_p7Y48uDRcM_TEAP4Rby_k"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

TABLE = "fighter_submissions"

REQUIRED_TOP_LEVEL = [
    "fighter_id",
    "identity",
    "classification",
    "appearance",
    "stats",
    "ai_profile",
    "moveset",
]

REQUIRED_STATS = [
    "power",
    "speed",
    "defense",
    "grapple",
    "strike",
    "air",
    "stamina",
    "recovery",
]


def fetch_submissions():
    url = f"{SUPABASE_URL}/rest/v1/{TABLE}?status=eq.submitted&select=*"
    res = requests.get(url, headers=HEADERS, timeout=30)
    res.raise_for_status()
    return res.json()


def patch_row(row_id: int, payload: dict):
    url = f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.{row_id}"
    res = requests.patch(
        url,
        headers={**HEADERS, "Prefer": "return=minimal"},
        json=payload,
        timeout=30,
    )
    res.raise_for_status()


def save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_script(script_rel_path: str, fighter_id: str):
    return subprocess.run(
        ["py", script_rel_path, fighter_id],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def extract_failure_reason(result: subprocess.CompletedProcess[str]) -> str:
    combined = "\n".join(part for part in [result.stdout, result.stderr] if part).strip()
    if not combined:
        return f"Pipeline failed with exit code {result.returncode}"

    lines = [line.strip() for line in combined.splitlines() if line.strip()]
    for line in reversed(lines):
        if "Traceback" in line:
            continue
        return line[:300]
    return combined[:300]


def validate_fighter(fighter: dict):
    for key in REQUIRED_TOP_LEVEL:
        if key not in fighter:
            return f"Missing field: {key}"

    identity = fighter.get("identity", {})
    if not isinstance(identity, dict):
        return "identity must be an object"

    if not identity.get("display_name"):
        return "Missing identity.display_name"

    stats = fighter.get("stats", {})
    if not isinstance(stats, dict):
        return "stats must be an object"

    for stat in REQUIRED_STATS:
        if stat not in stats:
            return f"Missing stat: {stat}"
        if not isinstance(stats[stat], (int, float)):
            return f"Stat {stat} must be numeric"

    return None


def process_submission(row: dict):
    fighter = row.get("fighter_data") or {}
    fighter_id = fighter.get("fighter_id")

    if not fighter_id:
        print(f"[SKIP] Row {row.get('id')} missing fighter_id")
        return

    print(f"\nApproved: {fighter_id}")

    draft_path = DRAFTS_DIR / f"{fighter_id}.json"
    save_json(draft_path, fighter)

    error = validate_fighter(fighter)
    if error:
        print(f"[REJECTED] {fighter_id}: {error}")
        rejected_path = REJECTED_DIR / f"{fighter_id}.json"
        save_json(rejected_path, fighter)

        try:
            patch_row(
                row["id"],
                {
                    "status": "rejected",
                    "rejection_reason": error,
                },
            )
        except Exception as patch_err:
            print(f"[WARN] Failed to patch rejected status for {fighter_id}: {patch_err}")
        return

    approved_path = APPROVED_DIR / f"{fighter_id}.json"
    save_json(approved_path, fighter)

    print(f"[PIPELINE] Running pipeline for {fighter_id}")

    try:
        generate = run_script("scripts/generate_fighter.py", fighter_id)
        if generate.stdout:
            print(generate.stdout.rstrip())
        if generate.stderr:
            print(generate.stderr.rstrip())
        if generate.returncode != 0:
            reason = extract_failure_reason(generate)
            print(f"[REJECTED] {fighter_id}: {reason}")
            save_json(REJECTED_DIR / f"{fighter_id}.json", fighter)
            try:
                patch_row(
                    row["id"],
                    {
                        "status": "rejected",
                        "rejection_reason": reason,
                    },
                )
            except Exception as patch_err:
                print(f"[WARN] Failed to patch rejected status for {fighter_id}: {patch_err}")
            return

        publish = run_script("scripts/publish_fighter.py", fighter_id)
        if publish.stdout:
            print(publish.stdout.rstrip())
        if publish.stderr:
            print(publish.stderr.rstrip())
        if publish.returncode != 0:
            reason = extract_failure_reason(publish)
            print(f"[ERROR] Publish failed for {fighter_id}: {reason}")
            try:
                patch_row(
                    row["id"],
                    {
                        "status": "publish_failed",
                        "rejection_reason": reason,
                    },
                )
            except Exception as patch_err:
                print(f"[WARN] Failed to patch publish_failed status for {fighter_id}: {patch_err}")
            return

        print(f"Published {fighter_id}")

        try:
            patch_row(
                row["id"],
                {
                    "status": "published",
                },
            )
        except Exception as patch_err:
            print(f"[WARN] Failed to patch published status for {fighter_id}: {patch_err}")

    except Exception as err:
        print(f"[ERROR] Pipeline failed for {fighter_id}: {err}")


def main():
    print("======================================")
    print("Syncing Supabase submissions...")
    print("======================================")

    submissions = fetch_submissions()

    if not submissions:
        print("No submissions found.")
        return

    for row in submissions:
        process_submission(row)


if __name__ == "__main__":
    main()
