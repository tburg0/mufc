async function fetchText(path){
  const r = await fetch("../" + path + "?t=" + Date.now(), { cache:"no-store" });
  return await r.text();
}

async function fetchJSON(path){
  const r = await fetch("../" + path + "?t=" + Date.now(), { cache:"no-store" });
  return await r.json();
}

function setText(id, val){
  const el = document.getElementById(id);
  if (el) el.textContent = (val ?? "—");
}

function show(id, on){
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.toggle("hidden", !on);
}

function getRec(records, name){
  const r = records?.[name] || {};
  return {
    w: Number(r.W ?? 0),
    l: Number(r.L ?? 0),
    elo: Number(r.elo ?? 1500)
  };
}

function buildRankMap(records){
  if(!records) return {};
  const arr = Object.entries(records)
    .map(([name, r]) => ({
      name,
      elo: Number(r.elo ?? 1500),
      games: Number(r.W ?? 0) + Number(r.L ?? 0)
    }))
    .filter(x => x.games > 0)
    .sort((a,b) => b.elo - a.elo);

  const map = {};
  arr.forEach((x,i)=>{ map[x.name] = i + 1; });
  return map;
}

function tierTag(rank, games){
  if (games < 5) return "Prospect";
  if (rank && rank <= 10) return "Elite";
  if (rank && rank <= 25) return "Contender";
  return "Roster";
}

function normKey(name){
  return (name || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "")
    .replace(/[^\w\-]/g, "");
}

function unwrapMeta(metaWrap){
  if (!metaWrap) return {};
  if (metaWrap.fighters && typeof metaWrap.fighters === "object") return metaWrap.fighters;
  return metaWrap;
}

function metaFor(meta, name){
  if(!meta || !name) return null;

  let entry = null;

  if (meta[name]) {
    entry = meta[name];
  } else {
    const nk = normKey(name);
    for (const k of Object.keys(meta)){
      if (normKey(k) === nk) {
        entry = meta[k];
        break;
      }
    }
  }

  let hops = 0;
  while (entry && entry.alias_to && hops < 5) {
    entry = meta[entry.alias_to] || entry;
    hops++;
  }

  return entry;
}

function getAuthor(metaObj){
  return (
    metaObj?.author ||
    metaObj?.creator_name ||
    metaObj?.creator ||
    metaObj?.submitted_by ||
    "Unknown"
  );
}

function parsePrematch(txt){
  const lines = (txt || "").split(/\r?\n/).map(l => l.trimEnd());

  const out = {
    pre: "—",
    p1Name: "—", p2Name: "—",
    p1Meta: "—", p2Meta: "—",
    p1Odds: "ODDS —", p2Odds: "ODDS —",
    h2h: "H2H: —",
    form: "LAST 5: —",
    main: "MAIN EVENT: —",
    debut: null,
    eventNotice: null,
    pillNotice: null,
    bannerText: null
  };

  const pre = lines.find(l => l.startsWith("PRE-MATCH:"));
  if (pre) out.pre = pre.replace("PRE-MATCH:", "").trim();

  const debutLine = lines.find(l => l.includes("DEBUT MATCH"));
  out.debut = debutLine ? debutLine.trim() : null;

  const royalLine = lines.find(l => l.includes("ROYAL TOURNAMENT"));
  const tagSeriesLine = lines.find(l => l.includes("TAG SERIES"));
  const worldTitleLine = lines.find(l => l.includes("CHAMPIONSHIP FIGHT"));
  const tagTitleLine = lines.find(l => l.includes("TAG TEAM CHAMPIONSHIP"));

  if (royalLine) {
    out.eventNotice = royalLine.trim();
  } else if (tagSeriesLine) {
    out.eventNotice = tagSeriesLine.trim();
  }

  if (tagTitleLine) {
    out.pillNotice = tagTitleLine.trim();
    out.bannerText = "🏆 TAG TEAM CHAMPIONSHIP 🏆";
  } else if (worldTitleLine) {
    out.pillNotice = worldTitleLine.trim();
    out.bannerText = "🏆 CHAMPIONSHIP FIGHT 🏆";
  } else if (debutLine) {
    out.pillNotice = debutLine.trim();
    out.bannerText = "🔥 DEBUT MATCH 🔥";
  } else if (royalLine) {
    out.pillNotice = royalLine.trim();
  } else if (tagSeriesLine) {
    out.pillNotice = tagSeriesLine.trim();
  } else {
    out.pillNotice = out.pre;
  }

  let rec1 = null, rec2 = null;
  for (let i = 0; i < lines.length; i++){
    if (lines[i].startsWith("RECORDS:")){
      rec1 = lines[i].replace("RECORDS:", "").trim();
      rec2 = (i + 1 < lines.length) ? lines[i + 1].trim() : "";
      break;
    }
  }

  function splitNameMeta(s){
    const idx = s.indexOf(":");
    if (idx === -1) return { name: "—", meta: (s.trim() || "—"), odds: "ODDS —" };
    const name = s.slice(0, idx).trim();
    const meta = s.slice(idx + 1).trim();
    const m = meta.match(/\[([^\]]+)\]/);
    const odds = m ? `ODDS ${m[1]}` : "ODDS —";
    return { name, meta, odds };
  }

  if (rec1){
    const a = splitNameMeta(rec1);
    out.p1Name = a.name || "—";
    out.p1Meta = a.meta || "—";
    out.p1Odds = a.odds || "ODDS —";
  }
  if (rec2){
    const b = splitNameMeta(rec2);
    out.p2Name = b.name || "—";
    out.p2Meta = b.meta || "—";
    out.p2Odds = b.odds || "ODDS —";
  }

  const h2h = lines.find(l => l.startsWith("H2H:"));
  if (h2h) out.h2h = h2h.trim();

  const form = lines.find(l => l.startsWith("FORM"));
  if (form) out.form = form.replace("FORM L5:", "LAST 5:").trim();

  const me = lines.find(l => l.startsWith("MAIN EVT:") || l.startsWith("MAIN EVENT:"));
  if (me) out.main = me.replace("MAIN EVT:", "MAIN EVENT:").trim();

  return out;
}

