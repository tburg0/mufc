async function fetchText(path) {
  const response = await fetch("../" + path + "?t=" + Date.now(), { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to fetch text: ${path} (${response.status})`);
  }
  return response.text();
}

async function fetchJSON(path) {
  const response = await fetch("../" + path + "?t=" + Date.now(), { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to fetch json: ${path} (${response.status})`);
  }
  return response.json();
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value ?? "--";
  }
}

function setHTML(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.innerHTML = value ?? "--";
  }
}

function show(id, enabled) {
  const element = document.getElementById(id);
  if (element) {
    element.classList.toggle("hidden", !enabled);
  }
}

function getRec(records, name) {
  const record = records?.[name] || {};
  return {
    w: Number(record.W ?? 0),
    l: Number(record.L ?? 0),
    elo: Number(record.elo ?? 1500),
    reigns: Number(record.reigns ?? 0),
    defenses: Number(record.defenses ?? 0),
    streak: Number(record.streak ?? 0),
  };
}

function buildRankMap(records) {
  if (!records) {
    return {};
  }

  const sorted = Object.entries(records)
    .map(([name, record]) => ({
      name,
      elo: Number(record.elo ?? 1500),
      games: Number(record.W ?? 0) + Number(record.L ?? 0),
    }))
    .filter((entry) => entry.games > 0 && !entry.name.includes("+"))
    .sort((a, b) => b.elo - a.elo);

  const rankMap = {};
  sorted.forEach((entry, index) => {
    rankMap[entry.name] = index + 1;
  });
  return rankMap;
}

function tierTag(rank, games) {
  if (games < 5) {
    return "Prospect";
  }
  if (rank && rank <= 10) {
    return "Elite";
  }
  if (rank && rank <= 25) {
    return "Contender";
  }
  return "Roster";
}

function normKey(name) {
  return String(name || "")
    .trim()
    .toLowerCase()
    .replace(/[_\s]+/g, "")
    .replace(/[^\w]/g, "");
}

function unwrapMeta(metaWrap) {
  if (!metaWrap) {
    return {};
  }
  if (metaWrap.fighters && typeof metaWrap.fighters === "object") {
    return metaWrap.fighters;
  }
  return metaWrap;
}

function metaFor(meta, name) {
  if (!meta || !name) {
    return null;
  }

  if (meta[name]) {
    return meta[name];
  }

  const normalizedName = normKey(name);
  for (const key of Object.keys(meta)) {
    if (normKey(key) === normalizedName) {
      return meta[key];
    }
  }

  for (const key of Object.keys(meta)) {
    const entry = meta[key];
    if (!entry) {
      continue;
    }

    const folder = normKey(entry.char_folder || "");
    const defStem = normKey(String(entry.def_file || "").replace(/\.def$/i, ""));
    if (normalizedName === folder || normalizedName === defStem) {
      return entry;
    }
  }

  return null;
}

function getAuthor(metaObj) {
  return (
    metaObj?.author ||
    metaObj?.creator_name ||
    metaObj?.creator ||
    metaObj?.submitted_by ||
    "Unknown"
  );
}

const fighterProfileCache = {};
let lastMatchKey = "";
let hideTimer = null;
let revealResetTimer = null;
let debutCardTimer = null;
let debutCardExitTimer = null;

async function loadRuntimeMapping() {
  try {
    return await fetchJSON("generated/runtime_mapping.json");
  } catch {
    return {};
  }
}

async function loadGeneratedProfile(fighterId) {
  if (!fighterId) {
    return null;
  }
  if (Object.prototype.hasOwnProperty.call(fighterProfileCache, fighterId)) {
    return fighterProfileCache[fighterId];
  }

  try {
    const payload = await fetchJSON(`generated/fighters/${fighterId}.json`);
    fighterProfileCache[fighterId] = payload;
    return payload;
  } catch {
    fighterProfileCache[fighterId] = null;
    return null;
  }
}

function profileForName(mapping, name) {
  if (!mapping || !name) {
    return null;
  }
  if (mapping[name]) {
    return mapping[name];
  }

  const normalizedName = normKey(name);
  for (const key of Object.keys(mapping)) {
    if (normKey(key) === normalizedName) {
      return mapping[key];
    }
  }
  return null;
}

