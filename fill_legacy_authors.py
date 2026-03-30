import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
META_PATH = ROOT / "fighters_metadata.json"

DEFAULT_AUTHOR = "Legacy Fighter"

CAPCOM_NAMES = {
    "ryu", "ken", "chunli", "chun-li", "guile", "blanka", "zangief", "dhalsim",
    "cammy", "vega", "balrog", "mbison", "m. bison", "sagat", "akuma",
    "dan", "sakura", "ibuki", "juri", "rashid", "ed", "e.honda", "ehonda",
    "honda", "cody", "guy", "hugo", "poison", "rolento", "lucia", "kage",
    "kyo kusanagi"  # remove if you want SNK for Kyo instead
}

SNK_NAMES = {
    "kyo", "kyo kusanagi", "iori", "iori yagami", "terry", "terry bogard",
    "andy", "andy bogard", "joe higashi", "mai", "mai shiranui", "athena",
    "kensou", "ralf", "clark", "leona", "kim", "kim dong hwan", "geese",
    "rock howard", "ryo", "robert", "takuma", "yuri", "benimaru", "shingo",
    "rugal", "goenitz", "k'", "k9999", "shen woo", "oswald"
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
    return "".join(ch.lower() for ch in (text or "") if ch.isalnum() or ch in {" ", "-", "_"}) \
        .replace("_", " ").strip()

def guess_author(name: str, meta: dict) -> str:
    n = norm(name)

    # If there is already a creator-like field, prefer that
    for key in ("creator_name", "creator", "submitted_by"):
        val = meta.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()

    # Heuristic by archetype/source/type if available
    source = str(meta.get("source", "")).lower()
    if "custom" in source or "submitted" in source:
        return "Custom"

    # Name heuristics
    if n in SNK_NAMES:
        return "SNK"
    if n in CAPCOM_NAMES:
        return "Capcom"
    if n in MARVEL_NAMES:
        return "Marvel"
    if n in DC_NAMES:
        return "DC"

    # Partial-match heuristics
    if any(x in n for x in ("kusanagi", "yagami", "bogard", "shiranui", "kensou", "rugal", "goenitz")):
        return "SNK"
    if any(x in n for x in ("blanka", "chun", "dhalsim", "zangief", "cammy", "akuma", "sagat", "guile")):
        return "Capcom"
    if any(x in n for x in ("thor", "wolverine", "spider", "magneto", "venom", "doom", "deadpool")):
        return "Marvel"
    if any(x in n for x in ("batman", "superman", "joker", "harley", "darkseid")):
        return "DC"

    return DEFAULT_AUTHOR

def main():
    if not META_PATH.exists():
        raise FileNotFoundError(f"fighters_metadata.json not found: {META_PATH}")

    with open(META_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Support either {"fighters": {...}} or plain dict
    if isinstance(data, dict) and "fighters" in data and isinstance(data["fighters"], dict):
        fighters = data["fighters"]
        wrapped = True
    elif isinstance(data, dict):
        fighters = data
        wrapped = False
    else:
        raise ValueError("fighters_metadata.json is not a JSON object")

    updated = 0
    skipped = 0

    for fighter_name, meta in fighters.items():
        if not isinstance(meta, dict):
            continue

        existing = meta.get("author")
        if isinstance(existing, str) and existing.strip():
            skipped += 1
            continue

        meta["author"] = guess_author(fighter_name, meta)
        updated += 1

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated authors: {updated}")
    print(f"Already had authors: {skipped}")
    print(f"Saved: {META_PATH}")

if __name__ == "__main__":
    main()