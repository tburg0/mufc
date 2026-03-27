import os, re, json, sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

# --- Always run relative to this script's folder (critical) ---
SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)

CHARS_DIR = SCRIPT_DIR / "chars"
OUT_FILE = SCRIPT_DIR / "fighters_metadata.json"

RE_KV = re.compile(r'^\s*([A-Za-z0-9_]+)\s*=\s*"?([^"\n\r;]+)"?\s*$', re.IGNORECASE)
RE_INCLUDE = re.compile(r'^\s*include\s*=\s*"?([^"\n\r;]+)"?\s*$', re.IGNORECASE)

RE_LIFE = re.compile(r'^\s*life\s*=\s*(\d+)\s*$', re.IGNORECASE | re.MULTILINE)
RE_ATTACK = re.compile(r'^\s*attack\s*=\s*(\d+)\s*$', re.IGNORECASE | re.MULTILINE)
RE_DEFENCE = re.compile(r'^\s*defence\s*=\s*(\d+)\s*$', re.IGNORECASE | re.MULTILINE)
RE_DEFENSE = re.compile(r'^\s*defense\s*=\s*(\d+)\s*$', re.IGNORECASE | re.MULTILINE)

RE_PROJECTILE = re.compile(r'^\s*type\s*=\s*Projectile\s*$', re.IGNORECASE | re.MULTILINE)
RE_HELPER = re.compile(r'^\s*type\s*=\s*Helper\s*$', re.IGNORECASE | re.MULTILINE)
RE_THROWLIKE = re.compile(r'^\s*type\s*=\s*(TargetState|TargetBind)\s*$', re.IGNORECASE | re.MULTILINE)

def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def pick_def_file(char_dir: Path) -> Path | None:
    preferred = char_dir / f"{char_dir.name}.def"
    if preferred.exists():
        return preferred
    defs = list(char_dir.glob("*.def"))
    return defs[0] if defs else None

def parse_def(def_path: Path) -> Dict[str, Any]:
    txt = read_text(def_path)
    info = {"def_path": str(def_path), "displayname": None, "author": None, "files": []}

    for line in txt.splitlines():
        s = line.strip()
        if not s or s.startswith(";"):
            continue
        m = RE_KV.match(s)
        if not m:
            continue
        k = m.group(1).strip().lower()
        v = m.group(2).strip()

        if k == "displayname":
            info["displayname"] = v
        elif k == "author":
            info["author"] = v
        elif k in ("cns", "cmd", "st", "stcommon", "air", "sprite", "anim"):
            info["files"].append(v)

    for line in txt.splitlines():
        mi = RE_INCLUDE.match(line.strip())
        if mi:
            info["files"].append(mi.group(1).strip())

    info["files"] = sorted(list({f for f in info["files"] if f}))
    return info

def resolve_file(base_dir: Path, rel: str) -> Path:
    rel = rel.replace("\\", "/").strip().strip('"')
    return (base_dir / rel).resolve()

def extract_stats_from_cns(paths: List[Path]) -> Tuple[int,int,int]:
    life = None
    attack = None
    defence = None

    for p in paths:
        txt = read_text(p)
        if not txt:
            continue
        if life is None:
            m = RE_LIFE.search(txt)
            if m: life = int(m.group(1))
        if attack is None:
            m = RE_ATTACK.search(txt)
            if m: attack = int(m.group(1))
        if defence is None:
            m = RE_DEFENCE.search(txt) or RE_DEFENSE.search(txt)
            if m: defence = int(m.group(1))

    # defaults
    life = life if life is not None else 1000
    attack = attack if attack is not None else 100
    defence = defence if defence is not None else 100
    return life, attack, defence

def classify_archetype(cns_paths: List[Path]) -> Tuple[str, Dict[str,int]]:
    proj = helper = throwlike = 0
    for p in cns_paths:
        txt = read_text(p)
        if not txt:
            continue
        proj += len(RE_PROJECTILE.findall(txt))
        helper += len(RE_HELPER.findall(txt))
        throwlike += len(RE_THROWLIKE.findall(txt))

    archetype = "Balanced"
    if proj >= 8:
        archetype = "Zoner"
    elif throwlike >= 12 and proj <= 3:
        archetype = "Grappler"
    elif helper >= 10 and proj < 6:
        archetype = "Summoner"
    elif proj <= 2 and helper <= 2:
        archetype = "Rushdown"

    return archetype, {"projectile": proj, "helper": helper, "throwlike": throwlike}

def power_index(life: int, attack: int, defence: int) -> float:
    return round((life/10.0)*0.5 + attack*0.35 + defence*0.15, 1)

def main():
    print("=== MUFC Character Scanner ===")
    print("Script dir:", SCRIPT_DIR)
    print("Looking for chars dir:", CHARS_DIR)

    out: Dict[str, Any] = {"generated_by": "character_scanner.py", "fighters": {}}

    if not CHARS_DIR.exists():
        print("ERROR: chars/ folder not found at:", CHARS_DIR)
        # Still write file so you can see it ran
        OUT_FILE.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
        print("Wrote EMPTY metadata to:", OUT_FILE)
        return

    char_dirs = [p for p in CHARS_DIR.iterdir() if p.is_dir()]
    print("Found folders in chars/:", len(char_dirs))

    scanned = 0
    skipped_no_def = 0

    for char_dir in sorted(char_dirs):
        def_path = pick_def_file(char_dir)
        if not def_path:
            skipped_no_def += 1
            continue

        info = parse_def(def_path)
        display = info["displayname"] or char_dir.name
        author = info["author"] or "Unknown"

        resolved = []
        for f in info["files"]:
            rp = resolve_file(char_dir, f)
            if rp.exists():
                resolved.append(rp)

        cns_paths = [p for p in resolved if p.suffix.lower() == ".cns"]
        life, atk, dfn = extract_stats_from_cns(cns_paths)
        arch, signals = classify_archetype(cns_paths)

        out["fighters"][char_dir.name] = {
            "folder": char_dir.name,
            "displayname": display,
            "author": author,
            "life": life,
            "attack": atk,
            "defence": dfn,
            "power_index": power_index(life, atk, dfn),
            "archetype": arch,
            "signals": signals,
            "def_path": str(def_path),
            "cns_files_found": len(cns_paths),
        }
        scanned += 1

    OUT_FILE.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")

    print("Scanned fighters:", scanned)
    print("Skipped (no .def):", skipped_no_def)
    print("Wrote metadata to:", OUT_FILE)
    print("File size bytes:", OUT_FILE.stat().st_size)

if __name__ == "__main__":
    main()