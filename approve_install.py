import json, shutil, time
from pathlib import Path
from typing import Dict, Any

REPORTS_DIR = Path("submissions/reports")
QUAR_DIR = Path("submissions/quarantine")
APPROVED_DIR = Path("submissions/approved")

CHARS_DIR = Path("chars")
SELECT_DEF = Path("data/select.def")

def load_json(p: Path) -> Dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def backup_select_def() -> Path:
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup = SELECT_DEF.parent / f"select.def.bak_{ts}"
    shutil.copyfile(SELECT_DEF, backup)
    return backup

def append_to_select_def(folder_name: str) -> None:
    """
    Appends 'folder_name' as a character line if not present.
    Keeps it simple: adds near the end of character list (before [ExtraStages] if found).
    """
    text = SELECT_DEF.read_text(encoding="utf-8", errors="ignore").splitlines(True)

    # already present?
    needle = folder_name.lower()
    for line in text:
        s = line.strip()
        if not s or s.startswith(";"):
            continue
        if s.split(",", 1)[0].strip().lower() == needle:
            return

    # Find insertion point: before [ExtraStages] (or end of file)
    insert_idx = len(text)
    for i, line in enumerate(text):
        if line.strip().lower() == "[extrastages]":
            insert_idx = i
            break

    new_line = f"{folder_name}\n"
    text.insert(insert_idx, new_line)
    SELECT_DEF.write_text("".join(text), encoding="utf-8")

def install_from_report(report_path: Path, overwrite: bool = False) -> None:
    report = load_json(report_path)

    if report.get("status") != "PASS":
        raise SystemExit(f"Report is not PASS: {report_path.name}")

    rec = report.get("recommended")
    if not rec:
        raise SystemExit("No recommended candidate in report.")

    src_folder = Path(rec["folder"])
    folder_name = rec["folder_name"]

    if not src_folder.exists():
        raise SystemExit(f"Source folder missing: {src_folder}")

    dest_folder = CHARS_DIR / folder_name

    if dest_folder.exists():
        if not overwrite:
            raise SystemExit(f"Destination exists: {dest_folder}. Re-run with --overwrite or rename.")
        shutil.rmtree(dest_folder, ignore_errors=True)

    print(f"Installing character: {folder_name}")
    shutil.copytree(src_folder, dest_folder)

    # Backup & append select.def
    backup = backup_select_def()
    append_to_select_def(folder_name)
    print(f"Updated select.def (backup: {backup.name})")

    # Move original zip to approved (if still exists in inbox/rejected, user may move manually)
    safe_name = report_path.stem.split("__")[0] + ".zip"
    # Try to locate zip by name anywhere under submissions
    zip_candidates = list(Path("submissions").rglob(safe_name))
    for z in zip_candidates:
        if z.is_file() and z.suffix.lower() == ".zip":
            APPROVED_DIR.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(z), str(APPROVED_DIR / z.name))
                print(f"Moved zip to approved: submissions/approved/{z.name}")
            except:
                pass
            break

    print("Done.")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("report", help="Path to a PASS report JSON in submissions/reports/")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing chars/<name> folder if present")
    args = ap.parse_args()

    install_from_report(Path(args.report), overwrite=args.overwrite)

if __name__ == "__main__":
    main()