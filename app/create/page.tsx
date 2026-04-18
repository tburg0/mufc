"use client";

import enums from "../../config/fighter_enums.json";
import moveLoadouts from "../../config/runtime_move_loadouts.json";
import moveVariants from "../../config/runtime_move_variants.json";
import { useEffect, useMemo, useState } from "react";

type Base = { id: string; display_name: string; archetype: string; author: string; customizable?: boolean; char_folder: string; def_file: string; def_path: string };
type Assembly = { body_class: string; locomotion_package: string; strike_package: string; grapple_package: string; special_package: string; intro_package: string; victory_package: string };
type Fighter = {
  schema_version: "1.0.0"; fighter_id: string; submission_id: string | null; status: "draft" | "submitted"; created_at: string | null; updated_at: string | null;
  base_fighter: Base | null; assembly: Assembly;
  identity: { display_name: string; nickname: string; announcer_name: string; hometown: string; country: string; bio_short: string; creator_name: string; creator_id: string };
  classification: { division: "singles" | "tag" | "both"; gender_presentation: "male" | "female" | "neutral"; weight_class: string; archetype: string; stance: string; alignment: "face" | "heel" | "tweener" };
  appearance: { body_type: string; height_class: string; physique: string; skin_tone: string; hair_style: string; hair_color: string; mask_style: string; facial_hair: string; gear_top: string; gear_bottom: string; gloves: boolean; boots: string; accessory: string; primary_color: string; secondary_color: string; accent_color: string; portrait_style: string; aura_fx: string };
  stats: { point_budget_total: number; point_budget_used: number; power: number; speed: number; defense: number; grapple: number; strike: number; air: number; stamina: number; recovery: number };
  ai_profile: { profile_mode: "simple" | "advanced"; base_archetype: string; aggression: number; combo_rate: number; grapple_rate: number; strike_rate: number; air_rate: number; throw_escape_rate: number; guard_rate: number; counter_rate: number; special_usage: number; super_usage: number; risk_tolerance: number; ring_control: number; preferred_range: "close" | "mid" | "far" | "adaptive"; finish_priority: number };
  moveset: { template_base: string; moveset_style: string; signature_1: string; signature_2: string; signature_3: string; finisher: string; super_finisher: string; taunt_style: string; intro_style: string; victory_pose: string };
  league_settings: { eligible_for_singles: boolean; eligible_for_tag: boolean; preferred_tag_role: "starter" | "hot_tag" | "either"; debut_priority: boolean; can_hold_world_title: boolean; can_hold_tag_title: boolean };
};

