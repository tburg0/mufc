import os, json, hashlib, shutil, zipfile, time
from pathlib import Path
from typing import Dict, Any, List, Tuple

# ---------------- CONFIG ----------------
INBOX_DIR = Path("submissions/inbox")
QUAR_DIR = Path("submissions/quarantine")
REPORTS_DIR = Path("submissions/reports")
REJECTED_DIR = Path("submissions/rejected")

CHARS_DIR = Path("chars")

MAX_ZIP_MB = 800          # adjust to taste
MAX_FILES = 5000
BLOCK_EXTS = {".exe", ".dll", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".jar", ".com", ".scr"}

# What we want to find inside:
REQUIRED_DEF_EXT = ".def"
OPTIONAL_CORE_EXTS = {".sff", ".air", ".cmd", ".cns"}

# ---------------- HELPERS ----------------
def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def is_zip_slip(member_name: str) -> bool:
    # Prevent ../ and absolute paths
    member = Path(member_name)
    if member.is_absolute():
        return True
    parts = member.parts
    return any(part == ".." for part in parts)

def normalize(p: str) -> str:
    return p.replace("\\", "/")

def find_character_candidates(extract_dir: Path) -> List[Dict[str, Any]]:
    """
    Returns candidate character folders with:
      - folder path
      - main .def (best guess)
    """
    candidates = []
    # Heuristic: any folder containing at least one .def is a candidate
    for root, dirs, files in os.walk(extract_dir):
        files_lower = [f.lower() for f in files]
        def_files = [f for f in files if f.lower().endswith(".def")]
        if def_files:
            root_path = Path(root)
            # Best guess main def: foldername.def if exists else first .def
            folder_name = root_path.name
            main_def = None
            for f in def_files:
                if f.lower() == f"{folder_name.lower()}.def":
                    main_def = f
                    break
            if not main_def:
                main_def = def_files[0]
            candidates.append({
                "folder": str(root_path),
                "folder_name": folder_name,
                "main_def": str(root_path / main_def),
            })
    return candidates

def summarize_folder(folder: Path) -> Dict[str, Any]:
    exts = {}
    total_files = 0
    total_bytes = 0
    for root, dirs, files in os.walk(folder):
        for f in files:
            total_files += 1
            fp = Path(root) / f
            try:
                total_bytes += fp.stat().st_size
            except Exception:
                pass
            ext = fp.suffix.lower()
            exts[ext] = exts.get(ext, 0) + 1
    return {
        "total_files": total_files,
        "total_mb": round(total_bytes / (1024 * 1024), 2),
        "extensions": dict(sorted(exts.items(), key=lambda x: x[1], reverse=True)[:30]),
    }

