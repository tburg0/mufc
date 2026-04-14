import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
STATE_FILE = ROOT / "league_state.json"
RECORDS_FILE = ROOT / "records.json"
HISTORY_FILE = ROOT / "match_history.jsonl"
ROSTER_FILE = ROOT / "generated" / "published_roster.json"
MAPPING_FILE = ROOT / "generated" / "runtime_mapping.json"
SELECT_FILE = ROOT / "data" / "select.def"
CHARS_DIR = ROOT / "chars"
TAG_SERIES_FILE = ROOT / "tag_series.json"
ROYAL_FILE = ROOT / "royal_bracket.json"

MATCH_FILE = ROOT / "current_match.txt"
ARGS_FILE = ROOT / "mugen_args.txt"
CONTEXT_FILE = ROOT / "match_context.json"
TITLE_FLAG_FILE = ROOT / "is_title_match.txt"

ROUNDS_NORMAL = 2
ROUNDS_TITLE = 3
TAG_SERIES_TRIGGER_EVERY = 6
TITLE_EVERY_N_MATCHES = 5
ROYAL_TRIGGER_EVERY = 18
ROYAL_FIELD_SIZE = 8
STREAK_TITLE_THRESHOLD = 3
TOP_N_MAIN_EVENT = 10
DEBUT_PROTECTION_TOP_RANK_CUTOFF = 12
RECENT_MATCHUP_AVOID_WINDOW = 8
RIVALRY_MIN_MEETINGS = 2
RIVALRY_HISTORY_TAIL = 400
ELO_START = 1500.0


# -------------------------
# Generic helpers
# -------------------------

