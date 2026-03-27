async function loadText(path) {
  try {
    const response = await fetch("../" + path + "?t=" + Date.now(), { cache: "no-store" });
    return await response.text();
  } catch (e) {
    return "";
  }
}

async function loadJSON(path) {
  try {
    const response = await fetch("../" + path + "?t=" + Date.now(), { cache: "no-store" });
    return await response.json();
  } catch (e) {
    return null;
  }
}

function getWL(records, name) {
  const r = (records && records[name]) ? records[name] : {};
  const w = Number(r.W ?? 0);
  const l = Number(r.L ?? 0);
  return `${w}-${l}`;
}

async function updateOverlay() {
  // Load core files
  const [leaderboard, prematch, matchRaw, isTitleRaw] = await Promise.all([
    loadText("leaderboard.txt"),
    loadText("prematch.txt"),
    loadText("current_match.txt"),
    loadText("is_title_match.txt"),
  ]);

  const [state, records] = await Promise.all([
    loadJSON("league_state.json"),
    loadJSON("records.json"),
  ]);

  // Champion (with W-L)
  const champ = state && state.champion ? state.champion : "—";
  const champWL = records ? getWL(records, champ) : "—";
  document.getElementById("championName").textContent = `${champ} (${champWL})`;

  // Current match names
  let p1 = "—", p2 = "—";
  const matchLine = (matchRaw || "").trim();
  if (matchLine.includes(",")) {
    const parts = matchLine.split(",");
    p1 = (parts[0] || "—").trim();
    p2 = (parts[1] || "—").trim();
  }

  // Match number
  const matchCount = state && typeof state.match_count === "number" ? state.match_count : 0;
  const matchNum = matchCount + 1; // next scheduled match number

  // W-L for current match
  const p1WL = records ? getWL(records, p1) : "—";
  const p2WL = records ? getWL(records, p2) : "—";

  const isTitle = (isTitleRaw || "").trim() === "1";
  const titleTag = isTitle ? "🏆 CHAMPIONSHIP FIGHT! " : "";

  document.getElementById("matchHeader").textContent =
    `${titleTag}Match #${matchNum}: ${p1} (${p1WL}) vs ${p2} (${p2WL})`;

  // Match info (simple + readable)
  document.getElementById("matchInfo").textContent =
    `Champion: ${champ} (${champWL})`;

  // Pre-match block (your “PRE-MATCH / RECORDS / FORM / H2H / ODDS...” text)
  document.getElementById("prematchText").textContent =
    prematch ? prematch.trim() : "(prematch.txt not found yet)";

  // Leaderboard
  document.getElementById("leaderboardText").textContent =
    leaderboard ? leaderboard.trim() : "(leaderboard.txt not found yet)";
}

// Update every 2s
setInterval(updateOverlay, 2000);
updateOverlay();