const E = enums as Record<string, any>;
const LOADOUTS = moveLoadouts as Record<string, any>;
const VARIANTS = moveVariants as Record<string, any>;
const STATS = ["power", "speed", "defense", "grapple", "strike", "air", "stamina", "recovery"] as const;
const AI = ["aggression", "combo_rate", "grapple_rate", "strike_rate", "air_rate", "throw_escape_rate", "guard_rate", "counter_rate", "special_usage", "super_usage", "risk_tolerance", "ring_control", "finish_priority"] as const;
const MOVES = ["spinebuster", "counter_slam", "lariat", "roundhouse_burst", "knee_combo", "backfist", "dropkick", "suplex_throw"] as const;
const FINISHERS = ["sitout_powerbomb", "storm_drop", "flash_high_kick", "super_lariat", "driver_drop", "skybreaker"] as const;
const SUPER_FINISHERS = ["storm_drop", "chaos_driver", "critical_burst", "last_stand_bomb"] as const;
const TEMPLATES: Record<string, string> = { lightweight_striker: "template_strike_01", balanced_midweight: "template_balanced_01", heavy_grappler: "template_grapple_01" };
const OK: Record<string, Record<string, string[]>> = {
  body_class: { lightweight_striker: ["rushdown", "striker", "zoner"], balanced_midweight: ["balanced", "wildcard", "rushdown", "striker"], heavy_grappler: ["grappler", "counter_grappler", "tank"] },
  locomotion_package: { measured_step: ["balanced_midweight", "heavy_grappler"], pressure_walk: ["balanced_midweight", "lightweight_striker"], ring_cutter: ["lightweight_striker"], juggernaut_stride: ["heavy_grappler"] },
  strike_package: { balanced_hands: ["balanced", "wildcard", "striker"], kick_volley: ["rushdown", "striker"], counter_shots: ["counter_grappler", "balanced"], heavy_club: ["tank", "grappler"] },
  grapple_package: { fundamental_grabs: ["balanced", "wildcard", "striker"], chain_wrestling: ["grappler", "counter_grappler", "balanced"], power_throws: ["grappler", "tank"] },
  special_package: { ring_general: ["balanced", "wildcard"], burst_offense: ["rushdown", "striker"], space_control: ["zoner", "striker"], shutdown_counter: ["counter_grappler", "tank"] },
  intro_package: { calm_walkout: ["face", "tweener", "heel"], spotlight_pose: ["face", "tweener"], menace_stare: ["heel", "tweener"] },
  victory_package: { stoic_exit: ["face", "tweener", "heel"], crowd_pop: ["face", "tweener"], cold_dismissal: ["heel", "tweener"] }
};
const BLURB: Record<string, string> = { balanced: "Reliable everywhere.", rushdown: "Fast and volatile.", grappler: "Close-range control.", striker: "Precision damage.", zoner: "Distance management.", counter_grappler: "Trap-and-punish pressure.", tank: "Slow menace with huge impact.", wildcard: "Unpredictable and adaptable." };
const ARCHETYPE_PROFILES: Record<string, { title: string; fantasy: string; gameplan: string; risk: string }> = {
  balanced: { title: "Complete Package", fantasy: "Feels like a polished all-around pro who can survive any bracket draw.", gameplan: "Mixes throws, strikes, and ring control without glaring weaknesses.", risk: "Wins by being dependable, not by overwhelming with one specialty." },
  rushdown: { title: "Crowd-Rush Aggressor", fantasy: "Feels like a fighter who is always one dash away from stealing the whole match.", gameplan: "Stays on top of opponents with fast entries, combo pressure, and volatile pace.", risk: "Can burn out or get blown up if the pressure rhythm breaks." },
  grappler: { title: "Mat Dictator", fantasy: "Feels like a ring bully who turns one grab into a whole nightmare sequence.", gameplan: "Forces close-range interactions, punishes hesitation, and cashes out on command throws.", risk: "Needs to close distance before the big damage identity fully turns on." },
  striker: { title: "Clean Technician", fantasy: "Feels like a dangerous hitter with highlight-reel precision and cleaner confirms.", gameplan: "Controls exchanges with sharp hitboxes, launcher routes, and direct burst damage.", risk: "Usually depends on timing and spacing more than raw durability." },
  zoner: { title: "Space Controller", fantasy: "Feels like the kind of fighter chat complains about because nobody can get in clean.", gameplan: "Owns long lanes, checkmates dashes, and makes opponents walk through layered threats.", risk: "Can look mortal when trapped in close-range scramble fights." },
  counter_grappler: { title: "Trap Wrestler", fantasy: "Feels like a patient punish artist who turns mistakes into humiliating momentum swings.", gameplan: "Baits approaches, punishes over-commitment, then converts into punishing throw or orb pressure.", risk: "Needs opponents to blink first or create ugly situations on purpose." },
  tank: { title: "Boss Fight Bruiser", fantasy: "Feels like a walking disaster who shrugs off clean hits and makes every answer hurt.", gameplan: "Marches forward, absorbs pace, and cashes out with huge body-checks and quake-level finishers.", risk: "Gives up initiative early and can be kited if the build lacks enough answers." },
  wildcard: { title: "Chaos Engine", fantasy: "Feels like a fighter no one fully scouts because the next sequence can be anything.", gameplan: "Blends weird movement, swingy pressure, and dramatic finish routes that break normal expectations.", risk: "Can become inconsistent if the build leans too hard into novelty without enough structure." },
};
const PACKAGE_COPY: Record<string, string> = {
  measured_step: "Patient footwork that keeps spacing calm and readable until the burst moment.",
  pressure_walk: "Forward-leaning movement built to keep opponents uncomfortable.",
  ring_cutter: "Fast pursuit pathing that shrinks the ring and corners people quickly.",
  juggernaut_stride: "Heavy, deliberate movement that sells unstoppable force.",
  balanced_hands: "Reliable strike tuning for all-purpose conversions and checks.",
  kick_volley: "High-tempo kicking sequences that thrive in rush and scramble exchanges.",
  counter_shots: "Punish-first striking with sharper interruption timing.",
  heavy_club: "Dense, bruising swings built to make every clean hit matter.",
  fundamental_grabs: "Straightforward wrestling utility that works in most matchups.",
  chain_wrestling: "Flowing grab routes that reward repeated close-range control.",
  power_throws: "High-impact tosses that make every clinch feel dangerous.",
  ring_general: "Balanced special tools for momentum swings and match control.",
  burst_offense: "Aggressive special usage meant to create sudden avalanches.",
  space_control: "Special package focused on lane denial and distance traps.",
  shutdown_counter: "Reactive special tuning built for stopping offense cold.",
};
const SLOT_COPY: Record<string, string> = {
  signature_1: "Primary signature",
  signature_2: "Secondary signature",
  signature_3: "Third signature",
  finisher: "Main finisher",
  super_finisher: "Super finisher",
};
const D: Record<string, Partial<Fighter>> = {
  balanced: { classification: { weight_class: "middleweight", archetype: "balanced", stance: "orthodox", division: "both", gender_presentation: "neutral", alignment: "tweener" }, assembly: { body_class: "balanced_midweight", locomotion_package: "measured_step", strike_package: "balanced_hands", grapple_package: "fundamental_grabs", special_package: "ring_general", intro_package: "calm_walkout", victory_package: "stoic_exit" }, moveset: { template_base: "template_balanced_01", moveset_style: "balanced_pro", signature_1: "dropkick", signature_2: "backfist", signature_3: "suplex_throw", finisher: "driver_drop", super_finisher: "", taunt_style: "silent_nod", intro_style: "confident_walk", victory_pose: "arms_folded" }, stats: { point_budget_total: 500, point_budget_used: 500, power: 65, speed: 65, defense: 65, grapple: 60, strike: 65, air: 60, stamina: 60, recovery: 60 }, ai_profile: { profile_mode: "simple", base_archetype: "balanced", aggression: 55, combo_rate: 55, grapple_rate: 45, strike_rate: 55, air_rate: 45, throw_escape_rate: 60, guard_rate: 55, counter_rate: 50, special_usage: 50, super_usage: 45, risk_tolerance: 50, ring_control: 55, preferred_range: "mid", finish_priority: 55 } },
  rushdown: { classification: { weight_class: "middleweight", archetype: "rushdown", stance: "switch", division: "singles", gender_presentation: "neutral", alignment: "heel" }, assembly: { body_class: "lightweight_striker", locomotion_package: "ring_cutter", strike_package: "kick_volley", grapple_package: "fundamental_grabs", special_package: "burst_offense", intro_package: "menace_stare", victory_package: "cold_dismissal" }, moveset: { template_base: "template_rush_01", moveset_style: "brawler", signature_1: "roundhouse_burst", signature_2: "knee_combo", signature_3: "dropkick", finisher: "flash_high_kick", super_finisher: "critical_burst", taunt_style: "hands_up", intro_style: "wild_charge", victory_pose: "roar" }, stats: { point_budget_total: 500, point_budget_used: 500, power: 68, speed: 82, defense: 52, grapple: 45, strike: 82, air: 70, stamina: 55, recovery: 46 }, ai_profile: { profile_mode: "simple", base_archetype: "rushdown", aggression: 82, combo_rate: 80, grapple_rate: 25, strike_rate: 82, air_rate: 60, throw_escape_rate: 52, guard_rate: 35, counter_rate: 30, special_usage: 68, super_usage: 55, risk_tolerance: 78, ring_control: 62, preferred_range: "close", finish_priority: 76 } },
  grappler: { classification: { weight_class: "heavyweight", archetype: "grappler", stance: "orthodox", division: "both", gender_presentation: "neutral", alignment: "tweener" }, assembly: { body_class: "heavy_grappler", locomotion_package: "juggernaut_stride", strike_package: "heavy_club", grapple_package: "power_throws", special_package: "shutdown_counter", intro_package: "calm_walkout", victory_package: "stoic_exit" }, moveset: { template_base: "template_grapple_01", moveset_style: "power_grapple", signature_1: "spinebuster", signature_2: "suplex_throw", signature_3: "lariat", finisher: "sitout_powerbomb", super_finisher: "storm_drop", taunt_style: "cold_stare", intro_style: "slow_walk", victory_pose: "arms_folded" }, stats: { point_budget_total: 500, point_budget_used: 500, power: 80, speed: 45, defense: 74, grapple: 88, strike: 52, air: 35, stamina: 72, recovery: 54 }, ai_profile: { profile_mode: "simple", base_archetype: "grappler", aggression: 48, combo_rate: 28, grapple_rate: 84, strike_rate: 34, air_rate: 12, throw_escape_rate: 64, guard_rate: 62, counter_rate: 48, special_usage: 44, super_usage: 36, risk_tolerance: 32, ring_control: 58, preferred_range: "close", finish_priority: 66 } }
};