function parsePrematch(text) {
  const lines = String(text || "")
    .split(/\r?\n/)
    .map((line) => line.trimEnd());

  const result = {
    pre: "--",
    p1Name: "--",
    p2Name: "--",
    p1Meta: "--",
    p2Meta: "--",
    p1Odds: "ODDS --",
    p2Odds: "ODDS --",
    h2h: "H2H: --",
    form: "LAST 5: --",
    main: "MAIN EVENT: --",
    debut: null,
    eventNotice: null,
    pillNotice: null,
    bannerText: null,
  };

  const pre = lines.find((line) => line.startsWith("PRE-MATCH:"));
  if (pre) {
    result.pre = pre.replace("PRE-MATCH:", "").trim();
  }

  const debutLine = lines.find((line) => line.includes("DEBUT MATCH"));
  const royalLine = lines.find((line) => line.includes("ROYAL TOURNAMENT"));
  const tagSeriesLine = lines.find((line) => line.includes("TAG SERIES"));
  const worldTitleLine = lines.find((line) => line.includes("CHAMPIONSHIP FIGHT"));
  const tagTitleLine = lines.find((line) => line.includes("TAG TEAM CHAMPIONSHIP"));

  result.debut = debutLine ? debutLine.trim() : null;
  result.eventNotice = royalLine?.trim() || tagSeriesLine?.trim() || null;

  if (tagTitleLine) {
    result.pillNotice = tagTitleLine.trim();
    result.bannerText = "TAG TEAM CHAMPIONSHIP";
  } else if (worldTitleLine) {
    result.pillNotice = worldTitleLine.trim();
    result.bannerText = "CHAMPIONSHIP FIGHT";
  } else if (debutLine) {
    result.pillNotice = debutLine.trim();
    result.bannerText = "DEBUT MATCH";
  } else {
    result.pillNotice = result.eventNotice || result.pre;
  }

  let recordLineOne = null;
  let recordLineTwo = null;
  for (let index = 0; index < lines.length; index += 1) {
    if (lines[index].startsWith("RECORDS:")) {
      recordLineOne = lines[index].replace("RECORDS:", "").trim();
      recordLineTwo = index + 1 < lines.length ? lines[index + 1].trim() : "";
      break;
    }
  }

  function splitNameMeta(line) {
    const separator = line.indexOf(":");
    if (separator === -1) {
      return { name: "--", meta: line.trim() || "--", odds: "ODDS --" };
    }
    const name = line.slice(0, separator).trim();
    const meta = line.slice(separator + 1).trim();
    const oddsMatch = meta.match(/\[([^\]]+)\]/);
    return {
      name: name || "--",
      meta: meta || "--",
      odds: oddsMatch ? `ODDS ${oddsMatch[1]}` : "ODDS --",
    };
  }

  if (recordLineOne) {
    const parsed = splitNameMeta(recordLineOne);
    result.p1Name = parsed.name;
    result.p1Meta = parsed.meta;
    result.p1Odds = parsed.odds;
  }
  if (recordLineTwo) {
    const parsed = splitNameMeta(recordLineTwo);
    result.p2Name = parsed.name;
    result.p2Meta = parsed.meta;
    result.p2Odds = parsed.odds;
  }

  const h2h = lines.find((line) => line.startsWith("H2H:"));
  const form = lines.find((line) => line.startsWith("FORM"));
  const main = lines.find((line) => line.startsWith("MAIN EVT:") || line.startsWith("MAIN EVENT:"));

  if (h2h) {
    result.h2h = h2h.trim();
  }
  if (form) {
    result.form = form.replace("FORM L5:", "LAST 5:").trim();
  }
  if (main) {
    result.main = main.replace("MAIN EVT:", "MAIN EVENT:").trim();
  }

  return result;
}

function parseOddsValue(label) {
  const match = String(label || "").match(/-?\d+/);
  return match ? parseInt(match[0], 10) : null;
}