def load_json(path: Path, default: Any):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def write_text(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def team_key(a: str, b: str) -> str:
    x, y = sorted([a, b], key=lambda s: s.lower())
    return f"{x}+{y}"


def canonical_team_key(names: List[str]) -> str:
    if len(names) != 2:
        return "+".join(names)
    return team_key(names[0], names[1])


def read_recent_events(path: Path, limit: int) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    events: List[Dict[str, Any]] = []
    for raw in lines[-limit:]:
        raw = raw.strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            events.append(payload)
    return events


# -------------------------
# Roster loading
# -------------------------

def parse_select_entries() -> List[str]:
    if not SELECT_FILE.exists():
        return []

    entries: List[str] = []
    in_characters = False
    for raw in SELECT_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        lower = line.lower()
        if lower == "[characters]":
            in_characters = True
            continue
        if line.startswith("[") and lower != "[characters]":
            in_characters = False
            continue
        if not in_characters:
            continue
        if lower.startswith("randomselect"):
            continue
        token = line.split(",", 1)[0].strip()
        if token:
            entries.append(token)
    return entries


def resolve_native_runtime(entry: str) -> Optional[Tuple[str, str]]:
    """Return (display_name, runtime_argument)."""
    token = entry.replace("\\", "/").strip()
    if not token:
        return None

    # Prefer explicit folder component if present.
    folder = token.split("/", 1)[0].strip()
    if folder and (CHARS_DIR / folder).is_dir():
        return folder, token

    if (CHARS_DIR / token).is_dir():
        return token, token

    return None


def scan_native_character_dirs() -> List[Tuple[str, str]]:
    found: List[Tuple[str, str]] = []
    if not CHARS_DIR.exists():
        return found

    for child in sorted(CHARS_DIR.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir():
            continue
        name = child.name
        if name.startswith(".") or name.lower() in {"stages", "sound"}:
            continue
        if name.lower().startswith("custom_"):
            continue
        defs = list(child.glob("*.def"))
        if not defs:
            continue
        found.append((name, name))
    return found


def load_submitted_roster() -> List[Dict[str, Any]]:
    roster_blob = load_json(ROSTER_FILE, {"fighters": []})
    mapping = load_json(MAPPING_FILE, {})
    fighters: List[Dict[str, Any]] = []
    seen_names = set()

    for fighter in roster_blob.get("fighters", []):
        if not fighter.get("live"):
            continue
        name = str(fighter.get("name", "")).strip()
        if not name or name in seen_names:
            continue
        entry = mapping.get(name) or {}
        runtime = entry.get("runtime_character")
        if not runtime:
            continue
        runtime_token = str(runtime).replace("\\", "/").strip()
        runtime_folder = runtime_token.split("/", 1)[0].strip()
        runtime_dir = CHARS_DIR / runtime_folder
        runtime_def = runtime_dir / f"{runtime_folder}.def"
        if not runtime_folder or not runtime_dir.is_dir() or not runtime_def.exists():
            continue
        fighters.append({
            "name": name,
            "runtime": runtime,
            "source": "submitted",
            "fighter_id": fighter.get("fighter_id"),
            "palette_slot": int(entry.get("palette_slot", 1) or 1),
            "preferred_ai_level": int(entry.get("preferred_ai_level", 8) or 8),
        })
        seen_names.add(name)
    return fighters


def load_native_roster() -> List[Dict[str, Any]]:
    fighters: List[Dict[str, Any]] = []
    seen_names = set()

    # First honor select.def entries.
    for entry in parse_select_entries():
        resolved = resolve_native_runtime(entry)
        if not resolved:
            continue
        display_name, runtime = resolved
        if display_name in seen_names:
            continue
        fighters.append({
            "name": display_name,
            "runtime": runtime,
            "source": "native",
            "palette_slot": 1,
            "preferred_ai_level": 8,
        })
        seen_names.add(display_name)

    # Then supplement with any additional valid /chars folders.
    for display_name, runtime in scan_native_character_dirs():
        if display_name in seen_names:
            continue
        fighters.append({
            "name": display_name,
            "runtime": runtime,
            "source": "native",
            "palette_slot": 1,
            "preferred_ai_level": 8,
        })
        seen_names.add(display_name)

    return fighters


def load_roster() -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    submitted = load_submitted_roster()
    native = load_native_roster()

    merged: List[Dict[str, Any]] = []
    seen_names = set()
    for fighter in submitted + native:
        if fighter["name"] in seen_names:
            continue
        merged.append(fighter)
        seen_names.add(fighter["name"])

    counts = {
        "submitted": len(submitted),
        "native": len(native),
        "total": len(merged),
    }
    return merged, counts


# -------------------------
# Record helpers
# -------------------------

def get_record(records: Dict[str, Any], name: str) -> Dict[str, Any]:
    return records.get(name, {})


def games_played(records: Dict[str, Any], name: str) -> int:
    rec = get_record(records, name)
    return int(rec.get("W", 0)) + int(rec.get("L", 0))


def streak(records: Dict[str, Any], name: str) -> int:
    return int(get_record(records, name).get("streak", 0))


def elo(records: Dict[str, Any], name: str) -> float:
    return float(get_record(records, name).get("elo", ELO_START))


def leaderboard_names(records: Dict[str, Any], roster_names: List[str], team_mode: bool = False) -> List[str]:
    allowed = set(roster_names)
    rows: List[Tuple[str, float, int, int]] = []
    for name, rec in records.items():
        if team_mode != ("+" in name):
            continue
        if team_mode:
            # for teams, do not filter on single-roster names
            pass
        else:
            if name not in allowed:
                continue
        w = int(rec.get("W", 0))
        l = int(rec.get("L", 0))
        g = w + l
        rows.append((name, float(rec.get("elo", ELO_START)), g, int(rec.get("streak", 0))))
    rows.sort(key=lambda row: (row[1], row[2], row[3]), reverse=True)
    return [name for name, *_ in rows]


def top_two_contenders(records: Dict[str, Any], roster_names: List[str], champion: Optional[str]) -> List[str]:
    board = [n for n in leaderboard_names(records, roster_names) if n != champion]
    return board[:2]


def choose_debut_fighter(state: Dict[str, Any], roster: List[Dict[str, Any]], records: Dict[str, Any]) -> Optional[str]:
    roster_names = {f["name"] for f in roster}
    queue = [name for name in state.get("debut_queue", []) if name in roster_names and games_played(records, name) == 0]
    if queue:
        chosen = queue.pop(0)
        state["debut_queue"] = queue
        return chosen

    rookies = [name for name in roster_names if games_played(records, name) == 0]
    if not rookies:
        return None
    return random.choice(sorted(rookies, key=str.lower))


def choose_random_opponent(candidate_names: List[str], excluded: List[str], records: Dict[str, Any], prefer_veterans: bool = True) -> str:
    pool = [name for name in candidate_names if name not in excluded]
    if not pool:
        raise RuntimeError("Not enough fighters to select opponent")
    if prefer_veterans:
        vets = [name for name in pool if games_played(records, name) > 0]
        if vets:
            pool = vets
    return random.choice(pool)


def rank_of(name: str, records: Dict[str, Any], roster_names: List[str], team_mode: bool = False) -> Optional[int]:
    board = leaderboard_names(records, roster_names, team_mode=team_mode)
    try:
        return board.index(name) + 1
    except ValueError:
        return None


def is_main_event(name_a: str, name_b: str, records: Dict[str, Any], roster_names: List[str], team_mode: bool = False) -> bool:
    ra = rank_of(name_a, records, roster_names, team_mode=team_mode)
    rb = rank_of(name_b, records, roster_names, team_mode=team_mode)
    return bool(ra and rb and ra <= TOP_N_MAIN_EVENT and rb <= TOP_N_MAIN_EVENT)


def recent_singles_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        event for event in events
        if not event.get("tag_series") and not event.get("is_royal") and not event.get("royal")
    ]


def pair_key(a: str, b: str) -> Tuple[str, str]:
    return tuple(sorted((a, b), key=str.lower))


def recently_matched(a: str, b: str, events: List[Dict[str, Any]], limit: int = RECENT_MATCHUP_AVOID_WINDOW) -> bool:
    needle = pair_key(a, b)
    for event in reversed(recent_singles_events(events)):
        if pair_key(str(event.get("p1", "")), str(event.get("p2", ""))) == needle:
            return True
        limit -= 1
        if limit <= 0:
            break
    return False


def head_to_head_stats(a: str, b: str, events: List[Dict[str, Any]]) -> Tuple[int, int]:
    wins_a = 0
    wins_b = 0
    needle = pair_key(a, b)
    for event in recent_singles_events(events):
        if pair_key(str(event.get("p1", "")), str(event.get("p2", ""))) != needle:
            continue
        winner = str(event.get("winner", ""))
        if winner == a:
            wins_a += 1
        elif winner == b:
            wins_b += 1
    return wins_a, wins_b


def rivalry_candidates(roster_names: List[str], records: Dict[str, Any], events: List[Dict[str, Any]]) -> List[Tuple[float, str, str]]:
    seen: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for event in recent_singles_events(events):
        p1 = str(event.get("p1", "")).strip()
        p2 = str(event.get("p2", "")).strip()
        winner = str(event.get("winner", "")).strip()
        if not p1 or not p2 or p1 not in roster_names or p2 not in roster_names:
            continue
        key = pair_key(p1, p2)
        info = seen.setdefault(key, {"count": 0, "wins": {p1: 0, p2: 0}, "recent_bonus": 0})
        info["count"] += 1
        info["recent_bonus"] += max(0, 8 - info["count"])
        if winner:
            info["wins"][winner] = int(info["wins"].get(winner, 0)) + 1

    scored: List[Tuple[float, str, str]] = []
    for (a, b), info in seen.items():
        meetings = int(info["count"])
        if meetings < RIVALRY_MIN_MEETINGS:
            continue
        wins_a = int(info["wins"].get(a, 0))
        wins_b = int(info["wins"].get(b, 0))
        if abs(wins_a - wins_b) > 1:
            continue
        if recently_matched(a, b, events, limit=4):
            continue
        elo_gap = abs(elo(records, a) - elo(records, b))
        score = meetings * 4 + info["recent_bonus"] - (elo_gap / 80.0)
        scored.append((score, a, b))

    scored.sort(key=lambda item: item[0], reverse=True)
    return scored


def contender_pool(records: Dict[str, Any], roster_names: List[str], champion: Optional[str], top_n: int = 12) -> List[str]:
    board = leaderboard_names(records, roster_names)
    return [name for name in board[:top_n] if name != champion]


def choose_weighted_random(candidates: List[Tuple[float, str]]) -> Optional[str]:
    weighted = [(weight, value) for weight, value in candidates if weight > 0]
    if not weighted:
        return None
    total = sum(weight for weight, _ in weighted)
    pick = random.uniform(0, total)
    running = 0.0
    for weight, value in weighted:
        running += weight
        if pick <= running:
            return value
    return weighted[-1][1]


def choose_protected_debut_opponent(
    debut_name: str,
    roster_names: List[str],
    records: Dict[str, Any],
    events: List[Dict[str, Any]],
    champion: Optional[str],
) -> str:
    rank_map = {name: idx + 1 for idx, name in enumerate(leaderboard_names(records, roster_names))}
    debut_elo = elo(records, debut_name)
    weighted: List[Tuple[float, str]] = []

    for candidate in roster_names:
        if candidate == debut_name or candidate == champion:
            continue
        gp = games_played(records, candidate)
        if gp <= 0:
            continue
        if recently_matched(debut_name, candidate, events):
            continue
        rank = rank_map.get(candidate, 999)
        if rank <= DEBUT_PROTECTION_TOP_RANK_CUTOFF:
            continue
        score = 10.0
        score += min(gp, 12)
        score -= min(abs(elo(records, candidate) - debut_elo) / 60.0, 8.0)
        score -= max(0, streak(records, candidate) - 1) * 1.6
        weighted.append((score, candidate))

    chosen = choose_weighted_random(weighted)
    if chosen:
        return chosen
    return choose_random_opponent(roster_names, [debut_name], records, prefer_veterans=True)


def choose_contender_showcase(
    roster_names: List[str],
    records: Dict[str, Any],
    events: List[Dict[str, Any]],
    champion: Optional[str],
) -> Optional[Tuple[str, str]]:
    contenders = contender_pool(records, roster_names, champion, top_n=12)
    best: Optional[Tuple[float, str, str]] = None
    for index, a in enumerate(contenders):
        for b in contenders[index + 1:]:
            if recently_matched(a, b, events):
                continue
            gp_a = games_played(records, a)
            gp_b = games_played(records, b)
            if gp_a <= 0 or gp_b <= 0:
                continue
            rank_gap = abs((rank_of(a, records, roster_names) or 99) - (rank_of(b, records, roster_names) or 99))
            elo_gap = abs(elo(records, a) - elo(records, b))
            score = 16.0 - rank_gap - (elo_gap / 75.0) + (gp_a + gp_b) / 10.0
            if best is None or score > best[0]:
                best = (score, a, b)
    if best:
        return best[1], best[2]
    return None


def choose_rebound_match(
    roster_names: List[str],
    records: Dict[str, Any],
    events: List[Dict[str, Any]],
) -> Optional[Tuple[str, str]]:
    slumping = [
        name for name in roster_names
        if games_played(records, name) >= 2 and streak(records, name) <= -2
    ]
    if len(slumping) < 2:
        return None
    best: Optional[Tuple[float, str, str]] = None
    for index, a in enumerate(slumping):
        for b in slumping[index + 1:]:
            if recently_matched(a, b, events):
                continue
            elo_gap = abs(elo(records, a) - elo(records, b))
            score = 12.0 - (elo_gap / 80.0) + abs(streak(records, a)) + abs(streak(records, b))
            if best is None or score > best[0]:
                best = (score, a, b)
    if best:
        return best[1], best[2]
    return None


# -------------------------
# Match builders
# -------------------------

def choose_world_title_match(state: Dict[str, Any], roster: List[Dict[str, Any]], records: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    roster_names = [f["name"] for f in roster]
    champion = state.get("champion")

    # Vacant title logic
    if not champion or champion not in roster_names:
        contenders = leaderboard_names(records, roster_names)
        if len(contenders) >= 2:
            return {
                "type": "SINGLES",
                "p1": contenders[0],
                "p2": contenders[1],
                "is_world_title": True,
                "title_reason": "Vacant championship match (#1 vs #2)",
                "main_event": True,
            }
        return None

    # 1) Royal winner queue retains priority when present.
    royal = state.get("royal_winner_queue")
    if royal and royal in roster_names and royal != champion:
        return {
            "type": "SINGLES",
            "p1": champion,
            "p2": royal,
            "is_world_title": True,
            "title_reason": "Royal winner title shot",
            "main_event": True,
        }

    # 2) Every N matches, force champ vs current #2 contender.
    next_match_num = int(state.get("match_count", 0)) + 1
    if next_match_num % TITLE_EVERY_N_MATCHES == 0:
        contenders = top_two_contenders(records, roster_names, champion)
        if contenders:
            challenger = contenders[0]
            return {
                "type": "SINGLES",
                "p1": champion,
                "p2": challenger,
                "is_world_title": True,
                "title_reason": f"Scheduled title defense (every {TITLE_EVERY_N_MATCHES} matches)",
                "main_event": True,
            }

    # 3) Hot streak contender gets a title shot.
    contenders = [
        name for name in roster_names
        if name != champion and games_played(records, name) > 0 and streak(records, name) >= STREAK_TITLE_THRESHOLD
    ]
    if contenders:
        contenders.sort(
            key=lambda name: (streak(records, name), elo(records, name), games_played(records, name)),
            reverse=True
        )
        challenger = contenders[0]
        return {
            "type": "SINGLES",
            "p1": champion,
            "p2": challenger,
            "is_world_title": True,
            "title_reason": f"{challenger} earned a title shot on a {streak(records, challenger)}-fight win streak",
            "main_event": True,
        }

    return None

def active_royal_match(roster_names: List[str]) -> Optional[Dict[str, Any]]:
    bracket = load_json(ROYAL_FILE, {"active": False})
    if not bracket.get("active"):
        return None

    round_name = str(bracket.get("round") or "").strip()
    round_map = {
        "QF": bracket.get("qf", []),
        "SF": bracket.get("sf", []),
        "F": bracket.get("final", []),
    }
    pairings = round_map.get(round_name, [])
    winners_qf = set(bracket.get("winners_qf", []))
    winners_sf = set(bracket.get("winners_sf", []))

    for pair in pairings:
        if not isinstance(pair, list) or len(pair) != 2:
            continue
        p1, p2 = str(pair[0]).strip(), str(pair[1]).strip()
        if p1 not in roster_names or p2 not in roster_names:
            continue
        if round_name == "QF" and (p1 in winners_qf or p2 in winners_qf):
            continue
        if round_name == "SF" and (p1 in winners_sf or p2 in winners_sf):
            continue
        if round_name == "F" and bracket.get("winner"):
            continue
        return {
            "type": "SINGLES",
            "p1": p1,
            "p2": p2,
            "is_royal": True,
            "royal_round": round_name,
            "title_reason": "Winner earns a world title shot",
            "main_event": round_name == "F",
            "main_event_reason": f"Royal {round_name}",
        }
    return None


def maybe_start_royal_tournament(state: Dict[str, Any], roster: List[Dict[str, Any]], records: Dict[str, Any], events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if state.get("royal_winner_queue"):
        return None
    next_match_num = int(state.get("match_count", 0)) + 1
    if next_match_num % ROYAL_TRIGGER_EVERY != 0:
        return None

    roster_names = [f["name"] for f in roster]
    champion = state.get("champion")
    contenders = contender_pool(records, roster_names, champion, top_n=max(ROYAL_FIELD_SIZE, 12))
    rookies = [name for name in roster_names if games_played(records, name) <= 1 and name not in contenders and name != champion]
    field: List[str] = []

    for name in contenders:
        if name not in field:
            field.append(name)
        if len(field) >= max(ROYAL_FIELD_SIZE - 2, 4):
            break

    for name in rookies:
        if len(field) >= ROYAL_FIELD_SIZE:
            break
        if name not in field:
            field.append(name)

    for name in leaderboard_names(records, roster_names):
        if len(field) >= ROYAL_FIELD_SIZE:
            break
        if name != champion and name not in field:
            field.append(name)

    if len(field) < 4:
        return None

    if len(field) > ROYAL_FIELD_SIZE:
        field = field[:ROYAL_FIELD_SIZE]
    random.shuffle(field)

    qf = [[field[i], field[i + 1]] for i in range(0, len(field), 2) if i + 1 < len(field)]
    if len(qf) < 2:
        return None

    bracket = {
        "active": True,
        "created_ts": __import__("time").time(),
        "round": "QF",
        "field": field,
        "qf": qf,
        "sf": [],
        "final": [],
        "winner": None,
        "winners_qf": [],
        "winners_sf": [],
    }
    save_json(ROYAL_FILE, bracket)
    return active_royal_match(roster_names)


def choose_regular_singles(state: Dict[str, Any], roster: List[Dict[str, Any]], records: Dict[str, Any], events: List[Dict[str, Any]]) -> Dict[str, Any]:
    roster_names = [f["name"] for f in roster]
    champion = state.get("champion")

    debut_name = choose_debut_fighter(state, roster, records)
    if debut_name:
        opponent = choose_protected_debut_opponent(debut_name, roster_names, records, events, champion)
        return {
            "type": "SINGLES",
            "p1": debut_name,
            "p2": opponent,
            "is_world_title": False,
            "is_debut": True,
            "debut_fighter": debut_name,
            "title_reason": None,
            "main_event": False,
            "main_event_reason": None,
            "booking_reason": "Protected debut showcase",
        }

    rivalry = rivalry_candidates(roster_names, records, events)
    if rivalry and random.random() < 0.45:
        _, p1, p2 = rivalry[0]
        return {
            "type": "SINGLES",
            "p1": p1,
            "p2": p2,
            "is_world_title": False,
            "is_debut": False,
            "debut_fighter": None,
            "title_reason": None,
            "main_event": is_main_event(p1, p2, records, roster_names, team_mode=False),
            "main_event_reason": "Rivalry rematch",
            "booking_reason": "Rivalry rematch",
        }

    contender = choose_contender_showcase(roster_names, records, events, champion)
    if contender and random.random() < 0.55:
        p1, p2 = contender
        return {
            "type": "SINGLES",
            "p1": p1,
            "p2": p2,
            "is_world_title": False,
            "is_debut": False,
            "debut_fighter": None,
            "title_reason": None,
            "main_event": True,
            "main_event_reason": "Contender showcase",
            "booking_reason": "Contender showcase",
        }

    rebound = choose_rebound_match(roster_names, records, events)
    if rebound and random.random() < 0.35:
        p1, p2 = rebound
        return {
            "type": "SINGLES",
            "p1": p1,
            "p2": p2,
            "is_world_title": False,
            "is_debut": False,
            "debut_fighter": None,
            "title_reason": None,
            "main_event": False,
            "main_event_reason": None,
            "booking_reason": "Redemption bout",
        }

    selectable = [name for name in roster_names if name != champion]
    p1 = random.choice(selectable or roster_names)
    recent_opponents = [
        str(event.get("p2" if str(event.get("p1")) == p1 else "p1", "")).strip()
        for event in reversed(recent_singles_events(events))
        if p1 in (str(event.get("p1", "")).strip(), str(event.get("p2", "")).strip())
    ][:RECENT_MATCHUP_AVOID_WINDOW]
    exclusions = [p1] + recent_opponents
    p2 = choose_random_opponent(roster_names, exclusions, records, prefer_veterans=False)
    return {
        "type": "SINGLES",
        "p1": p1,
        "p2": p2,
        "is_world_title": False,
        "is_debut": False,
        "debut_fighter": None,
        "title_reason": None,
        "main_event": is_main_event(p1, p2, records, roster_names, team_mode=False),
        "main_event_reason": "Top-10 vs Top-10" if is_main_event(p1, p2, records, roster_names, team_mode=False) else None,
        "booking_reason": "Open booking",
    }


def active_tag_series_match(records: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    series = load_json(TAG_SERIES_FILE, {"active": False})
    if not series.get("active"):
        return None

    leg = int(series.get("leg", 1))
    team_a = series.get("teamA", [])
    team_b = series.get("teamB", [])
    if len(team_a) != 2 or len(team_b) != 2:
        return None

    used_pairs = set()
    for legobj in series.get("legs", []):
        p1 = legobj.get("p1")
        p2 = legobj.get("p2")
        if p1 and p2:
            used_pairs.add(tuple(sorted((p1, p2), key=str.lower)))

    candidate_pairs = [
        (team_a[0], team_b[0]),
        (team_a[1], team_b[1]),
        (team_a[0], team_b[1]),
        (team_a[1], team_b[0]),
    ]
    fresh_pairs = [pair for pair in candidate_pairs if tuple(sorted(pair, key=str.lower)) not in used_pairs]
    if not fresh_pairs:
        fresh_pairs = candidate_pairs
    p1, p2 = random.choice(fresh_pairs)

    # Persist chosen fighters into the series leg for overlay consistency.
    for legobj in series.get("legs", []):
        if int(legobj.get("leg", 0)) == leg:
            legobj["p1"] = p1
            legobj["p2"] = p2
            break
    save_json(TAG_SERIES_FILE, series)

    return {
        "type": "SINGLES",
        "p1": p1,
        "p2": p2,
        "is_tag_series": True,
        "tag_series_id": series.get("id"),
        "tag_leg": leg,
        "is_tag_title": bool(series.get("is_tag_title", False)),
        "main_event": bool(series.get("is_tag_title", False)),
        "main_event_reason": "Tag title series" if series.get("is_tag_title") else None,
    }


def maybe_start_tag_series(state: Dict[str, Any], roster: List[Dict[str, Any]], records: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    next_match_num = int(state.get("match_count", 0)) + 1
    if next_match_num % TAG_SERIES_TRIGGER_EVERY != 0:
        return None

    roster_names = [f["name"] for f in roster]
    if len(roster_names) < 4:
        return None

    next_series_num = int(state.get("tag_series_count", 0)) + 1
    champs = state.get("tag_champions") or []

    is_tag_title = False
    team_a: List[str]
    team_b: List[str]

    team_leaderboard = leaderboard_names(records, roster_names, team_mode=True)

    if next_series_num % TITLE_EVERY_N_MATCHES == 0 and len(champs) == 2:
        champ_key = team_key(champs[0], champs[1])
        contenders = [name for name in team_leaderboard if name != champ_key]
        challenger_key = contenders[0] if contenders else None
        if challenger_key and "+" in challenger_key:
            team_a = list(champs)
            team_b = challenger_key.split("+", 1)
            is_tag_title = True
        else:
            team_a = random.sample(roster_names, 2)
            remaining = [name for name in roster_names if name not in team_a]
            team_b = random.sample(remaining, 2)
    else:
        team_a = random.sample(roster_names, 2)
        remaining = [name for name in roster_names if name not in team_a]
        team_b = random.sample(remaining, 2)

        # Hot team streak title shot.
        if len(champs) == 2:
            champ_key = team_key(champs[0], champs[1])
            hot_teams = [name for name in team_leaderboard if name != champ_key and streak(records, name) >= STREAK_TITLE_THRESHOLD]
            if hot_teams:
                challenger_key = hot_teams[0]
                team_a = list(champs)
                team_b = challenger_key.split("+", 1)
                is_tag_title = True

    if len(team_a) != 2 or len(team_b) != 2:
        return None

    series_id = random.randrange(10**12, 10**13 - 1)
    series = {
        "active": True,
        "id": series_id,
        "teamA": team_a,
        "teamB": team_b,
        "teamA_key": team_key(team_a[0], team_a[1]),
        "teamB_key": team_key(team_b[0], team_b[1]),
        "scoreA": 0,
        "scoreB": 0,
        "leg": 1,
        "is_tag_title": is_tag_title,
        "created_ts": __import__("time").time(),
        "legs": [
            {"leg": 1, "p1": None, "p2": None, "winner": None, "result": None},
            {"leg": 2, "p1": None, "p2": None, "winner": None, "result": None},
            {"leg": 3, "p1": None, "p2": None, "winner": None, "result": None, "tiebreak": True},
        ],
    }
    save_json(TAG_SERIES_FILE, series)
    return active_tag_series_match(records)


# -------------------------
# Orchestration
# -------------------------

def fighter_lookup(roster: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    for fighter in roster:
        for alias in (
            fighter.get("name"),
            fighter.get("runtime"),
            fighter.get("fighter_id"),
        ):
            key = str(alias or "").strip()
            if key:
                lookup[key] = fighter
    return lookup


def canonical_fighter_name(name: Optional[str], lookup: Dict[str, Dict[str, Any]]) -> Optional[str]:
    key = str(name or "").strip()
    if not key:
        return None
    fighter = lookup.get(key)
    if fighter:
        return fighter["name"]
    return key


def normalize_tag_series_state(lookup: Dict[str, Dict[str, Any]]) -> None:
    series = load_json(TAG_SERIES_FILE, {"active": False})
    if not series.get("active"):
        return

    changed = False

    for team_field in ("teamA", "teamB"):
        raw_team = series.get(team_field, [])
        normalized_team = [canonical_fighter_name(name, lookup) for name in raw_team]
        if normalized_team != raw_team:
            series[team_field] = normalized_team
            changed = True

    team_a = series.get("teamA", [])
    team_b = series.get("teamB", [])
    if len(team_a) == 2:
        desired = canonical_team_key(team_a)
        if series.get("teamA_key") != desired:
            series["teamA_key"] = desired
            changed = True
    if len(team_b) == 2:
        desired = canonical_team_key(team_b)
        if series.get("teamB_key") != desired:
            series["teamB_key"] = desired
            changed = True

    for leg in series.get("legs", []):
        for field in ("p1", "p2", "winner"):
            raw_value = leg.get(field)
            normalized_value = canonical_fighter_name(raw_value, lookup)
            if normalized_value != raw_value:
                leg[field] = normalized_value
                changed = True

    if changed:
        save_json(TAG_SERIES_FILE, series)


def invalidate_active_tag_series(reason: str) -> None:
    series = load_json(TAG_SERIES_FILE, {"active": False})
    if not series.get("active"):
        return
    series["active"] = False
    series["invalid_reason"] = reason
    save_json(TAG_SERIES_FILE, series)


def context_fighters_resolvable(ctx: Optional[Dict[str, Any]], lookup: Dict[str, Dict[str, Any]]) -> bool:
    if not ctx:
        return False
    p1 = str(ctx.get("p1") or "").strip()
    p2 = str(ctx.get("p2") or "").strip()
    return bool(p1 and p2 and p1 in lookup and p2 in lookup)


def active_tag_series_members(lookup: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    series = load_json(TAG_SERIES_FILE, {"active": False})
    if not series.get("active"):
        return True, []

    names: List[str] = []
    for team_field in ("teamA", "teamB"):
        for name in series.get(team_field, []):
            key = str(name or "").strip()
            if key:
                names.append(key)

    missing = [name for name in names if name not in lookup]
    return not missing, missing


def runtime_arg_for(fighter: Dict[str, Any]) -> str:
    return fighter["runtime"]


def main() -> None:
    state = load_json(STATE_FILE, {
        "match_count": 0,
        "champion": None,
        "debut_queue": [],
        "royal_winner_queue": None,
        "tag_champions": None,
        "tag_series_count": 0,
    })
    records = load_json(RECORDS_FILE, {})
    recent_events = read_recent_events(HISTORY_FILE, RIVALRY_HISTORY_TAIL)
    roster, counts = load_roster()
    if not roster:
        print("No fighters available.")
        return

    lookup = fighter_lookup(roster)
    normalize_tag_series_state(lookup)
    roster_names = [f["name"] for f in roster]

    tag_series_ok, missing_members = active_tag_series_members(lookup)
    if not tag_series_ok:
        invalidate_active_tag_series(f"Missing roster entries for tag series teams: {', '.join(missing_members)}")

    ctx = active_tag_series_match(records)
    if ctx is None:
        ctx = active_royal_match(roster_names)
    if ctx is not None and not context_fighters_resolvable(ctx, lookup):
        missing = [name for name in (ctx.get("p1"), ctx.get("p2")) if str(name or "").strip() not in lookup]
        invalidate_active_tag_series(f"Missing roster entries for active tag series: {', '.join(missing)}")
        ctx = None
    if ctx is None:
        ctx = choose_world_title_match(state, roster, records)
    if ctx is None:
        ctx = maybe_start_royal_tournament(state, roster, records, recent_events)
    if ctx is None:
        ctx = maybe_start_tag_series(state, roster, records)
        if ctx is not None and not context_fighters_resolvable(ctx, lookup):
            missing = [name for name in (ctx.get("p1"), ctx.get("p2")) if str(name or "").strip() not in lookup]
            raise RuntimeError(f"Generated tag series includes unavailable fighters: {', '.join(missing)}")
    if ctx is None:
        ctx = choose_regular_singles(state, roster, records, recent_events)

    p1 = ctx["p1"]
    p2 = ctx["p2"]
    fighter1 = lookup[p1]
    fighter2 = lookup[p2]
    r1 = runtime_arg_for(fighter1)
    r2 = runtime_arg_for(fighter2)
    ai1 = int(fighter1.get("preferred_ai_level", 8) or 8)
    ai2 = int(fighter2.get("preferred_ai_level", 8) or 8)

    ctx.setdefault("is_world_title", False)
    ctx.setdefault("is_tag_series", False)
    ctx.setdefault("is_tag_title", False)
    ctx.setdefault("is_debut", False)
    ctx.setdefault("debut_fighter", None)
    ctx.setdefault("royal_round", None)
    ctx.setdefault("is_royal", False)
    ctx.setdefault("main_event", False)
    ctx.setdefault("main_event_reason", None)

    if not ctx["main_event"]:
        if ctx["is_world_title"]:
            ctx["main_event"] = True
            ctx["main_event_reason"] = ctx.get("title_reason") or "World title fight"
        elif ctx["is_tag_title"]:
            ctx["main_event"] = True
            ctx["main_event_reason"] = "Tag title series"
        elif is_main_event(p1, p2, records, roster_names, team_mode=False):
            ctx["main_event"] = True
            ctx["main_event_reason"] = "Top-10 vs Top-10"

    rounds = ROUNDS_TITLE if (ctx["is_world_title"] or ctx["is_tag_title"]) else ROUNDS_NORMAL
    ctx["p1_runtime"] = r1
    ctx["p2_runtime"] = r2
    ctx["match_number"] = int(state.get("match_count", 0)) + 1
    ctx["roster_counts"] = counts

    write_text(MATCH_FILE, f"{p1},{p2}")
    write_text(ARGS_FILE, f"-p1 {r1} -p2 {r2} -p1.ai {ai1} -p2.ai {ai2} -rounds {rounds}")
    write_text(TITLE_FLAG_FILE, "1" if (ctx["is_world_title"] or ctx["is_tag_title"]) else "0")
    save_json(CONTEXT_FILE, ctx)

    print("\n=== MATCH GENERATED ===")
    print(f"{p1} vs {p2}")
    print(f"Runtime: {r1} vs {r2}")
    print(f"Roster pool: {counts['total']} total ({counts['submitted']} submitted, {counts['native']} native)")
    print(f"Rounds: {rounds}")
    print(f"Using args: -p1 {r1} -p2 {r2} -p1.ai {ai1} -p2.ai {ai2} -rounds {rounds}")
    if ctx["is_debut"]:
        print(f"DEBUT MATCH: {ctx['debut_fighter']}")
    if ctx["is_world_title"]:
        print(f"WORLD TITLE: {ctx.get('title_reason')}")
    if ctx["is_tag_series"]:
        print(f"TAG SERIES LEG {ctx.get('tag_leg')}")
        if ctx["is_tag_title"]:
            print("TAG TITLE SERIES")
    if ctx["main_event"]:
        print(f"MAIN EVENT: {ctx.get('main_event_reason') or 'Yes'}")


if __name__ == "__main__":
    main()
