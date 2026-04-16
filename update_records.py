import json
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple

MATCH_FILE = "current_match.txt"
WATCHER_LOG = "watcher_output.log"
CHAMPIONS_HISTORY_FILE = "champions_history.txt"
CHAMPIONS_STATS_FILE = "champions_stats.txt"
RECORDS_FILE = "records.json"
STATE_FILE = "league_state.json"
HISTORY_FILE = "match_history.jsonl"
LEADERBOARD_FILE = "leaderboard.txt"
TAG_HALL_FILE = "tag_hall_of_champions.txt"
CONTEXT_FILE = "match_context.json"
ROYAL_FILE = "royal_bracket.json"
GRAND_PRIX_FILE = "grand_prix_bracket.json"
TAG_SERIES_FILE = "tag_series.json"
MAPPING_FILE = os.path.join("generated", "runtime_mapping.json")

TOP_N = 10
MIN_GAMES = 1
WAIT_SECONDS = 6.0
POLL_INTERVAL = 0.2
ELO_START = 1500.0
K_FACTOR = 32
RESULT_RE = re.compile(r"RESULT:\s*(\d+)\s*-\s*(\d+)", re.IGNORECASE)


def now_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def load_json(path: str, default: Any):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json_atomic(path: str, obj: Any) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def append_history(event: Dict[str, Any]) -> None:
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_current_match() -> Tuple[str, str]:
    line = open(MATCH_FILE, "r", encoding="utf-8").read().strip()
    if "," not in line:
        raise ValueError("Bad current_match.txt format")
    p1, p2 = [x.strip() for x in line.split(",", 1)]
    return p1, p2


def canonical_name(name: str, ctx: Dict[str, Any], mapping: Dict[str, Any]) -> str:
    if not name:
        return name

    runtime_to_name: Dict[str, str] = {}
    for display_name, entry in mapping.items():
        if not isinstance(entry, dict):
            continue
        runtime = str(entry.get("runtime_character", "")).strip()
        if runtime:
            runtime_to_name[runtime] = display_name

    if name in runtime_to_name:
        return runtime_to_name[name]

    for side in ("p1", "p2"):
        runtime = str(ctx.get(f"{side}_runtime", "")).strip()
        display = str(ctx.get(side, "")).strip()
        if name == runtime and display:
            return display

    return name


def ensure_entry(records: Dict[str, Any], name: str) -> None:
    records.setdefault(name, {"W": 0, "L": 0, "streak": 0, "elo": ELO_START, "reigns": 0, "defenses": 0})


def win_pct(w: int, l: int) -> float:
    g = w + l
    return (w / g) if g else 0.0


def fmt_streak(s: int) -> str:
    if s > 0:
        return f"W{s}"
    if s < 0:
        return f"L{abs(s)}"
    return "-"


def elo_expected(a: float, b: float) -> float:
    return 1.0 / (1.0 + (10 ** ((b - a) / 400.0)))


def elo_update(a: float, b: float, a_score: float, k: int = K_FACTOR) -> Tuple[float, float]:
    ea = elo_expected(a, b)
    eb = 1.0 - ea
    a_new = a + k * (a_score - ea)
    b_new = b + k * ((1.0 - a_score) - eb)
    return a_new, b_new


def get_last_result_from_log() -> Optional[Tuple[int, int]]:
    if not os.path.exists(WATCHER_LOG):
        return None
    with open(WATCHER_LOG, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - 131072), os.SEEK_SET)
        chunk = f.read().decode("utf-8", errors="ignore")
    for line in reversed(chunk.splitlines()):
        m = RESULT_RE.search(line)
        if m:
            return int(m.group(1)), int(m.group(2))
    return None


def wait_for_result(timeout_s: float) -> Optional[Tuple[int, int]]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        res = get_last_result_from_log()
        if res is not None:
            return res
        time.sleep(POLL_INTERVAL)
    return None


def build_top10_elo(records: Dict[str, Any]) -> List[Tuple[str, int, int, int, float]]:
    rows = []
    for name, rec in records.items():
        if "+" in name:
            continue
        w = int(rec.get("W", 0))
        l = int(rec.get("L", 0))
        g = w + l
        if g >= MIN_GAMES:
            rows.append((name, w, l, g, float(rec.get("elo", ELO_START))))
    rows.sort(key=lambda x: x[4], reverse=True)
    return rows[:TOP_N]