function formatOddsLabel(currentOdds, otherOdds) {
  if (currentOdds == null || otherOdds == null) {
    return "ODDS --";
  }
  const isFavorite = currentOdds < otherOdds;
  const role = isFavorite ? "Favorite" : "Underdog";
  const shown = currentOdds > 0 ? `+${currentOdds}` : `${currentOdds}`;
  const color = isFavorite ? "#74f2a3" : "#ff7d7d";
  return `${role}: <span style="color:${color}; font-weight:900;">${shown}</span>`;
}

function formatStreak(streak) {
  if (streak > 0) {
    return `W${streak}`;
  }
  if (streak < 0) {
    return `L${Math.abs(streak)}`;
  }
  return "-";
}

function summarizeOrigin(profile) {
  const hometown = String(profile?.identity?.hometown || "").trim();
  const country = String(profile?.identity?.country || "").trim();
  if (hometown && country) {
    return `${hometown}, ${country}`;
  }
  return hometown || country || null;
}

function summarizeNickname(profile) {
  const nickname = String(profile?.identity?.nickname || "").trim();
  return nickname || null;
}

function summarizeStyle(profile, fallbackMeta) {
  const archetype = String(profile?.classification?.archetype || fallbackMeta?.archetype || "").trim();
  const weight = String(profile?.classification?.weight_class || "").trim();
  const stance = String(profile?.classification?.stance || "").trim();
  const chunks = [archetype, weight, stance].filter(Boolean);
  return chunks.length ? chunks.join(" | ") : "Style unavailable";
}

function summarizeCreator(profile, fallbackMeta) {
  return (
    String(profile?.identity?.creator_name || "").trim() ||
    String(fallbackMeta?.creator || "").trim() ||
    getAuthor(fallbackMeta)
  );
}

function buildDebutCardDetails(name, profile, fallbackMeta) {
  const nickname = summarizeNickname(profile);
  return {
    name: name || "--",
    nickname: nickname ? `"${nickname}"` : "A new CAF enters the league",
    creator: summarizeCreator(profile, fallbackMeta),
    origin: summarizeOrigin(profile) || "Origin undisclosed",
    style: summarizeStyle(profile, fallbackMeta),
  };
}

function buildTickerItems({
  state,
  matchNumber,
  stageText,
  p1,
  p2,
  p1Profile,
  p2Profile,
  p1Rec,
  p2Rec,
  championText,
  tagChampText,
  prematch,
  lastResult,
}) {
  const items = [];
  items.push(`MATCH ${matchNumber}`);
  items.push(`${p1} vs ${p2}`);
  if (stageText) {
    items.push(stageText);
  }
  if (prematch?.debut) {
    items.push(prematch.debut);
  }
  if (prematch?.eventNotice) {
    items.push(prematch.eventNotice);
  }
  if (prematch?.main && !prematch.main.endsWith("--")) {
    items.push(prematch.main);
  }

  const p1Origin = summarizeOrigin(p1Profile);
  const p2Origin = summarizeOrigin(p2Profile);
  if (p1Origin) {
    items.push(`${p1} fighting out of ${p1Origin}`);
  }
  if (p2Origin) {
    items.push(`${p2} fighting out of ${p2Origin}`);
  }

  const p1Creator = summarizeCreator(p1Profile, null);
  const p2Creator = summarizeCreator(p2Profile, null);
  if (p1Profile) {
    items.push(`${p1} created by ${p1Creator}`);
  }
  if (p2Profile) {
    items.push(`${p2} created by ${p2Creator}`);
  }

  items.push(`${p1} record ${p1Rec.w}-${p1Rec.l} | streak ${formatStreak(p1Rec.streak)} | Elo ${p1Rec.elo.toFixed(1)}`);
  items.push(`${p2} record ${p2Rec.w}-${p2Rec.l} | streak ${formatStreak(p2Rec.streak)} | Elo ${p2Rec.elo.toFixed(1)}`);
  items.push(championText);
  items.push(tagChampText);

  if (lastResult && lastResult !== "--") {
    items.push(`Last result: ${lastResult}`);
  }

  const count = state?.roster_counts || state?.counts;
  if (count) {
    const submitted = count.submitted ?? "--";
    const total = count.total ?? "--";
    items.push(`Live roster: ${total} fighters | Submitted CAF roster: ${submitted}`);
  }

  return items.filter(Boolean).join("   |   ");
}

