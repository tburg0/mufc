import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SELECT_PATH = ROOT / "data" / "select.def"
META_PATH = ROOT / "fighters_metadata.json"

DEFAULT_AUTHOR = "Legacy Fighter"
DEFAULT_ARCHETYPE = "Roster"
DEFAULT_POWER_INDEX = 50

CAPCOM_NAMES = {
    "ryu", "ken", "chunli", "chun-li", "guile", "blanka", "zangief", "dhalsim",
    "cammy", "vega", "balrog", "mbison", "m. bison", "sagat", "akuma",
    "dan", "sakura", "ibuki", "juri", "rashid", "ehonda", "e honda", "honda",
    "cody", "guy", "hugo", "poison", "rolento", "lucia"
}

SNK_NAMES = {
    "kyo", "kyo kusanagi", "iori", "iori yagami", "terry", "terry bogard",
    "andy", "andy bogard", "joe higashi", "mai", "mai shiranui", "athena",
    "kensou", "ralf", "clark", "leona", "kim", "kim dong hwan", "geese",
    "rock howard", "ryo", "robert", "takuma", "yuri", "benimaru", "shingo",
    "rugal", "goenitz", "oswald"
}

MARVEL_NAMES = {
    "thor", "hulk", "iron man", "spider-man", "spiderman", "wolverine",
    "captain america", "magneto", "storm", "cyclops", "venom", "thanos",
    "doctor doom", "doom", "deadpool", "loki", "black panther"
}

DC_NAMES = {
    "batman", "superman", "wonder woman", "flash", "green lantern",
    "aquaman", "joker", "harley quinn", "catwoman", "bane", "darkseid"
}


def norm(text: str) -> str:
    return (
        (text or "")
        .strip()
        .lower()
        .replace("_", " ")
    )


def guess_author(name: str) -> str:
    n = norm(name)

    if n in SNK_NAMES:
        return "SNK"
    if n in CAPCOM_NAMES:
        return "Capcom"
    if n in MARVEL_NAMES:
        return "Marvel"
    if n in DC_NAMES:
        return "DC"

    if any(x in n for x in ("kusanagi", "yagami", "bogard", "shiranui", "kensou", "rugal", "goenitz")):
        return "SNK"
    if any(x in n for x in ("blanka", "chun", "dhalsim", "zangief", "cammy", "akuma", "sagat", "guile")):
        return "Capcom"
    if any(x in n for x in ("thor", "wolverine", "spider", "magneto", "venom", "doom", "deadpool")):
        return "Marvel"
    if any(x in n for x in ("batman", "superman", "joker", "harley", "darkseid")):
        return "DC"

    return DEFAULT_AUTHOR


def guess_archetype(name: str) -> str:
    n = norm(name)

    if any(x in n for x in ("zangief", "hulk", "thor", "bane", "juggernaut")):
        return "Power"
    if any(x in n for x in ("ryu", "ken", "kyo", "iori", "terry", "guile")):
        return "Striker"
    if any(x in n for x in ("chun", "cammy", "mai", "ibuki", "sakura")):
        return "Agile"
    if any(x in n for x in ("doom", "magneto", "venom", "akuma")):
        return "Hybrid"

    return DEFAULT_ARCHETYPE


def guess_power_index(name: str) -> int:
    n = norm(name)

    if any(x in n for x in ("hulk", "thor", "akuma", "magneto", "doom", "juggernaut")):
        return 85
    if any(x in n for x in ("ryu", "ken", "kyo", "iori", "terry", "guile", "cammy", "chun")):
        return 72
    if any(x in n for x in ("sakura", "dan", "kensou", "athena")):
        return 62

    return DEFAULT_POWER_INDEX


def load_metadata() -> tuple[dict, bool]:
    if not META_PATH.exists():
        return {"fighters": {}}, True

    with open(META_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "fighters" in data and isinstance(data["fighters"], dict):
        return data, True

    if isinstance(data, dict):
        return data, False

    raise ValueError("fighters_metadata.json must be a JSON object")


def save_metadata(data: dict):
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def parse_select_def():
    if not SELECT_PATH.exists():
        raise FileNotFoundError(f"select.def not found: {SELECT_PATH}")

    entries = []
    in_chars = False

    with open(SELECT_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue

            lower = line.lower()

            if lower.startswith("[characters]"):
                in_chars = True
                continue

            if lower.startswith("[") and lower != "[characters]":
                if in_chars:
                    break
                continue

            if not in_chars:
                continue

            if line.startswith(";"):
                continue

            # remove inline comments
            if ";" in line:
                line = line.split(";", 1)[0].strip()

            if not line:
                continue

            # example:
            # Kyo Kusanagi, random
            # chars/foo/bar.def, random
            first_part = line.split(",", 1)[0].strip()

            if not first_part:
                continue

            lower_first = first_part.lower()

            if "randomselect" in lower_first:
                continue

            # stage lines usually live elsewhere, but guard anyway
            if lower_first.endswith(".def") and "stages/" in lower_first:
                continue

            entries.append(first_part)

    return entries


def display_name_from_select_entry(entry: str) -> str:
    # If explicit def path is used, use folder stem / file stem
    normalized = entry.replace("\\", "/").strip()

    if normalized.lower().endswith(".def"):
        parts = normalized.split("/")
        if len(parts) >= 2:
            # Prefer def stem
            stem = Path(parts[-1]).stem.strip()
            if stem:
                return stem
        return Path(normalized).stem.strip()

    # Otherwise use entry as-is
    return entry.strip()


def main():
    data, wrapped = load_metadata()
    fighters = data["fighters"] if wrapped else data

    native_entries = parse_select_def()

    added = 0
    already_present = 0

    for entry in native_entries:
        display_name = display_name_from_select_entry(entry)

        if not display_name:
            continue

        # keep exact display name as metadata key so overlay lookups still work
        if display_name in fighters:
            already_present += 1
            continue

        fighters[display_name] = {
            "author": guess_author(display_name),
            "archetype": guess_archetype(display_name),
            "power_index": guess_power_index(display_name),
            "source": "native",
            "select_entry": entry
        }
        added += 1

    save_metadata(data)

    print(f"Native roster entries found: {len(native_entries)}")
    print(f"Added metadata entries: {added}")
    print(f"Already present: {already_present}")
    print(f"Saved: {META_PATH}")


if __name__ == "__main__":
    main()