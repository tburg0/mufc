import json
import os
from typing import Any, Dict, List, Optional, Tuple

MATCH_FILE = "current_match.txt"
RECORDS_FILE = "records.json"
STATE_FILE = "league_state.json"
HISTORY_FILE = "match_history.jsonl"
OUT_FILE = "prematch.txt"
TITLE_FLAG_FILE = "is_title_match.txt"
CONTEXT_FILE = "match_context.json"
TAG_SERIES_FILE = "tag_series.json"

TAIL_LINES = 6000
ELO_START = 1500.0
TOP_N_MAIN_EVENT = 10


def load_json(path: str, default: Any):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fmt_streak(s: int) -> str:
    if s > 0:
        return f"W{s}"
    if s < 0:
        return f"L{abs(s)}"
    return "-"


def win_pct(w: int, l: int) -> float:
    g = w + l
    return (w / g) if g else 0.0


def read_tail_lines(path: str, n: int) -> List[str]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()[-n:]


def read_events(path: str, n: int) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for line in read_tail_lines(path, n):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue
    return events


def elo_expected(a: float, b: float) -> float:
    return 1.0 / (1.0 + (10 ** ((b - a) / 400.0)))


def moneyline_from_prob(p: float) -> int:
    p = min(max(p, 0.0001), 0.9999)
    if p >= 0.5:
        return -int(round(100 * p / (1 - p)))
    return int(round(100 * (1 - p) / p))


def team_key(a: str, b: str) -> str:
    x, y = sorted([a, b], key=lambda s: s.lower())
    return f"{x}+{y}"


def get_record(records: Dict[str, Any], name: str) -> Tuple[int, int, int, float]:
    r = records.get(name, {})
    return int(r.get("W", 0)), int(r.get("L", 0)), int(r.get("streak", 0)), float(r.get("elo", ELO_START))


def leaderboard_map(records: Dict[str, Any], team_mode: bool = False) -> Dict[str, int]:
    rows = []
    for name, rec in records.items():
        if team_mode != ("+" in name):
            continue
        w = int(rec.get("W", 0))
        l = int(rec.get("L", 0))
        g = w + l
        if g <= 0:
            continue
        rows.append((name, float(rec.get("elo", ELO_START)), g))
    rows.sort(key=lambda row: (row[1], row[2]), reverse=True)
    return {name: idx + 1 for idx, (name, _, _) in enumerate(rows)}


def last5_form(events: List[Dict[str, Any]], fighter: str) -> str:
    res: List[str] = []
    for event in reversed(events):
        if event.get("tag_series"):
            continue
        if fighter not in (event.get("p1"), event.get("p2")):
            continue
        winner = event.get("winner")
        loser = event.get("loser")
        if fighter == winner:
            res.append("W")
        elif fighter == loser:
            res.append("L")
        if len(res) == 5:
            break
    return " ".join(reversed(res)) if res else "-"


def h2h(events: List[Dict[str, Any]], a: str, b: str) -> Tuple[int, int]:
    a_wins = 0
    b_wins = 0
    for event in events:
        if event.get("tag_series"):
            continue
        if {event.get("p1"), event.get("p2")} != {a, b}:
            continue
        winner = event.get("winner")
        if winner == a:
            a_wins += 1
        elif winner == b:
            b_wins += 1
    return a_wins, b_wins


def last5_form_team(events: List[Dict[str, Any]], key: str) -> str:
    res: List[str] = []
    for event in reversed(events):
        te = event.get("tag_event") or {}
        if te.get("type") != "TAG_SERIES_COMPLETE":
            continue
        if key not in (te.get("teamA_key"), te.get("teamB_key")):
            continue
        winner_team = te.get("series_winner_team")
        winner_key = te.get("teamA_key") if winner_team == "A" else te.get("teamB_key")
        res.append("W" if winner_key == key else "L")
        if len(res) == 5:
            break
    return " ".join(reversed(res)) if res else "-"


