"use client";

import enums from "../../config/fighter_enums.json";
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

export default function CreatePage() {
  const [fighter, setFighter] = useState<Fighter>(() => empty());
  const [bases, setBases] = useState<Base[]>([]);
  const [msg, setMsg] = useState(""); const [saving, setSaving] = useState(false);
  useEffect(() => { fetch("/base_fighters.json", { cache: "no-store" }).then((r) => r.json()).then((d: Base[]) => setBases(d.filter((x) => x.customizable !== false))).catch(() => setMsg("Base fighter fallback list could not be loaded.")); }, []);
  const setPath = (path: string, value: string | number | boolean | null) => setFighter((prev) => { const next = JSON.parse(JSON.stringify(prev)) as Fighter; let cur: any = next; const p = path.split("."); for (let i = 0; i < p.length - 1; i += 1) cur = cur[p[i]]; cur[p[p.length - 1]] = value; return next; });
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
    return { ok: errors.length === 0, errors, used, left, template: fighter.base_fighter?.char_folder || TEMPLATES[fighter.assembly.body_class] || fighter.moveset.template_base };
  }, [fighter]);
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
        </div>
        <div className="builder-preview-card">
          <div className="builder-preview-label">Current Concept</div>
          <div className="builder-preview-name">{fighter.identity.display_name || "Unnamed Prospect"}</div>
          <div className="builder-preview-grid"><div><span>Body</span><strong>{label(fighter.assembly.body_class)}</strong></div><div><span>Special</span><strong>{label(fighter.assembly.special_package)}</strong></div><div><span>Finisher</span><strong>{label(fighter.moveset.finisher)}</strong></div><div><span>Mood</span><strong>{label(fighter.classification.alignment)}</strong></div></div>
          <p className="builder-preview-note">{BLURB[fighter.classification.archetype]}</p>
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
            <div className="builder-card-grid">{(E.classification.archetype as string[]).map((a) => <button key={a} type="button" className={`builder-choice-card ${fighter.classification.archetype === a ? "is-active" : ""}`} onClick={() => setFighter((p) => apply(p, a))}><strong>{label(a)}</strong><span>{BLURB[a]}</span></button>)}</div>
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
              <Field label="Body Class" hint="Sets the runtime family"><Pick value={fighter.assembly.body_class} set={(x) => setPath("assembly.body_class", x)} options={E.assembly.body_class} /></Field>
              <Field label="Locomotion Package"><Pick value={fighter.assembly.locomotion_package} set={(x) => setPath("assembly.locomotion_package", x)} options={E.assembly.locomotion_package} /></Field>
              <Field label="Strike Package"><Pick value={fighter.assembly.strike_package} set={(x) => setPath("assembly.strike_package", x)} options={E.assembly.strike_package} /></Field>
              <Field label="Grapple Package"><Pick value={fighter.assembly.grapple_package} set={(x) => setPath("assembly.grapple_package", x)} options={E.assembly.grapple_package} /></Field>
              <Field label="Special Package"><Pick value={fighter.assembly.special_package} set={(x) => setPath("assembly.special_package", x)} options={E.assembly.special_package} /></Field>
              <Field label="Intro Package"><Pick value={fighter.assembly.intro_package} set={(x) => setPath("assembly.intro_package", x)} options={E.assembly.intro_package} /></Field>
              <Field label="Victory Package"><Pick value={fighter.assembly.victory_package} set={(x) => setPath("assembly.victory_package", x)} options={E.assembly.victory_package} /></Field>
              <Field label="Resolved Template"><input className="builder-input is-readonly" value={label(v.template)} readOnly /></Field>
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
          </Section>
        </div>

        <aside className="builder-sidebar">
          <Section title="Submission Check">
            <div className={`builder-status-panel ${v.ok ? "is-ready" : "is-warning"}`}><strong>{v.ok ? "Ready to submit" : "Needs fixes"}</strong><span>{v.ok ? "This build satisfies the current pipeline rules." : "Tune the issues below before sending it live."}</span></div>
            {v.errors.length ? <ul className="builder-error-list">{v.errors.map((e) => <li key={e}>{e}</li>)}</ul> : <div className="builder-empty-state">No validation issues found.</div>}
          </Section>
          <Section title="Career Snapshot">
            <div className="builder-summary-list"><div><span>Name</span><strong>{fighter.identity.display_name || "Unnamed Prospect"}</strong></div><div><span>Creator</span><strong>{fighter.identity.creator_name || "Unknown Creator"}</strong></div><div><span>Body Class</span><strong>{label(fighter.assembly.body_class)}</strong></div><div><span>Archetype</span><strong>{label(fighter.classification.archetype)}</strong></div><div><span>Special</span><strong>{label(fighter.assembly.special_package)}</strong></div><div><span>Range</span><strong>{label(fighter.ai_profile.preferred_range)}</strong></div><div><span>Finisher</span><strong>{label(fighter.moveset.finisher)}</strong></div></div>
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