def team_key(a: str, b: str) -> str:
    x, y = sorted([a, b], key=lambda s: s.lower())
    return f"{x}+{y}"


def royal_advance(bracket: Dict[str, Any], winner: str) -> Dict[str, Any]:
    rd = bracket.get("round")
    if rd == "QF":
        winners = bracket.setdefault("winners_qf", [])
        winners.append(winner)
        if len(winners) >= 4:
            bracket["sf"] = [
                [winners[0], winners[1]],
                [winners[2], winners[3]],
            ]
            bracket["round"] = "SF"
    elif rd == "SF":
        winners = bracket.setdefault("winners_sf", [])
        winners.append(winner)
        if len(winners) >= 2:
            bracket["final"] = [[winners[0], winners[1]]]
            bracket["round"] = "F"
    elif rd == "F":
        bracket["winner"] = winner
        bracket["active"] = False
    return bracket


def grand_prix_advance(bracket: Dict[str, Any], winner: str) -> Dict[str, Any]:
    rd = bracket.get("round")
    if rd == "SF":
        winners = bracket.setdefault("winners_sf", [])
        winners.append(winner)
        if len(winners) >= 2:
            bracket["final"] = [[winners[0], winners[1]]]
            bracket["round"] = "F"
    elif rd == "F":
        bracket["winner"] = winner
        bracket["active"] = False
    return bracket


def append_title_queue(state: Dict[str, Any], fighter: str, source: str) -> None:
    queue = state.setdefault("tournament_title_queue", [])
    if any(str(item.get("fighter") or "").strip() == fighter for item in queue if isinstance(item, dict)):
        return
    queue.append({"fighter": fighter, "source": source})


def title_tracker(state: Dict[str, Any], key: str, champion_key: str) -> Dict[str, Any]:
    tracker = state.setdefault(key, {})
    tracked_champion_key = str(tracker.get("champion_key") or "")
    if tracked_champion_key != champion_key:
        tracker.clear()
        tracker["champion_key"] = champion_key
        tracker["faced"] = []
    tracker.setdefault("faced", [])
    return tracker


def mark_title_challenger_faced(state: Dict[str, Any], tracker_key: str, champion_key: str, challenger_key: str) -> None:
    tracker = title_tracker(state, tracker_key, champion_key)
    faced = [str(name) for name in tracker.get("faced", []) if str(name)]
    if challenger_key not in faced:
        faced.append(challenger_key)
    tracker["faced"] = faced


def update_rivalries(state: Dict[str, Any], p1: str, p2: str, winner: str, r1: int, r2: int, ctx: Dict[str, Any]) -> None:
    rivalries = state.setdefault("rivalries", [])
    fighters = sorted([p1, p2], key=lambda s: s.lower())
    next_match_number = int(state.get("match_count", 0)) + 1

    existing = None
    for item in rivalries:
        if not isinstance(item, dict):
            continue
        tracked = item.get("fighters") or []
        if sorted([str(name) for name in tracked], key=lambda s: s.lower()) == fighters:
            existing = item
            break

    if existing is None:
        existing = {
            "fighters": fighters,
            "meetings": 0,
            "wins": {fighters[0]: 0, fighters[1]: 0},
            "intensity": 0,
            "last_winner": None,
            "last_match_count": 0,
        }
        rivalries.append(existing)

    existing["meetings"] = int(existing.get("meetings", 0)) + 1
    wins = existing.setdefault("wins", {fighters[0]: 0, fighters[1]: 0})
    wins[winner] = int(wins.get(winner, 0)) + 1
    existing["last_winner"] = winner
    existing["last_match_count"] = next_match_number

    margin = abs(r1 - r2)
    intensity = float(existing.get("intensity", 0))
    if str(ctx.get("booking_reason") or "").strip().lower() == "rivalry rematch":
        intensity += 2.5
    if margin <= 1:
        intensity += 1.5
    if abs(int(wins.get(fighters[0], 0)) - int(wins.get(fighters[1], 0))) <= 1:
        intensity += 1.0
    existing["intensity"] = round(min(99.0, intensity), 2)

    rivalries[:] = sorted(
        [item for item in rivalries if isinstance(item, dict)],
        key=lambda item: (float(item.get("intensity", 0)), int(item.get("meetings", 0)), int(item.get("last_match_count", 0))),
        reverse=True,
    )[:40]


