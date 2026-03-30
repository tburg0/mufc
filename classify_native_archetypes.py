import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHARS_DIR = ROOT / "chars"
META_PATH = ROOT / "fighters_metadata.json"

OVERWRITE_EXISTING_ARCHETYPE = False

SKIP_FOLDERS = {
    "__pycache__",
}

PROJECTILE_HINTS = [
    "projectile",
    "helper",
    "projhit",
    "fireball",
    "hadouken",
    "reppuken",
    "beam",
    "shot"
]

THROW_HINTS = [
    "throw",
    "p2stateno",
    "targetbind",
    "targetstate",
    "targetdrop"
]

RUSHDOWN_HINTS = [
    "dash",
    "run",
    "hop",
    "rush",
    "chaincombo",
    "velset",
    "veladd"
]

COUNTER_HINTS = [
    "reversal",
    "counter",
    "guard",
    "parry"
]

ARMOR_HINTS = [
    "nothitby",
    "superarmor",
    "armor"
]


def load_metadata():
    if not META_PATH.exists():
        return {"fighters": {}}, True

    with open(META_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "fighters" in data and isinstance(data["fighters"], dict):
        return data, True

    if isinstance(data, dict):
        return data, False

    raise ValueError("fighters_metadata.json must be a JSON object")


def save_metadata(data):
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def norm(text: str) -> str:
    return (text or "").strip().lower().replace("_", " ").replace("-", " ")


def find_best_def_file(folder: Path):
    defs = sorted(folder.glob("*.def"))
    if not defs:
        return None

    folder_name_norm = norm(folder.name)
    for d in defs:
        if norm(d.stem) == folder_name_norm:
            return d

    return defs[0]


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1].strip()
    return value


def parse_def_info(def_path: Path):
    info = {}
    in_info = False
    linked_files = {
        "cmd": None,
        "cns": [],
        "st": [],
    }

    with open(def_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue

            if ";" in line:
                line = line.split(";", 1)[0].strip()

            if not line:
                continue

            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].strip().lower()
                in_info = (section == "info")
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip().lower()
            value = strip_quotes(value)

            if in_info and key in {"name", "author", "displayname"}:
                info[key] = value

            if key == "cmd":
                linked_files["cmd"] = value
            elif key == "cns":
                linked_files["cns"].append(value)
            elif key.startswith("st"):
                linked_files["st"].append(value)

    return info, linked_files


def safe_read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def collect_related_text(folder: Path, def_path: Path, linked_files: dict) -> str:
    chunks = []

    # DEF itself
    chunks.append(safe_read_text(def_path))

    # CMD
    if linked_files.get("cmd"):
        chunks.append(safe_read_text(folder / linked_files["cmd"]))

    # CNS
    for cns_name in linked_files.get("cns", []):
        chunks.append(safe_read_text(folder / cns_name))

    # ST files
    for st_name in linked_files.get("st", []):
        chunks.append(safe_read_text(folder / st_name))

    # Fallback: common files if not linked
    if not chunks or len("".join(chunks)) < 200:
        for ext in ("*.cmd", "*.cns", "*.st"):
            for p in folder.glob(ext):
                chunks.append(safe_read_text(p))

    return "\n".join(chunks).lower()


def count_hits(text: str, hints: list[str]) -> int:
    total = 0
    for hint in hints:
        total += text.count(hint.lower())
    return total


def extract_damage_values(text: str) -> list[int]:
    vals = []
    for m in re.finditer(r"damage\s*=\s*(\d+)", text, flags=re.IGNORECASE):
        try:
            vals.append(int(m.group(1)))
        except Exception:
            pass
    return vals


