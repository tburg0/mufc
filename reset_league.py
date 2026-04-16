from __future__ import annotations

import json
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
STATE_FILE = ROOT / "league_state.json"
RECORDS_FILE = ROOT / "records.json"
HISTORY_FILE = ROOT / "match_history.jsonl"
CHAMPIONS_HISTORY_FILE = ROOT / "champions_history.txt"
CHAMPIONS_STATS_FILE = ROOT / "champions_stats.txt"
LEADERBOARD_FILE = ROOT / "leaderboard.txt"
HALL_FILE = ROOT / "hall_of_champions.txt"
TAG_HALL_FILE = ROOT / "tag_hall_of_champions.txt"
ROYAL_FILE = ROOT / "royal_bracket.json"
GRAND_PRIX_FILE = ROOT / "grand_prix_bracket.json"
TAG_SERIES_FILE = ROOT / "tag_series.json"
MATCH_FILE = ROOT / "current_match.txt"
CONTEXT_FILE = ROOT / "match_context.json"
TITLE_FLAG_FILE = ROOT / "is_title_match.txt"
PREMATCH_FILE = ROOT / "prematch.txt"
ARGS_FILE = ROOT / "mugen_args.txt"
ELO_START = 1500.0


def save_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_roster():
    spec = importlib.util.spec_from_file_location("matchmaker", ROOT / "matchmaker.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.load_roster()


def default_record() -> dict:
    return {
        "W": 0,
        "L": 0,
        "streak": 0,
        "elo": ELO_START,
        "reigns": 0,
        "defenses": 0,
        "mainW": 0,
        "mainL": 0,
        "titleW": 0,
        "titleL": 0,
    }


def main() -> None:
    roster, counts = load_roster()
    records = {fighter["name"]: default_record() for fighter in roster}

    state = {
        "champion": None,
        "reign_defenses": 0,
        "reign_start_ts": None,
        "tag_champions": None,
        "tag_defenses": 0,
        "tag_reigns": 0,
        "tag_match_count": 0,
        "tag_series_count": 0,
        "match_count": 0,
        "debut_queue": [],
        "royal_winner_queue": None,
        "tournament_title_queue": [],
        "world_title_tracker": {"champion_key": None, "faced": []},
        "tag_title_tracker": {"champion_key": None, "faced": []},
        "rivalries": [],
    }

    save_json(RECORDS_FILE, records)
    save_json(STATE_FILE, state)
    save_json(ROYAL_FILE, {"active": False})
    save_json(GRAND_PRIX_FILE, {"active": False})
    save_json(TAG_SERIES_FILE, {"active": False})

    HISTORY_FILE.write_text("", encoding="utf-8")
    CHAMPIONS_HISTORY_FILE.write_text("=== CHAMPIONS HISTORY ===\n\n", encoding="utf-8")
    CHAMPIONS_STATS_FILE.write_text("=== CHAMPION STATS ===\nCurrent Champion: None\n\nNo active champion.\n", encoding="utf-8")
    LEADERBOARD_FILE.write_text("Last result: --\n\nTop 10 by Elo (min games: 1)\n", encoding="utf-8")
    HALL_FILE.write_text("=== HALL OF CHAMPIONS ===\n\n", encoding="utf-8")
    TAG_HALL_FILE.write_text("=== TAG TEAM HALL OF CHAMPIONS ===\n\n", encoding="utf-8")
    MATCH_FILE.write_text("", encoding="utf-8")
    CONTEXT_FILE.write_text("{}", encoding="utf-8")
    TITLE_FLAG_FILE.write_text("0", encoding="utf-8")
    PREMATCH_FILE.write_text("PRE-MATCH: Season reset in progress\n", encoding="utf-8")
    ARGS_FILE.write_text("", encoding="utf-8")

    print(json.dumps({
        "reset": True,
        "fighters_reset": counts["total"],
        "native": counts["native"],
        "submitted": counts["submitted"],
        "champion": None,
        "tag_champions": None,
    }, indent=2))


if __name__ == "__main__":
    main()