def update_individual(records: Dict[str, Any], winner: str, loser: str) -> None:
    ensure_entry(records, winner)
    ensure_entry(records, loser)
    records[winner]["W"] = int(records[winner].get("W", 0)) + 1
    records[loser]["L"] = int(records[loser].get("L", 0)) + 1
    w_prev = int(records[winner].get("streak", 0))
    l_prev = int(records[loser].get("streak", 0))
    records[winner]["streak"] = (w_prev + 1) if w_prev > 0 else 1
    records[loser]["streak"] = (l_prev - 1) if l_prev < 0 else -1
    w_elo = float(records[winner].get("elo", ELO_START))
    l_elo = float(records[loser].get("elo", ELO_START))
    w_new, l_new = elo_update(w_elo, l_elo, 1.0, K_FACTOR)
    records[winner]["elo"] = round(w_new, 2)
    records[loser]["elo"] = round(l_new, 2)


def update_team(records: Dict[str, Any], wkey: str, lkey: str) -> None:
    ensure_entry(records, wkey)
    ensure_entry(records, lkey)
    records[wkey]["W"] = int(records[wkey].get("W", 0)) + 1
    records[lkey]["L"] = int(records[lkey].get("L", 0)) + 1
    w_prev = int(records[wkey].get("streak", 0))
    l_prev = int(records[lkey].get("streak", 0))
    records[wkey]["streak"] = (w_prev + 1) if w_prev > 0 else 1
    records[lkey]["streak"] = (l_prev - 1) if l_prev < 0 else -1
    w_elo = float(records[wkey].get("elo", ELO_START))
    l_elo = float(records[lkey].get("elo", ELO_START))
    w_new, l_new = elo_update(w_elo, l_elo, 1.0, K_FACTOR)
    records[wkey]["elo"] = round(w_new, 2)
    records[lkey]["elo"] = round(l_new, 2)


