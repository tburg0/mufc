import json
import subprocess
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT / 'scripts'
IMPORT_SCRIPT = SCRIPTS_DIR / 'import_supabase_submissions.py'
PUBLISH_ALL_SCRIPT = SCRIPTS_DIR / 'publish_all_approved.py'
BUILD_LIVE_SCRIPT = SCRIPTS_DIR / 'build_live_roster_v2.py'
LOCK_FILE = ROOT / '.sync_live_roster.lock'
LIVE_ROSTER_FILE = ROOT / 'live_roster.json'
PUBLIC_LIVE_ROSTER_FILE = ROOT / 'public' / 'live_roster.json'


def run_step(label: str, cmd: list[str]) -> int:
    print(f'[{label}] running: {' '.join(cmd)}')
    proc = subprocess.run(cmd, cwd=str(ROOT))
    print(f'[{label}] exit code: {proc.returncode}')
    return proc.returncode


def main() -> int:
    if LOCK_FILE.exists():
        print('sync_live_roster already running; skipping this pass.')
        return 0

    if not IMPORT_SCRIPT.exists():
        print(f'Missing import script: {IMPORT_SCRIPT}')
        return 1
    if not PUBLISH_ALL_SCRIPT.exists():
        print(f'Missing publish-all script: {PUBLISH_ALL_SCRIPT}')
        return 1
    if not BUILD_LIVE_SCRIPT.exists():
        print(f'Missing live-roster build script: {BUILD_LIVE_SCRIPT}')
        return 1

    LOCK_FILE.write_text('running', encoding='utf-8')
    try:
        py = 'py' if sys.platform.startswith('win') else sys.executable
        code1 = run_step('import', [py, str(IMPORT_SCRIPT)])
        code2 = run_step('publish_all', [py, str(PUBLISH_ALL_SCRIPT)])
        code3 = run_step('build_live_roster', [py, str(BUILD_LIVE_SCRIPT)])

        if code3 == 0 and LIVE_ROSTER_FILE.exists():
            PUBLIC_LIVE_ROSTER_FILE.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(LIVE_ROSTER_FILE, PUBLIC_LIVE_ROSTER_FILE)

        summary = {
            'import_exit_code': code1,
            'publish_all_exit_code': code2,
            'build_live_roster_exit_code': code3,
            'ok': code1 == 0 and code2 == 0 and code3 == 0,
        }
        (ROOT / 'generated' / 'last_live_sync.json').parent.mkdir(parents=True, exist_ok=True)
        (ROOT / 'generated' / 'last_live_sync.json').write_text(
            json.dumps(summary, indent=2), encoding='utf-8'
        )
        return 0 if summary['ok'] else 1
    finally:
        try:
            LOCK_FILE.unlink()
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    raise SystemExit(main())