def extract_velocity_values(text: str) -> list[float]:
    vals = []
    patterns = [
        r"ground\.velocity\s*=\s*([-]?\d+(?:\.\d+)?)",
        r"air\.velocity\s*=\s*([-]?\d+(?:\.\d+)?)",
        r"velset\s*=\s*([-]?\d+(?:\.\d+)?)",
        r"veladd\s*=\s*([-]?\d+(?:\.\d+)?)",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            try:
                vals.append(abs(float(m.group(1))))
            except Exception:
                pass
    return vals


def classify_from_text(text: str) -> tuple[str, dict]:
    projectile_score = count_hits(text, PROJECTILE_HINTS)
    throw_score = count_hits(text, THROW_HINTS)
    rush_score = count_hits(text, RUSHDOWN_HINTS)
    counter_score = count_hits(text, COUNTER_HINTS)
    armor_score = count_hits(text, ARMOR_HINTS)

    damages = extract_damage_values(text)
    velocities = extract_velocity_values(text)

    avg_damage = sum(damages) / len(damages) if damages else 0
    avg_vel = sum(velocities) / len(velocities) if velocities else 0

    score = {
        "projectile": projectile_score,
        "throw": throw_score,
        "rush": rush_score,
        "counter": counter_score,
        "armor": armor_score,
        "avg_damage": round(avg_damage, 2),
        "avg_velocity": round(avg_vel, 2),
    }

    # Heuristic classification
    if projectile_score >= 8 and throw_score <= 2:
        return "Zoner", score

    if throw_score >= 8 and avg_damage >= 80:
        return "Grappler", score

    if armor_score >= 4 and avg_damage >= 85:
        return "Tank", score

    if rush_score >= 8 and avg_vel >= 3.5:
        return "Rushdown", score

    if projectile_score >= 4 and rush_score >= 4:
        return "Hybrid", score

    if counter_score >= 4 and throw_score >= 3:
        return "Hybrid", score

    if avg_damage >= 75 and avg_vel >= 2.0:
        return "Striker", score

    if throw_score >= 5:
        return "Grappler", score

    if rush_score >= 5:
        return "Rushdown", score

    if projectile_score >= 4:
        return "Zoner", score

    return "Roster", score


def discover_chars():
    if not CHARS_DIR.exists():
        raise FileNotFoundError(f"chars folder not found: {CHARS_DIR}")

    out = []
    for folder in sorted(CHARS_DIR.iterdir()):
        if not folder.is_dir():
            continue
        if folder.name.lower() in SKIP_FOLDERS:
            continue

        def_file = find_best_def_file(folder)
        if not def_file:
            continue

        info, linked_files = parse_def_info(def_file)
        display_name = (
            info.get("name")
            or info.get("displayname")
            or def_file.stem.strip()
            or folder.name.strip()
        )

        text = collect_related_text(folder, def_file, linked_files)
        archetype, score = classify_from_text(text)

        out.append({
            "display_name": display_name,
            "folder_name": folder.name,
            "def_file": def_file.name,
            "def_path": f"{folder.name}/{def_file.name}",
            "archetype": archetype,
            "score": score,
        })

    return out


def main():
    data, wrapped = load_metadata()
    fighters_meta = data["fighters"] if wrapped else data

    chars = discover_chars()

    added = 0
    updated = 0
    skipped = 0

    for ch in chars:
        name = ch["display_name"]

        if name not in fighters_meta or not isinstance(fighters_meta[name], dict):
            fighters_meta[name] = {
                "author": "Legacy Fighter",
                "archetype": ch["archetype"],
                "power_index": 50,
                "source": "native",
                "char_folder": ch["folder_name"],
                "def_file": ch["def_file"],
                "def_path": ch["def_path"],
                "archetype_guess_detail": ch["score"],
            }
            added += 1
            continue

        meta = fighters_meta[name]
        meta.setdefault("source", "native")
        meta.setdefault("char_folder", ch["folder_name"])
        meta.setdefault("def_file", ch["def_file"])
        meta.setdefault("def_path", ch["def_path"])
        meta["archetype_guess_detail"] = ch["score"]

        existing_arch = str(meta.get("archetype", "")).strip()
        if OVERWRITE_EXISTING_ARCHETYPE or not existing_arch or existing_arch in {"Roster", "Unknown"}:
            meta["archetype"] = ch["archetype"]
            updated += 1
        else:
            skipped += 1

    save_metadata(data)

    print(f"Characters scanned: {len(chars)}")
    print(f"Added metadata entries: {added}")
    print(f"Updated archetypes: {updated}")
    print(f"Skipped existing archetypes: {skipped}")
    print(f"Saved: {META_PATH}")


if __name__ == "__main__":
    main()