def append_champion_history(old_champ: Optional[str], new_champ: str, result_str: str) -> None:
    line = f"{now_ts()} | NEW CHAMPION: {new_champ}"
    if old_champ:
        line += f" dethroned {old_champ}"
    if result_str:
        line += f" | {result_str}"
    with open(CHAMPIONS_HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def rebuild_champion_stats(state: Dict[str, Any], records: Dict[str, Any]) -> None:
    champ = state.get("champion")
    lines = ["=== CHAMPION STATS ===", f"Current Champion: {champ}", ""]
    if champ and champ in records:
        rec = records[champ]
        lines += [
            f"Name: {champ}",
            f"Record: {int(rec.get('W', 0))}-{int(rec.get('L', 0))}",
            f"Elo: {float(rec.get('elo', ELO_START)):.2f}",
            f"Reigns: {int(rec.get('reigns', 0))}",
            f"Defenses: {int(rec.get('defenses', 0))}",
            f"Current Reign Defenses: {int(state.get('reign_defenses', 0))}",
            f"Streak: {fmt_streak(int(rec.get('streak', 0)))}",
        ]
    else:
        lines.append("No active champion.")
    with open(CHAMPIONS_STATS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def build_hall_of_champions(records: Dict[str, Any]) -> None:
    rows = []

    for name, rec in records.items():
        if "+" in name:
            continue

        reigns = int(rec.get("reigns", 0))
        defenses = int(rec.get("defenses", 0))
        elo = float(rec.get("elo", ELO_START))
        w = int(rec.get("W", 0))
        l = int(rec.get("L", 0))

        if reigns > 0:
            rows.append((name, reigns, defenses, elo, w, l))

    rows.sort(key=lambda x: (x[1], x[2], x[3]), reverse=True)

    lines = [
        "=== HALL OF CHAMPIONS ===",
        "",
        f"{'#':>2} {'Name':<18} {'Reigns':>6} {'Defs':>6} {'W-L':>9} {'Elo':>7}",
        "-" * 72,
    ]

    for i, (name, r, d, e, w, l) in enumerate(rows[:20], 1):
        lines.append(f"{i:>2}. {name:<18} {r:>6} {d:>6} {f'{w}-{l}':>9} {e:>7.2f}")

    with open("hall_of_champions.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")



def build_tag_hall_of_champions(records: Dict[str, Any]) -> None:
    rows = []

    for name, rec in records.items():
        if "+" not in name:
            continue

        reigns = int(rec.get("reigns", 0))
        defenses = int(rec.get("defenses", 0))
        elo = float(rec.get("elo", ELO_START))
        w = int(rec.get("W", 0))
        l = int(rec.get("L", 0))
        display = " & ".join(part.strip() for part in name.split("+") if part.strip())

        if reigns > 0 or defenses > 0 or (w + l) > 0:
            rows.append((display, reigns, defenses, elo, w, l))

    rows.sort(key=lambda x: (x[1], x[2], x[3], x[4]), reverse=True)

    lines = [
        "=== TAG TEAM HALL OF CHAMPIONS ===",
        "",
        f"{'#':>2} {'Name':<24} {'Reigns':>6} {'Defs':>6} {'W-L':>9} {'Elo':>7}",
        "-" * 82,
    ]

    for i, (name, r, d, e, w, l) in enumerate(rows[:20], 1):
        lines.append(f"{i:>2}. {name:<24} {r:>6} {d:>6} {f'{w}-{l}':>9} {e:>7.2f}")

    with open(TAG_HALL_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def main() -> None:
    p1, p2 = read_current_match()
    ctx: Dict[str, Any] = load_json(CONTEXT_FILE, {"type": "SINGLES"})
    state: Dict[str, Any] = load_json(STATE_FILE, {"match_count": 0, "champion": None})
    records: Dict[str, Any] = load_json(RECORDS_FILE, {})
    mapping: Dict[str, Any] = load_json(MAPPING_FILE, {})

    p1 = canonical_name(p1, ctx, mapping)
    p2 = canonical_name(p2, ctx, mapping)

    res = wait_for_result(WAIT_SECONDS)
    if res is None:
        print("No RESULT found in watcher log yet. Skipping update.")
        return

    r1, r2 = res
    if r1 == r2:
        print("Tie/unknown result. No update.")
        return

    winner = p1 if r1 > r2 else p2
    loser = p2 if winner == p1 else p1
    update_individual(records, winner, loser)

    is_world_title = bool(ctx.get("is_world_title", False))
    is_royal = bool(ctx.get("is_royal", False))
    is_grand_prix = bool(ctx.get("is_grand_prix", False))
    is_tag_series = bool(ctx.get("is_tag_series", False))
    is_tag_title = bool(ctx.get("is_tag_title", False))
    is_debut = bool(ctx.get("is_debut", False))

    champion_pre = state.get("champion")
    title_changed = False

    if is_world_title:
        ensure_entry(records, winner)
        ensure_entry(records, loser)
        if champion_pre is None:
            state["champion"] = winner
            state["reign_defenses"] = 0
            state["reign_start_ts"] = now_ts()
            records[winner]["reigns"] = int(records[winner].get("reigns", 0)) + 1
            records[winner]["defenses"] = int(records[winner].get("defenses", 0))
            title_tracker(state, "world_title_tracker", winner)
            title_changed = True
            append_champion_history(None, winner, f"{winner} def. {loser} ({p1} {r1}-{r2} {p2})")
        elif champion_pre in (p1, p2):
            if winner == champion_pre:
                state["reign_defenses"] = int(state.get("reign_defenses", 0)) + 1
                records[winner]["defenses"] = int(records[winner].get("defenses", 0)) + 1
                mark_title_challenger_faced(state, "world_title_tracker", champion_pre, loser)
            else:
                mark_title_challenger_faced(state, "world_title_tracker", champion_pre, winner)
                state["champion"] = winner
                state["reign_defenses"] = 0
                state["reign_start_ts"] = now_ts()
                records[winner]["reigns"] = int(records[winner].get("reigns", 0)) + 1
                records[winner]["defenses"] = int(records[winner].get("defenses", 0))
                title_tracker(state, "world_title_tracker", winner)
                title_changed = True
                append_champion_history(champion_pre, winner, f"{winner} def. {loser} ({p1} {r1}-{r2} {p2})")

        state["royal_winner_queue"] = None
        if state.get("tournament_title_queue"):
            state["tournament_title_queue"] = []

    if is_royal:
        bracket = load_json(ROYAL_FILE, {"active": False})
        if bracket.get("active") or bracket.get("round") == "F":
            bracket = royal_advance(bracket, winner)
            save_json_atomic(ROYAL_FILE, bracket)
            if bracket.get("winner"):
                state["royal_winner_queue"] = bracket["winner"]
                append_title_queue(state, bracket["winner"], "Royal winner")

    if is_grand_prix:
        bracket = load_json(GRAND_PRIX_FILE, {"active": False})
        if bracket.get("active") or bracket.get("round") == "F":
            bracket = grand_prix_advance(bracket, winner)
            save_json_atomic(GRAND_PRIX_FILE, bracket)
            if bracket.get("winner"):
                append_title_queue(state, bracket["winner"], "Grand Prix winner")

    tag_series_event = None
    if is_tag_series:
        series = load_json(TAG_SERIES_FILE, {"active": False})
        if series.get("active") and int(series.get("id", -1)) == int(ctx.get("tag_series_id", -2)):
            leg = int(ctx.get("tag_leg", 1))
            team_a = series["teamA"]
            team_b = series["teamB"]
            key_a = series["teamA_key"]
            key_b = series["teamB_key"]

            if winner in team_a:
                series["scoreA"] += 1
                leg_winner_team = "A"
            else:
                series["scoreB"] += 1
                leg_winner_team = "B"

            for legobj in series.get("legs", []):
                if int(legobj.get("leg", 0)) == leg:
                    legobj["winner"] = winner
                    legobj["result"] = f"{r1}-{r2}"
                    break

            done = False
            series_winner_team = None
            if series["scoreA"] >= 2:
                done = True
                series_winner_team = "A"
            elif series["scoreB"] >= 2:
                done = True
                series_winner_team = "B"
            elif leg >= 2 and series["scoreA"] != series["scoreB"]:
                done = True
                series_winner_team = "A" if series["scoreA"] > series["scoreB"] else "B"
            else:
                series["leg"] = min(3, leg + 1)

            if not done:
                save_json_atomic(TAG_SERIES_FILE, series)
                tag_series_event = {
                    "type": "TAG_LEG",
                    "tag_series_id": series["id"],
                    "tag_leg": leg,
                    "teamA": team_a,
                    "teamB": team_b,
                    "teamA_key": key_a,
                    "teamB_key": key_b,
                    "scoreA": series["scoreA"],
                    "scoreB": series["scoreB"],
                    "leg_winner_team": leg_winner_team,
                }
            else:
                series["active"] = False
                series["winner_team"] = series_winner_team
                save_json_atomic(TAG_SERIES_FILE, series)

                if series_winner_team == "A":
                    wkey, lkey = key_a, key_b
                    winner_pair = team_a
                else:
                    wkey, lkey = key_b, key_a
                    winner_pair = team_b

                update_team(records, wkey, lkey)
                state["tag_series_count"] = int(state.get("tag_series_count", 0)) + 1

                tag_changed = False
                if is_tag_title:
                    champs = state.get("tag_champions")

                    ensure_entry(records, wkey)
                    ensure_entry(records, lkey)

                    if not champs:
                        state["tag_champions"] = winner_pair
                        state["tag_reigns"] = int(state.get("tag_reigns", 0)) + 1
                        state["tag_defenses"] = 0
                        records[wkey]["reigns"] = int(records[wkey].get("reigns", 0)) + 1
                        title_tracker(state, "tag_title_tracker", wkey)
                        tag_changed = True
                    elif set(champs) == set(winner_pair):
                        state["tag_defenses"] = int(state.get("tag_defenses", 0)) + 1
                        records[wkey]["defenses"] = int(records[wkey].get("defenses", 0)) + 1
                        mark_title_challenger_faced(state, "tag_title_tracker", wkey, lkey)
                    else:
                        champ_key = team_key(champs[0], champs[1]) if isinstance(champs, list) and len(champs) == 2 else ""
                        if champ_key:
                            mark_title_challenger_faced(state, "tag_title_tracker", champ_key, wkey)
                        state["tag_champions"] = winner_pair
                        state["tag_reigns"] = int(state.get("tag_reigns", 0)) + 1
                        state["tag_defenses"] = 0
                        records[wkey]["reigns"] = int(records[wkey].get("reigns", 0)) + 1
                        title_tracker(state, "tag_title_tracker", wkey)
                        tag_changed = True

                tag_series_event = {
                    "type": "TAG_SERIES_COMPLETE",
                    "tag_series_id": series["id"],
                    "teamA": team_a,
                    "teamB": team_b,
                    "teamA_key": key_a,
                    "teamB_key": key_b,
                    "final_scoreA": series["scoreA"],
                    "final_scoreB": series["scoreB"],
                    "series_winner_team": series_winner_team,
                    "team_record_updated": True,
                    "is_tag_title": is_tag_title,
                    "tag_champs_after": state.get("tag_champions"),
                    "tag_changed": tag_changed,
                }

    if not is_tag_series and not is_world_title and not is_royal and not is_grand_prix:
        if winner != state.get("champion") and int(records[winner].get("streak", 0)) >= 5:
            append_title_queue(state, winner, f"{winner} earned an automatic title shot on a {records[winner]['streak']}-fight win streak")
        update_rivalries(state, p1, p2, winner, r1, r2, ctx)

    state["match_count"] = int(state.get("match_count", 0)) + 1
    save_json_atomic(RECORDS_FILE, records)
    save_json_atomic(STATE_FILE, state)
    rebuild_champion_stats(state, records)
    build_hall_of_champions(records)
    build_tag_hall_of_champions(records)

    event = {
        "ts": now_ts(),
        "type": "SINGLES",
        "p1": p1,
        "p2": p2,
        "result": f"{r1}-{r2}",
        "winner": winner,
        "loser": loser,
        "world_title": is_world_title,
        "title_reason": ctx.get("title_reason"),
        "royal": is_royal,
        "royal_round": ctx.get("royal_round"),
        "grand_prix": is_grand_prix,
        "grand_prix_round": ctx.get("grand_prix_round"),
        "tag_series": is_tag_series,
        "tag_series_id": ctx.get("tag_series_id"),
        "tag_leg": ctx.get("tag_leg"),
        "is_debut": is_debut,
        "debut_fighter": ctx.get("debut_fighter"),
        "main_event": bool(ctx.get("main_event", False)),
        "main_event_reason": ctx.get("main_event_reason"),
        "booking_reason": ctx.get("booking_reason"),
        "contender_implication": bool(ctx.get("contender_implication", False)),
        "champion_after": state.get("champion"),
        "title_changed": title_changed,
    }
    if tag_series_event:
        event["tag_event"] = tag_series_event
    append_history(event)

    lines: List[str] = [
        f"Last result: {winner} def. {loser}  ({p1} {r1}-{r2} {p2})",
        f"{winner}: {records[winner]['W']}-{records[winner]['L']} ({fmt_streak(int(records[winner]['streak']))}) | Elo {records[winner]['elo']}",
        f"{loser}: {records[loser]['W']}-{records[loser]['L']} ({fmt_streak(int(records[loser]['streak']))}) | Elo {records[loser]['elo']}",
        "",
        f"Top {TOP_N} by Elo (min games: {MIN_GAMES})",
        "-" * 70,
        f"{'#':>2} {'C':>1}  {'Name':<18} {'W-L':<9} {'Win%':>6}  {'Stk':>4}  {'Elo':>7}  {'Ch':>3}",
        "-" * 70,
    ]
    top = build_top10_elo(records)
    champ = state.get("champion")
    for i, (name, w, l, g, elo_val) in enumerate(top, 1):
        cflag = "C" if name == champ else " "
        stk = fmt_streak(int(records.get(name, {}).get("streak", 0)))
        reigns = int(records.get(name, {}).get("reigns", 0))
        lines.append(
            f"{i:>2}. {cflag:>1}  {name:<18} {w:>3}-{l:<3}  {win_pct(w, l)*100:>5.1f}%  {stk:>4}  {elo_val:>7.2f}  {reigns:>3}"
        )
    lines += [
        "-" * 70,
        f"Champion: {champ} (Reign Def {state.get('reign_defenses', 0)})",
        f"Tag Champions: {state.get('tag_champions')} (Def {state.get('tag_defenses', 0)})",
    ]
    print("\n".join(lines))
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