let lastMatchKey = "";
let hideTimer = null;

function setPrematchBig(on){
  document.getElementById("totCard")?.classList.toggle("prematchBig", on);
  document.getElementById("leaderPanel")?.classList.toggle("prematchBig", on);
}

function setPanelsVisible(on){
  document.getElementById("totCard")?.classList.toggle("hiddenPanel", !on);
  document.getElementById("leaderPanel")?.classList.toggle("hiddenPanel", !on);
  setPrematchBig(on);
}

function scheduleAutoHide(ms=20000){
  if(hideTimer) clearTimeout(hideTimer);
  hideTimer = setTimeout(()=>setPanelsVisible(false), ms);
}

async function update(){
  try{
    const [state, records, matchRawTxt, isTitleTxt, metaWrap] = await Promise.all([
      fetchJSON("league_state.json"),
      fetchJSON("records.json"),
      fetchText("current_match.txt"),
      fetchText("is_title_match.txt"),
      fetchJSON("fighters_metadata.json"),
    ]);

    const meta = unwrapMeta(metaWrap);
    const rankMap = buildRankMap(records);

    const matchRaw = (matchRawTxt || "").trim();
    let p1 = "—", p2 = "—";
    if (matchRaw.includes(",")){
      const parts = matchRaw.split(",");
      p1 = (parts[0] || "—").trim();
      p2 = (parts[1] || "—").trim();
    }

    const prematchTxt = await fetchText("prematch.txt");
    const tot = parsePrematch(prematchTxt);

    show("debutBanner", false);
    show("eventBanner", false);

    setText("matchNum", `MATCH #${(state?.match_count ?? 0) + 1}`);

    const isTitle = (isTitleTxt || "").trim() === "1";

    if (tot.bannerText){
      setText("titleBanner", tot.bannerText);
      show("titleBanner", true);
    } else if (isTitle) {
      setText("titleBanner", "🏆 CHAMPIONSHIP FIGHT 🏆");
      show("titleBanner", true);
    } else {
      show("titleBanner", false);
    }

    try{
      const stageRaw = (await fetchText("current_stage.txt")).trim();
      setText("stageName", `STAGE: ${stageRaw || "—"}`);
    }catch{
      setText("stageName", "STAGE: —");
    }

    const champ = state?.champion ?? "—";
    const champRec = getRec(records, champ);
    const champM = metaFor(meta, champ) || {};
    const champAuth = getAuthor(champM);
    setText("champName", `CHAMP: ${champ} (${champRec.w}-${champRec.l}) • by ${champAuth}`);

    const p1Rec = getRec(records, p1);
    const p2Rec = getRec(records, p2);

    const p1Rank = rankMap[p1] ? `#${rankMap[p1]} ` : "";
    const p2Rank = rankMap[p2] ? `#${rankMap[p2]} ` : "";

    const p1M = metaFor(meta, p1) || {};
    const p2M = metaFor(meta, p2) || {};
    const p1Auth = getAuthor(p1M);
    const p2Auth = getAuthor(p2M);

    setText(
      "matchLine",
      `${p1Rank}${p1} (${p1Rec.w}-${p1Rec.l}) • ${p1Auth}  vs  ${p2Rank}${p2} (${p2Rec.w}-${p2Rec.l}) • ${p2Auth}`
    );

    const p1Games = p1Rec.w + p1Rec.l;
    const p2Games = p2Rec.w + p2Rec.l;

    const p1Tier = tierTag(rankMap[p1], p1Games);
    const p2Tier = tierTag(rankMap[p2], p2Games);

    const p1Power = (p1M.power_index ?? "—");
    const p2Power = (p2M.power_index ?? "—");

    const p1Arch = (p1M.archetype ?? "—");
    const p2Arch = (p2M.archetype ?? "—");

    setText("totSub", "—");
    setText("matchNotice", tot.pillNotice || "—");

    setText("p1Name", tot.p1Name);
    setText("p2Name", tot.p2Name);

    setText("p1Meta",
`${tot.p1Meta}
Tier: ${p1Tier} | Power: ${p1Power} | ${p1Arch}
By: ${p1Auth}`);

    setText("p2Meta",
`${tot.p2Meta}
Tier: ${p2Tier} | Power: ${p2Power} | ${p2Arch}
By: ${p2Auth}`);

    const p1OddsEl = document.getElementById("p1Odds");
    const p2OddsEl = document.getElementById("p2Odds");

    function parseOddsValue(s){
      const m = String(s || "").match(/-?\d+/);
      return m ? parseInt(m[0], 10) : null;
    }

    function formatOddsLabel(oddsA, oddsB){
      if (oddsA == null || oddsB == null) return "ODDS —";

      const isFavorite = oddsA < oddsB;
      const role = isFavorite ? "Favorite" : "Underdog";
      const shown = oddsA > 0 ? `+${oddsA}` : `${oddsA}`;
      const color = isFavorite ? "#4dff88" : "#ff4d4d";

      return `${role}: <span style="color:${color}; font-weight:900;">${shown}</span>`;
    }

    const p1OddsNum = parseOddsValue(tot.p1Odds);
    const p2OddsNum = parseOddsValue(tot.p2Odds);

    if (p1OddsEl) {
      p1OddsEl.innerHTML = formatOddsLabel(p1OddsNum, p2OddsNum);
    }
    if (p2OddsEl) {
      p2OddsEl.innerHTML = formatOddsLabel(p2OddsNum, p1OddsNum);
    }

    setText("h2h", tot.h2h);
    setText("form", tot.form);
    setText("mainEvent", tot.main);

    const matchKey = `${matchRaw}|${isTitle ? "1" : "0"}`;
    if (matchKey && matchKey !== lastMatchKey){
      lastMatchKey = matchKey;
      setPanelsVisible(true);
      scheduleAutoHide(20000);
    }

    // Leaderboard + champion lines
    const lb = await fetchText("leaderboard.txt");
    const lines = (lb || "").split("\n");

    const tableLines = [];
    for (const rawLine of lines) {
      const line = rawLine.trim();
      if (line.startsWith("Champion:")) continue;
      if (line.startsWith("Tag Champions:")) continue;
      tableLines.push(rawLine);
    }

    setText("leaderboard", tableLines.join("\n"));

	const singlesChampName = state?.champion ?? "—";
	const singlesDef = Number(
	  state?.reign_defenses ??
      state?.defenses ??
      0
    );

    const tagChampsRaw =
      state?.tag_champions ??
      state?.tag_team ??
      state?.tag_champs ??
    null;

    const tagChampsDisplay = Array.isArray(tagChampsRaw)
      ? tagChampsRaw.join(" & ")
      : (tagChampsRaw || "—");

    const tagDef = Number(
      state?.tag_defenses ??
      state?.tag_team_defenses ??
      0
);

	const champText = `Singles Champion: ${singlesChampName} (Def ${singlesDef})`;
	const tagText = `Tag Team Champions: ${tagChampsDisplay} (Def ${tagDef})`;

	// FORCE write (debug safe)
	const champEl = document.getElementById("championLine");
	const tagEl = document.getElementById("tagChampionLine");

	if (champEl) {
	  champEl.textContent = champText;
      champEl.style.display = "block";
	}

	if (tagEl) {
      tagEl.textContent = tagText;
      tagEl.style.display = "block";
	}

    const last = lines.find(l => l.startsWith("Last result:"));
    setText("lastResult", last ? last.replace("Last result:","").trim() : "—");

  }catch{
    // silent fail for Streamlabs
  }
}

setInterval(update, 1500);
update();