def h2h_team(events: List[Dict[str, Any]], key_a: str, key_b: str) -> Tuple[int, int]:
    a_wins = 0
    b_wins = 0
    for event in events:
        te = event.get("tag_event") or {}
        if te.get("type") != "TAG_SERIES_COMPLETE":
            continue
        if {te.get("teamA_key"), te.get("teamB_key")} != {key_a, key_b}:
            continue
        winner_team = te.get("series_winner_team")
        winner_key = te.get("teamA_key") if winner_team == "A" else te.get("teamB_key")
        if winner_key == key_a:
            a_wins += 1
        elif winner_key == key_b:
            b_wins += 1
    return a_wins, b_wins


def main() -> None:
    parts = [x.strip() for x in open(MATCH_FILE, "r", encoding="utf-8").read().strip().split(",") if x.strip()]
    if len(parts) < 2:
        raise RuntimeError("current_match.txt missing fighters")

    records: Dict[str, Any] = load_json(RECORDS_FILE, {})
    state: Dict[str, Any] = load_json(STATE_FILE, {})
    ctx: Dict[str, Any] = load_json(CONTEXT_FILE, {})
    events = read_events(HISTORY_FILE, TAIL_LINES)
    rank_map = leaderboard_map(records, team_mode=False)
    team_rank_map = leaderboard_map(records, team_mode=True)

    is_world_title = bool(ctx.get("is_world_title", False))
    is_royal = bool(ctx.get("is_royal", False))
    is_grand_prix = bool(ctx.get("is_grand_prix", False))
    is_tag_series = bool(ctx.get("is_tag_series", False))
    is_tag_title = bool(ctx.get("is_tag_title", False))
    is_debut = bool(ctx.get("is_debut", False))
    debut_fighter = ctx.get("debut_fighter")
    main_event = bool(ctx.get("main_event", False))
    main_event_reason = ctx.get("main_event_reason")
    booking_reason = ctx.get("booking_reason")

    lines_out: List[str] = []

    if is_tag_series:
        series = load_json(TAG_SERIES_FILE, {"active": False})
        team_a = series.get("teamA", [])
        team_b = series.get("teamB", [])
        key_a = series.get("teamA_key") or team_key(team_a[0], team_a[1])
        key_b = series.get("teamB_key") or team_key(team_b[0], team_b[1])
        leg = int(ctx.get("tag_leg", 1))
        score_a = int(series.get("scoreA", 0))
        score_b = int(series.get("scoreB", 0))

        w_a, l_a, s_a, elo_a = get_record(records, key_a)
        w_b, l_b, s_b, elo_b = get_record(records, key_b)
        p_a = elo_expected(elo_a, elo_b)
        p_b = 1.0 - p_a

        form_a = last5_form_team(events, key_a)
        form_b = last5_form_team(events, key_b)
        h2a, h2b = h2h_team(events, key_a, key_b)

        rank_a = f"#{team_rank_map[key_a]} " if key_a in team_rank_map else ""
        rank_b = f"#{team_rank_map[key_b]} " if key_b in team_rank_map else ""

        lines_out.append(f"PRE-MATCH: TAG SERIES (Leg {leg}/3) | {rank_a}{key_a} vs {rank_b}{key_b} [Series {score_a}-{score_b}]")
        if is_tag_title:
            lines_out.append("🏆🏆🏆 TAG TEAM CHAMPIONSHIP (Series) 🏆🏆🏆")

        lines_out.append(
            f"RECORDS:   {key_a}: {w_a}-{l_a} GP{w_a+l_a} {win_pct(w_a, l_a)*100:.1f}% ({fmt_streak(s_a)}) | Elo {elo_a:.1f} [{moneyline_from_prob(p_a)}]"
        )
        lines_out.append(
            f"          {key_b}: {w_b}-{l_b} GP{w_b+l_b} {win_pct(w_b, l_b)*100:.1f}% ({fmt_streak(s_b)}) | Elo {elo_b:.1f} [{moneyline_from_prob(p_b)}]"
        )
        lines_out.append(f"FORM L5:   {key_a}: {form_a}   ||   {key_b}: {form_b}")
        lines_out.append(f"H2H:       {key_a} {h2a}-{h2b} {key_b}")
        lines_out.append(f"ODDS:      Favorite: {(key_a if p_a >= p_b else key_b)} ({max(p_a, p_b)*100:.1f}%)")

        me_text = "Yes"
        if main_event_reason:
            me_text = main_event_reason
        elif is_tag_title:
            me_text = "Tag title series"
        elif key_a in team_rank_map and key_b in team_rank_map and team_rank_map[key_a] <= TOP_N_MAIN_EVENT and team_rank_map[key_b] <= TOP_N_MAIN_EVENT:
            me_text = "Top-10 tag series"
        lines_out.append(f"MAIN EVT:  {me_text if main_event or me_text != 'Yes' else '—'}")
        lines_out.append(f"Tag Champs: {state.get('tag_champions')} (Def {state.get('tag_defenses', 0)})")
        open(TITLE_FLAG_FILE, "w", encoding="utf-8").write("1" if is_tag_title else "0")
    else:
        p1, p2 = parts[0], parts[1]
        rank1 = f"#{rank_map[p1]} " if p1 in rank_map else ""
        rank2 = f"#{rank_map[p2]} " if p2 in rank_map else ""
        lines_out.append(f"PRE-MATCH: {rank1}{p1} vs {rank2}{p2}")

        if is_debut and debut_fighter:
            lines_out.append(f"🔥 DEBUT MATCH: {debut_fighter}")
        if is_royal and ctx.get("royal_round"):
            lines_out.append(f"⚔️ ROYAL TOURNAMENT: {ctx.get('royal_round')} (Winner earns title shot)")
        if is_grand_prix and ctx.get("grand_prix_round"):
            lines_out.append(f"🏁 GRAND PRIX: {ctx.get('grand_prix_round')} (Winner earns title shot)")
        if is_world_title:
            lines_out.append("🏆🏆🏆 CHAMPIONSHIP FIGHT! 🏆🏆🏆")
            if ctx.get("title_reason"):
                lines_out.append(f"TITLE NOTE: {ctx['title_reason']}")
            open(TITLE_FLAG_FILE, "w", encoding="utf-8").write("1")
        else:
            open(TITLE_FLAG_FILE, "w", encoding="utf-8").write("0")

        w1, l1, s1, e1 = get_record(records, p1)
        w2, l2, s2, e2 = get_record(records, p2)
        p = elo_expected(e1, e2)

        lines_out.append(f"RECORDS:   {p1}: {w1}-{l1} GP{w1+l1} {win_pct(w1, l1)*100:.1f}% ({fmt_streak(s1)}) | Elo {e1:.1f} [{moneyline_from_prob(p)}]")
        lines_out.append(f"          {p2}: {w2}-{l2} GP{w2+l2} {win_pct(w2, l2)*100:.1f}% ({fmt_streak(s2)}) | Elo {e2:.1f} [{moneyline_from_prob(1.0-p)}]")
        lines_out.append(f"FORM L5:   {p1}: {last5_form(events, p1)}   ||   {p2}: {last5_form(events, p2)}")
        a_wins, b_wins = h2h(events, p1, p2)
        lines_out.append(f"H2H:       {p1} {a_wins}-{b_wins} {p2}")
        lines_out.append(f"ODDS:      Favorite: {(p1 if p >= 0.5 else p2)} ({max(p, 1.0-p)*100:.1f}%)")
        if booking_reason:
            lines_out.append(f"STORY:     {booking_reason}")

        me_text = "—"
        if main_event_reason:
            me_text = main_event_reason
        elif main_event:
            me_text = "Top-10 vs Top-10"
        lines_out.append(f"MAIN EVT:  {me_text}")
        lines_out.append(f"Champion:  {state.get('champion')}")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines_out) + "\n")


if __name__ == "__main__":
    main()