async function loadHall() {
  try {
    setText("hall", await fetchText("hall_of_champions.txt"));
  } catch {
    setText("hall", "--");
  }
}

async function loadTagHall() {
  try {
    setText("tagHall", await fetchText("tag_hall_of_champions.txt"));
  } catch {
    setText("tagHall", "--");
  }
}

function setPrematchBig(enabled) {
  document.getElementById("totCard")?.classList.toggle("prematchBig", enabled);
  document.getElementById("leaderPanel")?.classList.toggle("prematchBig", enabled);
  document.getElementById("hallPanel")?.classList.toggle("prematchBig", enabled);
  document.getElementById("tagHallPanel")?.classList.toggle("prematchBig", enabled);
}

function setPanelsVisible(enabled) {
  document.getElementById("totCard")?.classList.toggle("hiddenPanel", !enabled);
  document.getElementById("leaderPanel")?.classList.toggle("hiddenPanel", !enabled);
  document.getElementById("hallPanel")?.classList.toggle("hiddenPanel", !enabled);
  document.getElementById("tagHallPanel")?.classList.toggle("hiddenPanel", !enabled);
  setPrematchBig(enabled);
}

function setOverlayMode({ isTitle, isDebut, hasEvent }) {
  const body = document.body;
  body.classList.toggle("overlay-title", Boolean(isTitle));
  body.classList.toggle("overlay-debut", Boolean(isDebut));
  body.classList.toggle("overlay-event", Boolean(hasEvent));
}

function setDebutCardVisible(visible) {
  const card = document.getElementById("debutCard");
  if (!card) {
    return;
  }
  card.classList.toggle("hidden", !visible);
}

function clearDebutCardTimers() {
  if (debutCardTimer) {
    clearTimeout(debutCardTimer);
    debutCardTimer = null;
  }
  if (debutCardExitTimer) {
    clearTimeout(debutCardExitTimer);
    debutCardExitTimer = null;
  }
}

function playDebutCard(details) {
  const card = document.getElementById("debutCard");
  if (!card) {
    return;
  }

  clearDebutCardTimers();
  setText("debutCardName", details.name || "--");
  setText("debutCardNickname", details.nickname || "--");
  setText("debutCardCreator", details.creator || "--");
  setText("debutCardOrigin", details.origin || "--");
  setText("debutCardStyle", details.style || "--");

  card.classList.remove("hidden", "is-exit");
  card.classList.remove("is-live");
  void card.offsetWidth;
  card.classList.add("is-live");

  debutCardTimer = setTimeout(() => {
    card.classList.remove("is-live");
    card.classList.add("is-exit");
    debutCardExitTimer = setTimeout(() => {
      card.classList.add("hidden");
      card.classList.remove("is-exit");
    }, 700);
  }, 4200);
}

function triggerRevealAnimation() {
  const card = document.getElementById("totCard");
  if (!card) {
    return;
  }
  card.classList.remove("match-reveal");
  void card.offsetWidth;
  card.classList.add("match-reveal");
  if (revealResetTimer) {
    clearTimeout(revealResetTimer);
  }
  revealResetTimer = setTimeout(() => {
    card.classList.remove("match-reveal");
  }, 1400);
}

function scheduleAutoHide(ms = 20000) {
  if (hideTimer) {
    clearTimeout(hideTimer);
  }
  hideTimer = setTimeout(() => setPanelsVisible(false), ms);
}

