from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == 'scripts' else Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT / 'scripts'
APPROVED_DIR = ROOT / 'submissions' / 'approved'
GENERATED_DIR = ROOT / 'generated' / 'fighters'
PUBLISHED_ROSTER_PATH = ROOT / 'generated' / 'published_roster.json'
PYTHON = sys.executable or 'py'


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def normalize_fighter_id_from_roster_entry(entry) -> str | None:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        for key in ('fighter_id', 'id', 'submission_id', 'name'):
            value = entry.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def get_live_roster_ids() -> set[str]:
    roster = load_json(PUBLISHED_ROSTER_PATH, [])
    ids: set[str] = set()
    if isinstance(roster, list):
        for entry in roster:
            fid = normalize_fighter_id_from_roster_entry(entry)
            if fid:
                ids.add(fid)
    elif isinstance(roster, dict):
        for key, value in roster.items():
            if isinstance(key, str) and key.strip():
                ids.add(key.strip())
            fid = normalize_fighter_id_from_roster_entry(value)
            if fid:
                ids.add(fid)
    return ids


def run_script(script_name: str, fighter_id: str) -> subprocess.CompletedProcess:
    script_path = SCRIPTS_DIR / script_name
    cmd = [PYTHON, str(script_path), fighter_id]
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


def main() -> int:
    approved_files = sorted(APPROVED_DIR.glob('*.json'))
    live_ids = get_live_roster_ids()

    missing = [p.stem for p in approved_files if p.stem not in live_ids]

    print(f'Missing from live roster: {len(missing)}')
    if not missing:
        print('Nothing to publish.')
        return 0

    failures = 0

    for fighter_id in missing:
        generated_path = GENERATED_DIR / f'{fighter_id}.json'

        if not generated_path.exists():
            print(f'\n[GENERATE] {fighter_id}')
            gen = run_script('generate_fighter.py', fighter_id)
            if gen.stdout:
                print(gen.stdout.rstrip())
            if gen.stderr:
                print(gen.stderr.rstrip())
            if gen.returncode != 0:
                print(f'[FAILED GENERATE] {fighter_id} (exit code {gen.returncode})')
                failures += 1
                continue
            if not generated_path.exists():
                print(f'[FAILED GENERATE] {fighter_id} (no generated file created)')
                failures += 1
                continue

        print(f'\n[PUBLISH] {fighter_id}')
        pub = run_script('publish_fighter.py', fighter_id)
        if pub.stdout:
            print(pub.stdout.rstrip())
        if pub.stderr:
            print(pub.stderr.rstrip())
        if pub.returncode != 0:
            print(f'[FAILED] {fighter_id} (exit code {pub.returncode})')
            failures += 1
            continue

    print(f'\nCompleted with {failures} failure(s).')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
