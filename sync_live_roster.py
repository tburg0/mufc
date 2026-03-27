import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT / 'scripts'
IMPORT_SCRIPT = SCRIPTS_DIR / 'import_supabase_submissions.py'
PUBLISH_ALL_SCRIPT = SCRIPTS_DIR / 'publish_all_approved.py'
LOCK_FILE = ROOT / '.sync_live_roster.lock'


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

    LOCK_FILE.write_text('running', encoding='utf-8')
    try:
        py = 'py' if sys.platform.startswith('win') else sys.executable
        code1 = run_step('import', [py, str(IMPORT_SCRIPT)])
        code2 = run_step('publish_all', [py, str(PUBLISH_ALL_SCRIPT)])

        summary = {
            'import_exit_code': code1,
            'publish_all_exit_code': code2,
            'ok': code1 == 0 and code2 == 0,
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