async function update() {
  try {
    const [state, records, matchRawText, isTitleText, metaWrap, runtimeMapping] = await Promise.all([
      fetchJSON("league_state.json"),
      fetchJSON("records.json"),
      fetchText("current_match.txt"),
      fetchText("is_title_match.txt"),
      fetchJSON("fighters_metadata.json"),
      loadRuntimeMapping(),
    ]);

    const meta = unwrapMeta(metaWrap);
    const rankMap = buildRankMap(records);
    const matchRaw = String(matchRawText || "").trim();

    let p1 = "--";
    let p2 = "--";
    if (matchRaw.includes(",")) {
      const [first, second] = matchRaw.split(",");
      p1 = (first || "--").trim();
      p2 = (second || "--").trim();
    }

    const prematchText = await fetchText("prematch.txt");
    const prematch = parsePrematch(prematchText);

    const p1Meta = metaFor(meta, p1) || {};
    const p2Meta = metaFor(meta, p2) || {};
    const p1Map = profileForName(runtimeMapping, p1);
    const p2Map = profileForName(runtimeMapping, p2);
    const [p1Profile, p2Profile] = await Promise.all([
      loadGeneratedProfile(p1Map?.fighter_id),
      loadGeneratedProfile(p2Map?.fighter_id),
    ]);

    const p1Rec = getRec(records, p1);
    const p2Rec = getRec(records, p2);
    const p1Games = p1Rec.w + p1Rec.l;
    const p2Games = p2Rec.w + p2Rec.l;
    const p1Rank = rankMap[p1] ? `#${rankMap[p1]}` : "NR";
    const p2Rank = rankMap[p2] ? `#${rankMap[p2]}` : "NR";
    const p1Tier = tierTag(rankMap[p1], p1Games);
    const p2Tier = tierTag(rankMap[p2], p2Games);
    const p1Power = p1Profile?.league_metadata?.power_index ?? p1Meta?.power_index ?? "--";
    const p2Power = p2Profile?.league_metadata?.power_index ?? p2Meta?.power_index ?? "--";
    const p1Origin = summarizeOrigin(p1Profile);
    const p2Origin = summarizeOrigin(p2Profile);
    const p1Nickname = summarizeNickname(p1Profile);
    const p2Nickname = summarizeNickname(p2Profile);
    const p1Style = summarizeStyle(p1Profile, p1Meta);
    const p2Style = summarizeStyle(p2Profile, p2Meta);
    const p1Creator = summarizeCreator(p1Profile, p1Map);
    const p2Creator = summarizeCreator(p2Profile, p2Map);
    const isTitle = String(isTitleText || "").trim() === "1";

    const matchNumber = `#${(state?.match_count ?? 0) + 1}`;
    let stageLabel = "STAGE: --";
    try {
      const stage = String(await fetchText("current_stage.txt")).trim();
      stageLabel = `STAGE: ${stage || "--"}`;
    } catch {
      stageLabel = "STAGE: --";
    }

    const champion = state?.champion ?? "--";
    const championRec = getRec(records, champion);
    setText("totSub", prematch.pre || "Broadcast comparison");

    setText("p1Name", prematch.p1Name || p1);
    setText("p2Name", prematch.p2Name || p2);
    setText("p1Tag", `${p1Tier} | ${p1Rank}${p1Nickname ? ` | "${p1Nickname}"` : ""}`);
    setText("p2Tag", `${p2Tier} | ${p2Rank}${p2Nickname ? ` | "${p2Nickname}"` : ""}`);

    setText(
      "p1Meta",
      [
        prematch.p1Meta,
        `Power ${p1Power} | ${p1Style}`,
        `Creator: ${p1Creator}`,
        p1Origin ? `From: ${p1Origin}` : null,
        `Titles: ${p1Rec.reigns} reigns | ${p1Rec.defenses} defenses`,
      ].filter(Boolean).join("\n")
    );

    setText(
      "p2Meta",
      [
        prematch.p2Meta,
        `Power ${p2Power} | ${p2Style}`,
        `Creator: ${p2Creator}`,
        p2Origin ? `From: ${p2Origin}` : null,
        `Titles: ${p2Rec.reigns} reigns | ${p2Rec.defenses} defenses`,
      ].filter(Boolean).join("\n")
    );

    const p1Odds = parseOddsValue(prematch.p1Odds);
    const p2Odds = parseOddsValue(prematch.p2Odds);
    setHTML("p1Odds", formatOddsLabel(p1Odds, p2Odds));
    setHTML("p2Odds", formatOddsLabel(p2Odds, p1Odds));

    setText("h2h", prematch.h2h);
    setText("form", prematch.form);
    setText("originLine", `ORIGIN: ${p1Origin || "--"}  ||  ${p2Origin || "--"}`);
    setText("styleLine", `STYLE: ${p1Style}  ||  ${p2Style}`);
    setText("mainEvent", prematch.main);

    let stakes = "STAKES: Standard league match";
    if (prematch.debut) {
      stakes = `STAKES: ${prematch.debut}`;
    } else if (prematch.eventNotice) {
      stakes = `STAKES: ${prematch.eventNotice}`;
    } else if (prematch.bannerText) {
      stakes = `STAKES: ${prematch.bannerText}`;
    }
    setText("stakesLine", stakes);

    setOverlayMode({
      isTitle: isTitle || Boolean(prematch.bannerText === "CHAMPIONSHIP FIGHT" || prematch.bannerText === "TAG TEAM CHAMPIONSHIP"),
      isDebut: Boolean(prematch.debut),
      hasEvent: Boolean(prematch.eventNotice),
    });

    show("debutBanner", Boolean(prematch.debut));
    setText("debutBanner", prematch.debut || "");

    if (prematch.bannerText && prematch.bannerText !== "DEBUT MATCH") {
      setText("titleBanner", prematch.bannerText);
      show("titleBanner", true);
    } else {
      show("titleBanner", isTitle && !prematch.debut);
      if (isTitle) {
        setText("titleBanner", "CHAMPIONSHIP FIGHT");
      }
    }

    const matchKey = `${matchRaw}|${isTitle ? "1" : "0"}`;
    if (matchKey && matchKey !== lastMatchKey) {
      lastMatchKey = matchKey;
      setPanelsVisible(true);
      scheduleAutoHide(20000);
      triggerRevealAnimation();
      if (prematch.debut) {
        const debutName = String(prematch.debut).split(":").pop()?.trim() || p1;
        const debutIsP1 = normKey(debutName) === normKey(p1);
        const debutProfile = debutIsP1 ? p1Profile : p2Profile;
        const debutMeta = debutIsP1 ? (p1Map || p1Meta) : (p2Map || p2Meta);
        playDebutCard(buildDebutCardDetails(debutName, debutProfile, debutMeta));
      } else {
        clearDebutCardTimers();
        setDebutCardVisible(false);
      }
    }

    const leaderboardText = await fetchText("leaderboard.txt");
    const leaderboardLines = String(leaderboardText || "")
      .split("\n")
      .filter((line) => !line.startsWith("Champion:") && !line.startsWith("Tag Champions:"));
    setText("leaderboard", leaderboardLines.join("\n").trim() || "--");

    const singlesChampionText = `Singles Champion: ${champion} (Def ${Number(state?.reign_defenses ?? 0)})`;
    const tagChampionsRaw = state?.tag_champions ?? null;
    const tagChampionsText = Array.isArray(tagChampionsRaw)
      ? tagChampionsRaw.join(" & ")
      : (tagChampionsRaw || "--");
    const tagChampionText = `Tag Team Champions: ${tagChampionsText} (Def ${Number(state?.tag_defenses ?? 0)})`;
    setText("championLine", singlesChampionText);
    setText("tagChampionLine", tagChampionText);

    const lastResultLine = String(leaderboardText || "")
      .split("\n")
      .find((line) => line.startsWith("Last result:"));
    const lastResult = lastResultLine ? lastResultLine.replace("Last result:", "").trim() : "--";
    setText("lastResult", lastResult);

    const ticker = buildTickerItems({
      state,
      matchNumber,
      stageText: stageLabel,
      p1,
      p2,
      p1Profile,
      p2Profile,
      p1Rec,
      p2Rec,
      championText: singlesChampionText,
      tagChampText: tagChampionText,
      prematch,
      lastResult,
    });
    setText("tickerText", ticker);

    await loadHall();
    await loadTagHall();
  } catch (error) {
    console.error("ufc.js update() failed:", error);
  }
}

setInterval(update, 1500);
update();