const label = (v: string) => v.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
const slug = (v: string) => v.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 32);
const empty = (): Fighter => ({ schema_version: "1.0.0", fighter_id: "", submission_id: null, status: "draft", created_at: null, updated_at: null, base_fighter: null, assembly: { body_class: "balanced_midweight", locomotion_package: "measured_step", strike_package: "balanced_hands", grapple_package: "fundamental_grabs", special_package: "ring_general", intro_package: "calm_walkout", victory_package: "stoic_exit" }, identity: { display_name: "", nickname: "", announcer_name: "", hometown: "", country: "USA", bio_short: "", creator_name: "", creator_id: "" }, classification: { division: "both", gender_presentation: "neutral", weight_class: "middleweight", archetype: "balanced", stance: "orthodox", alignment: "tweener" }, appearance: { body_type: "athletic", height_class: "average", physique: "defined", skin_tone: "medium_1", hair_style: "short", hair_color: "black", mask_style: "none", facial_hair: "none", gear_top: "vest", gear_bottom: "tights", gloves: true, boots: "wrestling_boots", accessory: "none", primary_color: "red", secondary_color: "black", accent_color: "white", portrait_style: "intense", aura_fx: "none" }, stats: { point_budget_total: 500, point_budget_used: 500, power: 65, speed: 65, defense: 65, grapple: 60, strike: 65, air: 60, stamina: 60, recovery: 60 }, ai_profile: { profile_mode: "simple", base_archetype: "balanced", aggression: 55, combo_rate: 55, grapple_rate: 45, strike_rate: 55, air_rate: 45, throw_escape_rate: 60, guard_rate: 55, counter_rate: 50, special_usage: 50, super_usage: 45, risk_tolerance: 50, ring_control: 55, preferred_range: "mid", finish_priority: 55 }, moveset: { template_base: "template_balanced_01", moveset_style: "balanced_pro", signature_1: "dropkick", signature_2: "backfist", signature_3: "suplex_throw", finisher: "driver_drop", super_finisher: "", taunt_style: "silent_nod", intro_style: "confident_walk", victory_pose: "arms_folded" }, league_settings: { eligible_for_singles: true, eligible_for_tag: true, preferred_tag_role: "either", debut_priority: true, can_hold_world_title: true, can_hold_tag_title: true } });

function apply(prev: Fighter, archetype: string) { const x = D[archetype] ?? D.balanced; return { ...prev, classification: { ...prev.classification, ...x.classification, archetype }, assembly: { ...prev.assembly, ...x.assembly }, moveset: { ...prev.moveset, ...x.moveset }, stats: { ...prev.stats, ...x.stats }, ai_profile: { ...prev.ai_profile, ...x.ai_profile, base_archetype: archetype } }; }
function Section({ title, children }: { title: string; children: React.ReactNode }) { return <section className="builder-section"><h2 className="builder-section-title">{title}</h2>{children}</section>; }
function Field({ label: t, hint, children }: { label: string; hint?: string; children: React.ReactNode }) { return <label className="builder-field"><span className="builder-label">{t}</span>{hint ? <span className="builder-hint">{hint}</span> : null}{children}</label>; }
function Pick({ value, set, options }: { value: string; set: (v: string) => void; options: readonly string[] }) { return <select className="builder-input" value={value} onChange={(e) => set(e.target.value)}>{options.map((o) => <option key={o} value={o}>{label(o)}</option>)}</select>; }

function compatibleOptions(options: readonly string[], current: string, allowed?: readonly string[]) {
  const filtered = (allowed?.length ? options.filter((option) => allowed.includes(option)) : [...options]) as string[];
  if (current && !filtered.includes(current)) filtered.unshift(current);
  return filtered.length ? filtered : [...options];
}

function firstAllowed(options: readonly string[], allowed?: readonly string[], fallback?: string) {
  const filtered = compatibleOptions(options, "", allowed);
  return filtered[0] || fallback || options[0] || "";
}

