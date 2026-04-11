import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
STATE_FILE = ROOT / "league_state.json"
RECORDS_FILE = ROOT / "records.json"
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
STREAK_TITLE_THRESHOLD = 3
TOP_N_MAIN_EVENT = 10
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
        contenders.sort(key=lambda name: (streak(records, name), elo(records, name), games_played(records, name)), reverse=True)
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


def choose_regular_singles(state: Dict[str, Any], roster: List[Dict[str, Any]], records: Dict[str, Any]) -> Dict[str, Any]:
    roster_names = [f["name"] for f in roster]

    debut_name = choose_debut_fighter(state, roster, records)
    if debut_name:
        opponent = choose_random_opponent(roster_names, [debut_name], records, prefer_veterans=True)
        return {
            "type": "SINGLES",
            "p1": debut_name,
            "p2": opponent,
            "is_world_title": False,
            "is_debut": True,
            "debut_fighter": debut_name,
            "title_reason": None,
            "main_event": False,
        }

    p1 = random.choice(roster_names)
    p2 = choose_random_opponent(roster_names, [p1], records, prefer_veterans=False)
    return {
        "type": "SINGLES",
        "p1": p1,
        "p2": p2,
        "is_world_title": False,
        "is_debut": False,
        "debut_fighter": None,
        "title_reason": None,
        "main_event": is_main_event(p1, p2, records, roster_names, team_mode=False),
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
    if ctx is not None and not context_fighters_resolvable(ctx, lookup):
        missing = [name for name in (ctx.get("p1"), ctx.get("p2")) if str(name or "").strip() not in lookup]
        invalidate_active_tag_series(f"Missing roster entries for active tag series: {', '.join(missing)}")
        ctx = None
    if ctx is None:
        ctx = choose_world_title_match(state, roster, records)
    if ctx is None:
        ctx = maybe_start_tag_series(state, roster, records)
        if ctx is not None and not context_fighters_resolvable(ctx, lookup):
            missing = [name for name in (ctx.get("p1"), ctx.get("p2")) if str(name or "").strip() not in lookup]
            raise RuntimeError(f"Generated tag series includes unavailable fighters: {', '.join(missing)}")
    if ctx is None:
        ctx = choose_regular_singles(state, roster, records)

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