def validate_zip(zip_path: Path) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "zip": str(zip_path),
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "sha256": sha256_file(zip_path),
        "status": "FAIL",
        "errors": [],
        "warnings": [],
        "meta": {},
        "candidates": [],
        "recommended": None,
    }

    # Size check
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    report["meta"]["zip_size_mb"] = round(size_mb, 2)
    if size_mb > MAX_ZIP_MB:
        report["errors"].append(f"ZIP too large: {size_mb:.2f}MB > {MAX_ZIP_MB}MB")

    # Zip inspection
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            infos = z.infolist()
            report["meta"]["zip_entries"] = len(infos)
            if len(infos) > MAX_FILES:
                report["errors"].append(f"Too many files in ZIP: {len(infos)} > {MAX_FILES}")

            blocked = []
            slips = []
            for info in infos:
                name = normalize(info.filename)
                if is_zip_slip(name):
                    slips.append(name)
                ext = Path(name).suffix.lower()
                if ext in BLOCK_EXTS:
                    blocked.append(name)

            if slips:
                report["errors"].append(f"Zip-slip paths detected (example): {slips[:3]}")
            if blocked:
                report["errors"].append(f"Blocked file types present (example): {blocked[:3]}")

            # If fatal already, don't extract
            if report["errors"]:
                return report

            # Extract safely
            safe_mkdir(QUAR_DIR)
            extract_dir = QUAR_DIR / report["sha256"][:12]
            if extract_dir.exists():
                shutil.rmtree(extract_dir, ignore_errors=True)
            safe_mkdir(extract_dir)

            for info in infos:
                name = normalize(info.filename)
                if is_zip_slip(name):
                    continue
                # Prevent writing outside extract_dir
                target = extract_dir / name
                target_parent = target.parent
                safe_mkdir(target_parent)
                if info.is_dir():
                    safe_mkdir(target)
                else:
                    with z.open(info, "r") as src, open(target, "wb") as dst:
                        shutil.copyfileobj(src, dst)

            report["meta"]["extract_dir"] = str(extract_dir)

            # Find candidate characters
            candidates = find_character_candidates(extract_dir)
            report["candidates"] = candidates

            if not candidates:
                report["errors"].append("No character candidates found (no .def files anywhere).")
                return report

            # Recommend the best candidate:
            # Prefer a folder that looks like chars/<name>/<name>.def structure by checking if folder_name.def exists.
            # We already picked main_def with that heuristic; now select candidate with most typical files
            scored: List[Tuple[int, Dict[str, Any]]] = []
            for c in candidates:
                folder = Path(c["folder"])
                summary = summarize_folder(folder)
                c["summary"] = summary

                score = 0
                # Give points for common character assets
                exts = summary["extensions"]
                score += 5 if ".sff" in exts else 0
                score += 3 if ".air" in exts else 0
                score += 2 if ".cmd" in exts else 0
                score += 2 if ".cns" in exts else 0
                # Prefer foldername.def
                if Path(c["main_def"]).name.lower() == f"{c['folder_name'].lower()}.def":
                    score += 6
                # Prefer being in a single top-level folder (shallower path)
                depth = len(Path(c["folder"]).relative_to(extract_dir).parts)
                score += max(0, 4 - depth)
                scored.append((score, c))

            scored.sort(key=lambda x: x[0], reverse=True)
            report["recommended"] = scored[0][1]
            report["status"] = "PASS"

            # Warnings
            # Warn if recommended folder name already exists in chars/
            rec_name = report["recommended"]["folder_name"]
            if (CHARS_DIR / rec_name).exists():
                report["warnings"].append(f"Character folder already exists in chars/: {rec_name} (will require rename or overwrite decision).")

            # Warn if missing typical assets
            exts = report["recommended"]["summary"]["extensions"]
            missing = [e for e in OPTIONAL_CORE_EXTS if e not in exts]
            if missing:
                report["warnings"].append(f"Recommended candidate missing common files: {missing} (may still work).")

            return report

    except zipfile.BadZipFile:
        report["errors"].append("BadZipFile: not a valid zip archive.")
        return report
    except Exception as e:
        report["errors"].append(f"Unhandled error: {type(e).__name__}: {e}")
        return report

def write_report(report: Dict[str, Any]) -> Path:
    safe_mkdir(REPORTS_DIR)
    out = REPORTS_DIR / f"{Path(report['zip']).stem}__{report['sha256'][:12]}.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    return out

def main():
    safe_mkdir(INBOX_DIR)
    zips = sorted([p for p in INBOX_DIR.iterdir() if p.is_file() and p.suffix.lower() == ".zip"])
    if not zips:
        print("No zip files found in submissions/inbox/")
        return

    for zp in zips:
        print(f"\nValidating: {zp.name}")
        report = validate_zip(zp)
        report_path = write_report(report)
        print(f"Status: {report['status']}  Report: {report_path}")

        if report["status"] != "PASS":
            # move to rejected
            safe_mkdir(REJECTED_DIR)
            dest = REJECTED_DIR / zp.name
            try:
                shutil.move(str(zp), str(dest))
                print(f"Moved to rejected: {dest}")
            except Exception as e:
                print(f"WARNING: could not move to rejected: {e}")
        else:
            if report["warnings"]:
                print("Warnings:")
                for w in report["warnings"]:
                    print(" -", w)

if __name__ == "__main__":
    main()