function allowedPackages(fighter: Fighter) {
  const archetype = fighter.classification.archetype;
  const alignment = fighter.classification.alignment;
  const bodyClass = fighter.assembly.body_class;
  return {
    bodyClasses: (E.assembly.body_class as string[]).filter((option) => OK.body_class[option]?.includes(archetype)),
    locomotion: (E.assembly.locomotion_package as string[]).filter((option) => OK.locomotion_package[option]?.includes(bodyClass)),
    strike: (E.assembly.strike_package as string[]).filter((option) => OK.strike_package[option]?.includes(archetype)),
    grapple: (E.assembly.grapple_package as string[]).filter((option) => OK.grapple_package[option]?.includes(archetype)),
    special: (E.assembly.special_package as string[]).filter((option) => OK.special_package[option]?.includes(archetype)),
    intro: (E.assembly.intro_package as string[]).filter((option) => OK.intro_package[option]?.includes(alignment)),
    victory: (E.assembly.victory_package as string[]).filter((option) => OK.victory_package[option]?.includes(alignment)),
  };
}

function sanitizeFighter(next: Fighter) {
  const allowedBefore = allowedPackages(next);
  const bodyClass = allowedBefore.bodyClasses.includes(next.assembly.body_class)
    ? next.assembly.body_class
    : firstAllowed(E.assembly.body_class as string[], allowedBefore.bodyClasses, "balanced_midweight");

  next.assembly.body_class = bodyClass;
  next.moveset.template_base = TEMPLATES[bodyClass] || next.moveset.template_base;

  const allowedAfter = allowedPackages(next);
  next.assembly.locomotion_package = allowedAfter.locomotion.includes(next.assembly.locomotion_package)
    ? next.assembly.locomotion_package
    : firstAllowed(E.assembly.locomotion_package as string[], allowedAfter.locomotion, "measured_step");
  next.assembly.strike_package = allowedAfter.strike.includes(next.assembly.strike_package)
    ? next.assembly.strike_package
    : firstAllowed(E.assembly.strike_package as string[], allowedAfter.strike, "balanced_hands");
  next.assembly.grapple_package = allowedAfter.grapple.includes(next.assembly.grapple_package)
    ? next.assembly.grapple_package
    : firstAllowed(E.assembly.grapple_package as string[], allowedAfter.grapple, "fundamental_grabs");
  next.assembly.special_package = allowedAfter.special.includes(next.assembly.special_package)
    ? next.assembly.special_package
    : firstAllowed(E.assembly.special_package as string[], allowedAfter.special, "ring_general");
  next.assembly.intro_package = allowedAfter.intro.includes(next.assembly.intro_package)
    ? next.assembly.intro_package
    : firstAllowed(E.assembly.intro_package as string[], allowedAfter.intro, "calm_walkout");
  next.assembly.victory_package = allowedAfter.victory.includes(next.assembly.victory_package)
    ? next.assembly.victory_package
    : firstAllowed(E.assembly.victory_package as string[], allowedAfter.victory, "stoic_exit");

  if (next.appearance.hair_style === "hooded" && next.appearance.mask_style === "full_mask") {
    next.appearance.mask_style = "none";
  }
  if (next.appearance.body_type === "giant" && next.appearance.gear_top === "armor_light") {
    next.appearance.gear_top = "vest";
  }
  if (next.ai_profile.base_archetype !== next.classification.archetype) {
    next.ai_profile.base_archetype = next.classification.archetype;
  }
  return next;
}

function resolveTemplateId(fighter: Fighter, templateLabel: string) {
  const byBody = TEMPLATES[fighter.assembly.body_class];
  if (fighter.base_fighter?.char_folder) return fighter.base_fighter.char_folder;
  return byBody || fighter.moveset.template_base || templateLabel;
}

function buildMovePreview(fighter: Fighter, templateId: string) {
  const template = LOADOUTS.templates?.[templateId];
  const variantTemplate = VARIANTS.templates?.[templateId] ?? {};
  if (!template) return { families: [] as string[], variants: [] as Array<{ slot: string; move: string; family: string; label: string; summary: string }> };

  const selectors = ["signature_1", "signature_2", "signature_3", "finisher", "super_finisher"] as const;
  const families: string[] = [];
  const variants: Array<{ slot: string; move: string; family: string; label: string; summary: string }> = [];

  for (const slot of selectors) {
    const move = fighter.moveset[slot];
    if (!move) continue;
    const familyList =
      template.signatures?.[move] ||
      template.finishers?.[move] ||
      template.super_finishers?.[move] ||
      [];
    for (const family of familyList) {
      if (!families.includes(family)) families.push(family);
    }

    const variant = variantTemplate[slot]?.[move];
    if (variant?.family) {
      variants.push({
        slot,
        move,
        family: variant.family,
        label: variant.label || label(move),
        summary: variant.summary || "",
      });
    }
  }

  if (!families.length) {
    for (const family of template.defaults || []) families.push(family);
  }

  return { families, variants };
}

function buildIdentityPitch(fighter: Fighter, movePreview: ReturnType<typeof buildMovePreview>) {
  const archetype = ARCHETYPE_PROFILES[fighter.classification.archetype] ?? ARCHETYPE_PROFILES.balanced;
  const leadFamilies = movePreview.families.slice(0, 3).map((family) => label(family));
  const specialVoice = PACKAGE_COPY[fighter.assembly.special_package] ?? "Special package helps define how the fighter wins momentum swings.";
  const strikeVoice = PACKAGE_COPY[fighter.assembly.strike_package] ?? "Strike package shapes their core offense.";
  const grappleVoice = PACKAGE_COPY[fighter.assembly.grapple_package] ?? "Grapple package shapes their clinch identity.";
  const familiesText = leadFamilies.length ? `${leadFamilies.join(", ")} are the headline move families.` : "Template defaults still define the move family backbone.";
  return {
    title: archetype.title,
    fantasy: archetype.fantasy,
    gameplan: archetype.gameplan,
    risk: archetype.risk,
    packageStory: `${strikeVoice} ${grappleVoice} ${specialVoice}`,
    movesStory: familiesText,
  };
}

