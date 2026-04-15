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

function updateTickerMarquee() {
  const track = document.querySelector(".ticker-track");
  const marquee = document.getElementById("tickerMarquee");
  const text = document.getElementById("tickerText");
  const clone = document.getElementById("tickerTextClone");
  if (!track || !marquee || !text || !clone) {
    return;
  }

  const gap = 160;
  const textWidth = Math.ceil(text.scrollWidth);
  const loopDistance = textWidth + gap;
  const pixelsPerSecond = 110;
  const duration = Math.max(18, loopDistance / pixelsPerSecond);

  clone.textContent = text.textContent || "--";
  marquee.style.setProperty("--ticker-gap", `${gap}px`);
  marquee.style.setProperty("--ticker-start-offset", `${Math.ceil(track.clientWidth)}px`);
  marquee.style.setProperty("--ticker-loop", `${loopDistance}px`);
  marquee.style.setProperty("--ticker-duration", `${duration.toFixed(2)}s`);
  marquee.style.animation = "none";
  void marquee.offsetWidth;
  marquee.style.animation = "";
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

function isPlaceholderAuthor(author) {
  const value = String(author || "").trim().toLowerCase();
  return !value || value === "unknown" || value === "legacy fighter";
}

function resolveAliasMeta(meta, entry, maxHops = 5) {
  let current = entry;
  let hops = 0;

  while (current?.alias_to && hops < maxHops) {
    const next = meta?.[current.alias_to];
    if (!next || next === current) {
      break;
    }
    current = next;
    hops += 1;
  }

  return current;
}

function metaScore(entry) {
  if (!entry || typeof entry !== "object") {
    return -1;
  }

  let score = 0;
  if (!isPlaceholderAuthor(entry.author || entry.creator || entry.creator_name || entry.submitted_by)) {
    score += 10;
  }
  if (entry.char_folder) {
    score += 4;
  }
  if (entry.def_file || entry.def_path) {
    score += 3;
  }
  if (entry.source === "native") {
    score += 2;
  }
  if (entry.source === "submitted") {
    score += 1;
  }
  if (entry.alias_to) {
    score -= 2;
  }
  return score;
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

  const normalizedName = normKey(name);
  const candidates = [];
  const seen = new Set();

  function pushCandidate(entry) {
    if (!entry || typeof entry !== "object") {
      return;
    }
    const resolved = resolveAliasMeta(meta, entry);
    const signature = JSON.stringify([
      resolved.author || "",
      resolved.char_folder || "",
      resolved.def_file || "",
      resolved.def_path || "",
      resolved.alias_to || "",
      resolved.source || "",
    ]);
    if (seen.has(signature)) {
      return;
    }
    seen.add(signature);
    candidates.push(resolved);
  }

  pushCandidate(meta[name]);

  for (const key of Object.keys(meta)) {
    if (normKey(key) === normalizedName) {
      pushCandidate(meta[key]);
    }
  }

  for (const key of Object.keys(meta)) {
    const entry = meta[key];
    if (!entry || typeof entry !== "object") {
      continue;
    }

    const aliasTo = normKey(entry.alias_to || "");
    const folder = normKey(entry.char_folder || "");
    const defStem = normKey(String(entry.def_file || "").replace(/\.def$/i, ""));
    const selectEntry = normKey(String(entry.select_entry || "").split("/", 1)[0]);

    if (
      normalizedName === aliasTo ||
      normalizedName === folder ||
      normalizedName === defStem ||
      normalizedName === selectEntry
    ) {
      pushCandidate(entry);
    }
  }

  if (!candidates.length) {
    return null;
  }

  candidates.sort((a, b) => metaScore(b) - metaScore(a));
  return candidates[0];
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
let lastTickerText = "";
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
    story: null,
    pillNotice: null,
    bannerText: null,
  };

  const pre = lines.find((line) => line.startsWith("PRE-MATCH:"));
  if (pre) {
    result.pre = pre.replace("PRE-MATCH:", "").trim();
  }

  const debutLine = lines.find((line) => line.includes("DEBUT MATCH"));
  const royalLine = lines.find((line) => line.includes("ROYAL TOURNAMENT"));
  const grandPrixLine = lines.find((line) => line.includes("GRAND PRIX"));
  const tagSeriesLine = lines.find((line) => line.includes("TAG SERIES"));
  const worldTitleLine = lines.find((line) => line.includes("CHAMPIONSHIP FIGHT"));
  const tagTitleLine = lines.find((line) => line.includes("TAG TEAM CHAMPIONSHIP"));

  result.debut = debutLine ? debutLine.trim() : null;
  result.eventNotice = royalLine?.trim() || grandPrixLine?.trim() || tagSeriesLine?.trim() || null;

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
    result.pillNotice = result.eventNotice || null;
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
  const story = lines.find((line) => line.startsWith("STORY:"));
  const main = lines.find((line) => line.startsWith("MAIN EVT:") || line.startsWith("MAIN EVENT:"));

  if (h2h) {
    result.h2h = h2h.trim();
  }
  if (form) {
    result.form = form.replace("FORM L5:", "LAST 5:").trim();
  }
  if (story) {
    result.story = story.trim();
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

function formatHudRank(rank) {
  return rank && rank !== "NR" ? `${rank}` : "NR";
}

function formatHudRecord(record) {
  return `${record.w}-${record.l}`;
}

function formatHudStreak(streak) {
  const formatted = formatStreak(streak);
  return formatted === "-" ? "Streak -" : `Streak ${formatted}`;
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

function titleizeToken(value) {
  return String(value || "")
    .trim()
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .replace(/\b\w/g, (match) => match.toUpperCase());
}

function isCustomProfile(profile) {
  return Boolean(profile?.fighter_id);
}

function summarizeStyle(profile, fallbackMeta) {
  const archetype = String(profile?.classification?.archetype || fallbackMeta?.archetype || "").trim();
  const weight = String(profile?.classification?.weight_class || "").trim();
  const stance = String(profile?.classification?.stance || "").trim();
  const chunks = [archetype, weight, stance].filter(Boolean);
  return chunks.length ? chunks.join(" | ") : "Style unavailable";
}

function summarizeAlignment(profile) {
  const alignment = String(profile?.classification?.alignment || "").trim();
  const division = String(profile?.classification?.division || "").trim();
  const chunks = [alignment, division].filter(Boolean);
  return chunks.length ? chunks.join(" | ") : null;
}

function summarizeSignature(profile) {
  const choices = [
    profile?.moveset?.finisher,
    profile?.moveset?.signature_1,
    profile?.moveset?.signature_2,
    profile?.moveset?.signature_3,
    profile?.moveset?.moveset_style,
  ];
  const selected = choices.find((value) => String(value || "").trim());
  return selected ? titleizeToken(selected) : null;
}

function summarizeProfileBadge(profile) {
  if (isCustomProfile(profile)) {
    return "CAF";
  }
  return "ROSTER";
}

function buildIdentityCallout(name, profile, fallbackMeta) {
  const creator = summarizeCreator(profile, fallbackMeta);
  const origin = summarizeOrigin(profile);
  const nickname = summarizeNickname(profile);
  const signature = summarizeSignature(profile);
  const style = summarizeStyle(profile, fallbackMeta);
  const alignment = summarizeAlignment(profile);
  const identityBits = [
    nickname ? `"${nickname}"` : null,
    origin ? `from ${origin}` : null,
    alignment,
  ].filter(Boolean);
  return [
    `${name} ${isCustomProfile(profile) ? "CAF" : "fighter"}`,
    creator && !isPlaceholderAuthor(creator) ? `by ${creator}` : null,
    identityBits.length ? `| ${identityBits.join(" | ")}` : null,
    signature ? `| Signature ${signature}` : null,
    style && style !== "Style unavailable" ? `| ${style}` : null,
  ]
    .filter(Boolean)
    .join(" ");
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
  const signature = summarizeSignature(profile);
  return {
    name: name || "--",
    nickname: nickname ? `"${nickname}"` : "A new CAF enters the league",
    creator: summarizeCreator(profile, fallbackMeta),
    origin: summarizeOrigin(profile) || "Origin undisclosed",
    style: [summarizeStyle(profile, fallbackMeta), signature ? `Sig ${signature}` : null].filter(Boolean).join(" | "),
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
  if (prematch?.story) {
    items.push(prematch.story);
  }
  if (prematch?.main && !prematch.main.endsWith("--")) {
    items.push(prematch.main);
  }

  const p1Origin = summarizeOrigin(p1Profile);
  const p2Origin = summarizeOrigin(p2Profile);
  const p1Signature = summarizeSignature(p1Profile);
  const p2Signature = summarizeSignature(p2Profile);
  const p1Style = summarizeStyle(p1Profile, null);
  const p2Style = summarizeStyle(p2Profile, null);
  if (p1Origin) {
    items.push(`${p1} fighting out of ${p1Origin}`);
  }
  if (p2Origin) {
    items.push(`${p2} fighting out of ${p2Origin}`);
  }

  const p1Creator = summarizeCreator(p1Profile, null);
  const p2Creator = summarizeCreator(p2Profile, null);
  if (p1Profile) {
    items.push(buildIdentityCallout(p1, p1Profile, null));
    if (p1Signature) {
      items.push(`${p1} signature move ${p1Signature}`);
    }
    if (p1Style && p1Style !== "Style unavailable") {
      items.push(`${p1} style ${p1Style}`);
    }
    items.push(`${p1} created by ${p1Creator}`);
  }
  if (p2Profile) {
    items.push(buildIdentityCallout(p2, p2Profile, null));
    if (p2Signature) {
      items.push(`${p2} signature move ${p2Signature}`);
    }
    if (p2Style && p2Style !== "Style unavailable") {
      items.push(`${p2} style ${p2Style}`);
    }
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
  document.body.classList.toggle("overlay-prematch-panels", enabled);
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
    const p1Creator = summarizeCreator(p1Profile, p1Map || p1Meta);
    const p2Creator = summarizeCreator(p2Profile, p2Map || p2Meta);
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
    setText("p1HudRank", formatHudRank(p1Rank));
    setText("p2HudRank", formatHudRank(p2Rank));
    setText("p1HudRecord", formatHudRecord(p1Rec));
    setText("p2HudRecord", formatHudRecord(p2Rec));
    setText("p1HudStreak", formatHudStreak(p1Rec.streak));
    setText("p2HudStreak", formatHudStreak(p2Rec.streak));
    setText(
      "p1Tag",
      `${summarizeProfileBadge(p1Profile)} | ${p1Tier} | ${p1Rank}${p1Nickname ? ` | "${p1Nickname}"` : ""}`
    );
    setText(
      "p2Tag",
      `${summarizeProfileBadge(p2Profile)} | ${p2Tier} | ${p2Rank}${p2Nickname ? ` | "${p2Nickname}"` : ""}`
    );

    setText(
      "p1Meta",
      [
        prematch.p1Meta,
        `Power ${p1Power} | ${p1Style}`,
        `Creator: ${p1Creator}`,
        p1Origin ? `From: ${p1Origin}` : null,
        summarizeSignature(p1Profile) ? `Signature: ${summarizeSignature(p1Profile)}` : null,
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
        summarizeSignature(p2Profile) ? `Signature: ${summarizeSignature(p2Profile)}` : null,
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
    setText("creatorLine", `CREATORS: ${p1Creator || "--"}  ||  ${p2Creator || "--"}`);
    setText("styleLine", `STYLE: ${p1Style}  ||  ${p2Style}`);
    setText(
      "signatureLine",
      `SIGNATURES: ${summarizeSignature(p1Profile) || "--"}  ||  ${summarizeSignature(p2Profile) || "--"}`
    );
    setText("mainEvent", prematch.main);

    let stakes = "STAKES: Standard league match";
    if (prematch.debut) {
      stakes = `STAKES: ${prematch.debut}`;
    } else if (prematch.eventNotice) {
      stakes = `STAKES: ${prematch.eventNotice}`;
    } else if (prematch.story) {
      stakes = `STAKES: ${prematch.story.replace("STORY:", "").trim()}`;
    } else if (prematch.bannerText) {
      stakes = `STAKES: ${prematch.bannerText}`;
    }
    const cafCount = [p1Profile, p2Profile].filter(Boolean).length;
    if (cafCount === 2) {
      stakes += ` | CREATOR SHOWCASE: ${p1Creator} vs ${p2Creator}`;
    } else if (cafCount === 1) {
      const cafName = p1Profile ? p1 : p2;
      const cafCreator = p1Profile ? p1Creator : p2Creator;
      stakes += ` | CAF SPOTLIGHT: ${cafName} by ${cafCreator}`;
    }
    setText("stakesLine", stakes);

    setOverlayMode({
      isTitle: isTitle || Boolean(prematch.bannerText === "CHAMPIONSHIP FIGHT" || prematch.bannerText === "TAG TEAM CHAMPIONSHIP"),
      isDebut: Boolean(prematch.debut),
      hasEvent: Boolean(prematch.eventNotice),
    });

    show("debutBanner", false);
    setText("debutBanner", "");

    const centerPillText =
      prematch.pillNotice ||
      (isTitle ? "CHAMPIONSHIP FIGHT" : "");
    setText("titleBanner", centerPillText || "");
    show("titleBanner", Boolean(centerPillText));

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
    if (ticker !== lastTickerText) {
      lastTickerText = ticker;
      setText("tickerText", ticker);
      updateTickerMarquee();
    }

    await loadHall();
    await loadTagHall();
  } catch (error) {
    console.error("ufc.js update() failed:", error);
  }
}

setInterval(update, 1500);
window.addEventListener("resize", updateTickerMarquee);
update();