export default function CreatePage() {
  const [fighter, setFighter] = useState<Fighter>(() => empty());
  const [bases, setBases] = useState<Base[]>([]);
  const [msg, setMsg] = useState(""); const [saving, setSaving] = useState(false);
  useEffect(() => { fetch("/base_fighters.json", { cache: "no-store" }).then((r) => r.json()).then((d: Base[]) => setBases(d.filter((x) => x.customizable !== false))).catch(() => setMsg("Base fighter fallback list could not be loaded.")); }, []);
  const setPath = (path: string, value: string | number | boolean | null) => setFighter((prev) => { const next = JSON.parse(JSON.stringify(prev)) as Fighter; let cur: any = next; const p = path.split("."); for (let i = 0; i < p.length - 1; i += 1) cur = cur[p[i]]; cur[p[p.length - 1]] = value; return sanitizeFighter(next); });
  const allowed = useMemo(() => allowedPackages(fighter), [fighter]);
  const v = useMemo(() => {
    const used = STATS.reduce((s, k) => s + fighter.stats[k], 0), left = fighter.stats.point_budget_total - used, errors: string[] = [];
    if (!fighter.identity.display_name.trim()) errors.push("Display name is required.");
    if (!fighter.identity.creator_name.trim()) errors.push("Creator name is required.");
    if (!fighter.fighter_id || !/^[a-z0-9_]{3,32}$/.test(fighter.fighter_id)) errors.push("Fighter ID must be 3-32 lowercase chars.");
    if (left !== 0) errors.push(`Stat budget must equal ${fighter.stats.point_budget_total}.`);
    if (fighter.ai_profile.base_archetype !== fighter.classification.archetype) errors.push("AI archetype must match fighter archetype.");
    if (fighter.appearance.hair_style === "hooded" && fighter.appearance.mask_style === "full_mask") errors.push("Hooded hair cannot be combined with full mask.");
    if (fighter.appearance.body_type === "giant" && fighter.appearance.gear_top === "armor_light") errors.push("Giant body type cannot use armor_light.");
    if (!OK.body_class[fighter.assembly.body_class]?.includes(fighter.classification.archetype)) errors.push("Body class is incompatible with the archetype.");
    if (!OK.locomotion_package[fighter.assembly.locomotion_package]?.includes(fighter.assembly.body_class)) errors.push("Locomotion package is incompatible with the body class.");
    if (!OK.strike_package[fighter.assembly.strike_package]?.includes(fighter.classification.archetype)) errors.push("Strike package is incompatible with the archetype.");
    if (!OK.grapple_package[fighter.assembly.grapple_package]?.includes(fighter.classification.archetype)) errors.push("Grapple package is incompatible with the archetype.");
    if (!OK.special_package[fighter.assembly.special_package]?.includes(fighter.classification.archetype)) errors.push("Special package is incompatible with the archetype.");
    if (!OK.intro_package[fighter.assembly.intro_package]?.includes(fighter.classification.alignment)) errors.push("Intro package does not match the alignment.");
    if (!OK.victory_package[fighter.assembly.victory_package]?.includes(fighter.classification.alignment)) errors.push("Victory package does not match the alignment.");
    const guidance: string[] = [];
    if (allowed.bodyClasses.length) guidance.push(`Body classes are now filtered to ${label(fighter.classification.archetype)}-compatible options.`);
    if (allowed.intro.length || allowed.victory.length) guidance.push(`Entrance and victory packages follow the ${label(fighter.classification.alignment)} alignment automatically.`);
    return { ok: errors.length === 0, errors, guidance, used, left, template: fighter.base_fighter?.char_folder || TEMPLATES[fighter.assembly.body_class] || fighter.moveset.template_base };
  }, [fighter, allowed]);
  const movePreview = useMemo(() => buildMovePreview(fighter, resolveTemplateId(fighter, v.template)), [fighter, v.template]);
  const identityPitch = useMemo(() => buildIdentityPitch(fighter, movePreview), [fighter, movePreview]);
  async function save(status: "draft" | "submitted") {
    setSaving(true); setMsg("");
    const payload = { ...fighter, status, stats: { ...fighter.stats, point_budget_used: v.used }, created_at: fighter.created_at ?? new Date().toISOString(), updated_at: new Date().toISOString() };
    try { const r = await fetch("/api/fighters", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); const d = await r.json(); if (!r.ok) { const detailText = Array.isArray(d.details) ? ` ${d.details.join(" ")}` : ""; throw new Error((d.error || "Unable to save fighter.") + detailText); } setMsg(status === "submitted" ? "Fighter submitted to the live pipeline." : "Draft saved."); setFighter((p) => ({ ...p, status, created_at: payload.created_at, updated_at: payload.updated_at })); } catch (e) { setMsg(e instanceof Error ? e.message : "Unable to save fighter."); } finally { setSaving(false); }
  }

  return (
    <main className="builder-shell">
      <div className="builder-hero">
        <div className="builder-hero-copy">
          <div className="builder-kicker">MUFC Create-A-Fighter</div>
          <h1 className="builder-title">Build a competitor viewers want to follow.</h1>
          <p className="builder-lede">Create the identity, visual flavor, combat modules, and league profile of a fighter built for the 24/7 stream.</p>
          <div className="builder-chip-row"><span className="builder-chip">Archetype: {label(fighter.classification.archetype)}</span><span className="builder-chip">Template: {label(v.template)}</span><span className="builder-chip">Style: {label(fighter.moveset.moveset_style)}</span></div>
          <div className="builder-summary-list">
            <div><span>Fantasy</span><strong>{identityPitch.title}</strong></div>
            <div><span>Gameplan</span><strong>{identityPitch.gameplan}</strong></div>
            <div><span>Tradeoff</span><strong>{identityPitch.risk}</strong></div>
          </div>
        </div>
        <div className="builder-preview-card">
          <div className="builder-preview-label">Current Concept</div>
          <div className="builder-preview-name">{fighter.identity.display_name || "Unnamed Prospect"}</div>
          <div className="builder-preview-grid"><div><span>Body</span><strong>{label(fighter.assembly.body_class)}</strong></div><div><span>Special</span><strong>{label(fighter.assembly.special_package)}</strong></div><div><span>Finisher</span><strong>{label(fighter.moveset.finisher)}</strong></div><div><span>Mood</span><strong>{label(fighter.classification.alignment)}</strong></div></div>
          <div className="builder-chip-row">{movePreview.families.map((family) => <span key={family} className="builder-chip">Kit: {label(family)}</span>)}</div>
          <p className="builder-preview-note">{BLURB[fighter.classification.archetype]}</p>
          <p className="builder-preview-note">{identityPitch.fantasy}</p>
        </div>
      </div>

      <div className="builder-layout">
        <div className="builder-main">
          <Section title="Identity">
            <div className="builder-grid">
              <Field label="Display Name"><input className="builder-input" value={fighter.identity.display_name} onChange={(e) => setFighter((p) => ({ ...p, fighter_id: slug(e.target.value || p.fighter_id), identity: { ...p.identity, display_name: e.target.value } }))} /></Field>
              <Field label="Fighter ID" hint="Used by the roster pipeline"><input className="builder-input" value={fighter.fighter_id} onChange={(e) => setPath("fighter_id", slug(e.target.value))} /></Field>
              <Field label="Nickname"><input className="builder-input" value={fighter.identity.nickname} onChange={(e) => setPath("identity.nickname", e.target.value)} /></Field>
              <Field label="Announcer Name"><input className="builder-input" value={fighter.identity.announcer_name} onChange={(e) => setPath("identity.announcer_name", e.target.value)} /></Field>
              <Field label="Creator Name"><input className="builder-input" value={fighter.identity.creator_name} onChange={(e) => setPath("identity.creator_name", e.target.value)} /></Field>
              <Field label="Creator ID"><input className="builder-input" value={fighter.identity.creator_id} onChange={(e) => setPath("identity.creator_id", e.target.value)} /></Field>
              <Field label="Hometown"><input className="builder-input" value={fighter.identity.hometown} onChange={(e) => setPath("identity.hometown", e.target.value)} /></Field>
              <Field label="Country"><input className="builder-input" value={fighter.identity.country} onChange={(e) => setPath("identity.country", e.target.value)} /></Field>
            </div>
            <Field label="Short Bio"><textarea className="builder-textarea" value={fighter.identity.bio_short} onChange={(e) => setPath("identity.bio_short", e.target.value)} /></Field>
          </Section>

          <Section title="Fight Direction">
            <div className="builder-card-grid">{(E.classification.archetype as string[]).map((a) => <button key={a} type="button" className={`builder-choice-card ${fighter.classification.archetype === a ? "is-active" : ""}`} onClick={() => setFighter((p) => sanitizeFighter(apply(p, a)))}><strong>{label(a)}</strong><span>{BLURB[a]}</span></button>)}</div>
            <div className="builder-summary-list">
              <div><span>Archetype Fantasy</span><strong>{identityPitch.fantasy}</strong></div>
              <div><span>On-Stream Feel</span><strong>{identityPitch.gameplan}</strong></div>
              <div><span>Built-In Risk</span><strong>{identityPitch.risk}</strong></div>
            </div>
            <div className="builder-grid">
              <Field label="Division"><Pick value={fighter.classification.division} set={(x) => setPath("classification.division", x)} options={E.classification.division} /></Field>
              <Field label="Weight Class"><Pick value={fighter.classification.weight_class} set={(x) => setPath("classification.weight_class", x)} options={E.classification.weight_class} /></Field>
              <Field label="Stance"><Pick value={fighter.classification.stance} set={(x) => setPath("classification.stance", x)} options={E.classification.stance} /></Field>
              <Field label="Alignment"><Pick value={fighter.classification.alignment} set={(x) => setPath("classification.alignment", x)} options={E.classification.alignment} /></Field>
              <Field label="Gender Presentation"><Pick value={fighter.classification.gender_presentation} set={(x) => setPath("classification.gender_presentation", x)} options={E.classification.gender_presentation} /></Field>
              <Field label="Preferred Range"><Pick value={fighter.ai_profile.preferred_range} set={(x) => setPath("ai_profile.preferred_range", x)} options={E.ai_profile.preferred_range} /></Field>
            </div>
          </Section>

          <Section title="Assembly">
            <div className="builder-grid">
              <Field label="Body Class" hint="Only compatible body classes are shown for this archetype."><Pick value={fighter.assembly.body_class} set={(x) => setPath("assembly.body_class", x)} options={compatibleOptions(E.assembly.body_class as string[], fighter.assembly.body_class, allowed.bodyClasses)} /></Field>
              <Field label="Locomotion Package" hint="Filtered by body class."><Pick value={fighter.assembly.locomotion_package} set={(x) => setPath("assembly.locomotion_package", x)} options={compatibleOptions(E.assembly.locomotion_package as string[], fighter.assembly.locomotion_package, allowed.locomotion)} /></Field>
              <Field label="Strike Package" hint="Filtered by archetype."><Pick value={fighter.assembly.strike_package} set={(x) => setPath("assembly.strike_package", x)} options={compatibleOptions(E.assembly.strike_package as string[], fighter.assembly.strike_package, allowed.strike)} /></Field>
              <Field label="Grapple Package" hint="Filtered by archetype."><Pick value={fighter.assembly.grapple_package} set={(x) => setPath("assembly.grapple_package", x)} options={compatibleOptions(E.assembly.grapple_package as string[], fighter.assembly.grapple_package, allowed.grapple)} /></Field>
              <Field label="Special Package" hint="Filtered by archetype."><Pick value={fighter.assembly.special_package} set={(x) => setPath("assembly.special_package", x)} options={compatibleOptions(E.assembly.special_package as string[], fighter.assembly.special_package, allowed.special)} /></Field>
              <Field label="Intro Package" hint="Filtered by alignment."><Pick value={fighter.assembly.intro_package} set={(x) => setPath("assembly.intro_package", x)} options={compatibleOptions(E.assembly.intro_package as string[], fighter.assembly.intro_package, allowed.intro)} /></Field>
              <Field label="Victory Package" hint="Filtered by alignment."><Pick value={fighter.assembly.victory_package} set={(x) => setPath("assembly.victory_package", x)} options={compatibleOptions(E.assembly.victory_package as string[], fighter.assembly.victory_package, allowed.victory)} /></Field>
              <Field label="Resolved Template"><input className="builder-input is-readonly" value={label(v.template)} readOnly /></Field>
            </div>
            <div className="builder-summary-list">
              <div><span>Strike Package</span><strong>{PACKAGE_COPY[fighter.assembly.strike_package] ?? label(fighter.assembly.strike_package)}</strong></div>
              <div><span>Grapple Package</span><strong>{PACKAGE_COPY[fighter.assembly.grapple_package] ?? label(fighter.assembly.grapple_package)}</strong></div>
              <div><span>Special Package</span><strong>{PACKAGE_COPY[fighter.assembly.special_package] ?? label(fighter.assembly.special_package)}</strong></div>
            </div>
            <details className="builder-details"><summary>Legacy template fallback</summary><p className="builder-details-copy">Use this only when you deliberately want a roster folder as the source. The modular assembly above is now the main path.</p><Field label="Legacy Base Fighter"><select className="builder-input" value={fighter.base_fighter?.id || ""} onChange={(e) => setFighter((p) => ({ ...p, base_fighter: bases.find((x) => x.id === e.target.value) ?? null }))}><option value="">No legacy base fighter</option>{bases.map((b) => <option key={b.id} value={b.id}>{b.display_name} - {b.author}</option>)}</select></Field></details>
          </Section>

          <Section title="Appearance">
            <div className="builder-grid">
              {(["body_type","height_class","physique","skin_tone","hair_style","hair_color","mask_style","facial_hair","gear_top","gear_bottom","boots","accessory","portrait_style","aura_fx"] as const).map((k) => <Field key={k} label={label(k)}><Pick value={fighter.appearance[k]} set={(x) => setPath(`appearance.${k}`, x)} options={k === "portrait_style" ? E.appearance.portrait_style : k === "aura_fx" ? E.appearance.aura_fx : E.appearance[k]} /></Field>)}
              <Field label="Primary Color"><Pick value={fighter.appearance.primary_color} set={(x) => setPath("appearance.primary_color", x)} options={E.colors.primary_color} /></Field>
              <Field label="Secondary Color"><Pick value={fighter.appearance.secondary_color} set={(x) => setPath("appearance.secondary_color", x)} options={E.colors.secondary_color} /></Field>
              <Field label="Accent Color"><Pick value={fighter.appearance.accent_color} set={(x) => setPath("appearance.accent_color", x)} options={E.colors.accent_color} /></Field>
              <Field label="Gloves"><select className="builder-input" value={fighter.appearance.gloves ? "true" : "false"} onChange={(e) => setPath("appearance.gloves", e.target.value === "true")}><option value="true">True</option><option value="false">False</option></select></Field>
            </div>
          </Section>

          <Section title="Attributes">
            <div className="builder-meter-row"><div className="builder-meter-card"><span>Total Budget</span><strong>{fighter.stats.point_budget_total}</strong></div><div className="builder-meter-card"><span>Used</span><strong>{v.used}</strong></div><div className={`builder-meter-card ${v.left === 0 ? "is-ready" : "is-warning"}`}><span>Remaining</span><strong>{v.left}</strong></div></div>
            <div className="builder-slider-grid">{STATS.map((k) => <div key={k} className="builder-slider-card"><div className="builder-slider-head"><strong>{label(k)}</strong><span>{fighter.stats[k]}</span></div><input className="builder-range" type="range" min={35} max={95} value={fighter.stats[k]} onChange={(e) => setPath(`stats.${k}`, Number(e.target.value))} /></div>)}</div>
          </Section>

          <Section title="AI Profile">
            <div className="builder-grid"><Field label="Profile Mode"><Pick value={fighter.ai_profile.profile_mode} set={(x) => setPath("ai_profile.profile_mode", x)} options={E.ai_profile.profile_mode} /></Field><Field label="AI Archetype"><input className="builder-input is-readonly" value={label(fighter.ai_profile.base_archetype)} readOnly /></Field></div>
            <div className="builder-slider-grid">{AI.map((k) => <div key={k} className="builder-slider-card"><div className="builder-slider-head"><strong>{label(k)}</strong><span>{fighter.ai_profile[k]}</span></div><input className="builder-range" type="range" min={0} max={100} value={fighter.ai_profile[k]} disabled={fighter.ai_profile.profile_mode === "simple"} onChange={(e) => setPath(`ai_profile.${k}`, Number(e.target.value))} /></div>)}</div>
          </Section>

          <Section title="Moveset">
            <div className="builder-grid">
              <Field label="Template Base"><Pick value={fighter.moveset.template_base} set={(x) => setPath("moveset.template_base", x)} options={E.moveset.template_base} /></Field>
              <Field label="Moveset Style"><Pick value={fighter.moveset.moveset_style} set={(x) => setPath("moveset.moveset_style", x)} options={E.moveset.moveset_style} /></Field>
              <Field label="Signature 1"><Pick value={fighter.moveset.signature_1} set={(x) => setPath("moveset.signature_1", x)} options={MOVES} /></Field>
              <Field label="Signature 2"><Pick value={fighter.moveset.signature_2} set={(x) => setPath("moveset.signature_2", x)} options={MOVES} /></Field>
              <Field label="Signature 3"><Pick value={fighter.moveset.signature_3} set={(x) => setPath("moveset.signature_3", x)} options={MOVES} /></Field>
              <Field label="Finisher"><Pick value={fighter.moveset.finisher} set={(x) => setPath("moveset.finisher", x)} options={FINISHERS} /></Field>
              <Field label="Super Finisher"><Pick value={fighter.moveset.super_finisher} set={(x) => setPath("moveset.super_finisher", x)} options={["", ...SUPER_FINISHERS]} /></Field>
              <Field label="Taunt Style"><Pick value={fighter.moveset.taunt_style} set={(x) => setPath("moveset.taunt_style", x)} options={E.moveset.taunt_style} /></Field>
              <Field label="Intro Style"><Pick value={fighter.moveset.intro_style} set={(x) => setPath("moveset.intro_style", x)} options={E.moveset.intro_style} /></Field>
              <Field label="Victory Pose"><Pick value={fighter.moveset.victory_pose} set={(x) => setPath("moveset.victory_pose", x)} options={E.moveset.victory_pose} /></Field>
            </div>
            <div className="builder-summary-list">
              <div><span>Resolved Template</span><strong>{label(resolveTemplateId(fighter, v.template))}</strong></div>
              <div><span>Active Families</span><strong>{movePreview.families.length ? movePreview.families.map((family) => label(family)).join(", ") : "Template defaults"}</strong></div>
              <div><span>Playstyle Read</span><strong>{identityPitch.movesStory}</strong></div>
            </div>
            {movePreview.variants.length ? <div className="builder-card-grid">{movePreview.variants.map((variant) => <div key={`${variant.slot}-${variant.move}`} className="builder-choice-card is-active"><strong>{variant.label}</strong><span>{SLOT_COPY[variant.slot] ?? label(variant.slot)} | {label(variant.family)}</span><span>{variant.summary}</span></div>)}</div> : <div className="builder-empty-state">This build is using the template's default move behavior variants.</div>}
          </Section>
        </div>

        <aside className="builder-sidebar">
          <Section title="Submission Check">
            <div className={`builder-status-panel ${v.ok ? "is-ready" : "is-warning"}`}><strong>{v.ok ? "Ready to submit" : "Needs fixes"}</strong><span>{v.ok ? "This build satisfies the current pipeline rules." : "Tune the issues below before sending it live."}</span></div>
            {v.guidance.length ? <div className="builder-help-list">{v.guidance.map((item) => <div key={item}>{item}</div>)}</div> : null}
            {v.errors.length ? <ul className="builder-error-list">{v.errors.map((e) => <li key={e}>{e}</li>)}</ul> : <div className="builder-empty-state">No validation issues found.</div>}
          </Section>
          <Section title="Career Snapshot">
            <div className="builder-summary-list"><div><span>Name</span><strong>{fighter.identity.display_name || "Unnamed Prospect"}</strong></div><div><span>Creator</span><strong>{fighter.identity.creator_name || "Unknown Creator"}</strong></div><div><span>Body Class</span><strong>{label(fighter.assembly.body_class)}</strong></div><div><span>Archetype</span><strong>{label(fighter.classification.archetype)}</strong></div><div><span>Special</span><strong>{label(fighter.assembly.special_package)}</strong></div><div><span>Range</span><strong>{label(fighter.ai_profile.preferred_range)}</strong></div><div><span>Finisher</span><strong>{label(fighter.moveset.finisher)}</strong></div></div>
          </Section>
          <Section title="Broadcast Pitch">
            <div className="builder-summary-list">
              <div><span>Viewer Hook</span><strong>{identityPitch.fantasy}</strong></div>
              <div><span>Fight Story</span><strong>{identityPitch.gameplan}</strong></div>
              <div><span>Package Read</span><strong>{identityPitch.packageStory}</strong></div>
            </div>
          </Section>
          <Section title="Kit Preview">
            <div className="builder-summary-list">
              <div><span>Move Families</span><strong>{movePreview.families.length ? movePreview.families.map((family) => label(family)).join(", ") : "Template defaults"}</strong></div>
              <div><span>Variant Count</span><strong>{movePreview.variants.length}</strong></div>
            </div>
            {movePreview.variants.length ? <div className="builder-error-list">{movePreview.variants.map((variant) => <div key={`preview-${variant.slot}-${variant.move}`}><strong>{SLOT_COPY[variant.slot] ?? label(variant.slot)}:</strong> {variant.label} - {variant.summary}</div>)}</div> : <div className="builder-empty-state">No custom behavior variants selected yet.</div>}
          </Section>
          <Section title="Export">
            <div className="builder-button-row"><button className="builder-button secondary" onClick={() => void save("draft")} disabled={saving}>{saving ? "Saving..." : "Save Draft"}</button><button className="builder-button primary" onClick={() => void save("submitted")} disabled={saving || !v.ok}>{saving ? "Submitting..." : "Submit Fighter"}</button></div>
            {msg ? <div className="builder-message">{msg}</div> : null}
            <details className="builder-details"><summary>Show submission JSON</summary><pre className="builder-json">{JSON.stringify({ ...fighter, stats: { ...fighter.stats, point_budget_used: v.used }, validation: v }, null, 2)}</pre></details>
          </Section>
        </aside>
      </div>
    </main>
  );
}
