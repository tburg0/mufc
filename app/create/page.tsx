"use client";

import { useEffect, useMemo, useState } from "react";

type BaseFighterOption = {
  id: string;
  display_name: string;
  archetype: string;
  author: string;
  customizable?: boolean;
  char_folder: string;
  def_file: string;
  def_path: string;
};

type FighterSubmission = {
  schema_version: "1.0.0";
  fighter_id: string;
  submission_id: string | null;
  status: "draft" | "submitted";
  created_at: string | null;
  updated_at: string | null;
  base_fighter: {
    id: string;
    display_name: string;
    archetype: string;
    author: string;
    char_folder: string;
    def_file: string;
    def_path: string;
  } | null;
  identity: {
    display_name: string;
    nickname: string;
    announcer_name: string;
    hometown: string;
    country: string;
    bio_short: string;
    creator_name: string;
    creator_id: string;
  };
  classification: {
    division: "singles" | "tag" | "both";
    gender_presentation: "male" | "female" | "neutral";
    weight_class: string;
    archetype: string;
    stance: string;
    alignment: "face" | "heel" | "tweener";
  };
  appearance: {
    body_type: string;
    height_class: string;
    physique: string;
    skin_tone: string;
    hair_style: string;
    hair_color: string;
    mask_style: string;
    facial_hair: string;
    gear_top: string;
    gear_bottom: string;
    gloves: boolean;
    boots: string;
    accessory: string;
    primary_color: string;
    secondary_color: string;
    accent_color: string;
    portrait_style: string;
    aura_fx: string;
  };
  stats: {
    point_budget_total: number;
    point_budget_used: number;
    power: number;
    speed: number;
    defense: number;
    grapple: number;
    strike: number;
    air: number;
    stamina: number;
    recovery: number;
  };
  ai_profile: {
    profile_mode: "simple" | "advanced";
    base_archetype: string;
    aggression: number;
    combo_rate: number;
    grapple_rate: number;
    strike_rate: number;
    air_rate: number;
    throw_escape_rate: number;
    guard_rate: number;
    counter_rate: number;
    special_usage: number;
    super_usage: number;
    risk_tolerance: number;
    ring_control: number;
    preferred_range: "close" | "mid" | "far" | "adaptive";
    finish_priority: number;
  };
  moveset: {
    template_base: string;
    moveset_style: string;
    signature_1: string;
    signature_2: string;
    signature_3: string;
    finisher: string;
    super_finisher: string;
    taunt_style: string;
    intro_style: string;
    victory_pose: string;
  };
  league_settings: {
    eligible_for_singles: boolean;
    eligible_for_tag: boolean;
    preferred_tag_role: "starter" | "hot_tag" | "either";
    debut_priority: boolean;
    can_hold_world_title: boolean;
    can_hold_tag_title: boolean;
  };
};

const ENUMS = {
  division: ["singles", "tag", "both"],
  gender_presentation: ["male", "female", "neutral"],
  weight_class: ["flyweight", "lightweight", "middleweight", "heavyweight", "super_heavyweight"],
  archetype: ["balanced", "rushdown", "grappler", "striker", "zoner", "counter_grappler", "tank", "wildcard"],
  stance: ["orthodox", "southpaw", "switch", "brawler"],
  alignment: ["face", "heel", "tweener"],
  body_type: ["slim", "athletic", "heavy", "giant"],
  height_class: ["short", "average", "tall"],
  physique: ["lean", "defined", "thick", "bulky"],
  skin_tone: ["light_1", "light_2", "medium_1", "medium_2", "dark_1", "dark_2"],
  hair_style: ["bald", "short", "short_spiky", "long", "ponytail", "mohawk", "afro", "hooded"],
  hair_color: ["black", "brown", "blonde", "red", "white", "blue", "green", "purple"],
  mask_style: ["none", "lucha", "half_mask", "full_mask"],
  facial_hair: ["none", "stubble", "goatee", "full_beard", "mustache"],
  gear_top: ["bare", "vest", "open_jacket", "hoodie", "armor_light"],
  gear_bottom: ["trunks", "tights", "pants", "shorts"],
  boots: ["light_boots", "heavy_boots", "kickpads", "wrestling_boots"],
  accessory: ["none", "chain", "cape", "armband", "eyepatch"],
  color: ["black", "white", "red", "blue", "green", "yellow", "purple", "orange", "silver", "gold"],
  portrait_style: ["serious", "intense", "smug", "wild", "heroic"],
  aura_fx: ["none", "smoke", "flame", "shadow", "electric"],
  preferred_range: ["close", "mid", "far", "adaptive"],
  profile_mode: ["simple", "advanced"],
  template_base: [
    "template_balanced_01",
    "template_rush_01",
    "template_grapple_01",
    "template_strike_01",
    "template_zone_01",
    "template_counter_01",
    "template_tank_01",
    "template_wild_01"
  ],
  moveset_style: [
    "balanced_pro",
    "power_grapple",
    "chain_wrestler",
    "kickboxer",
    "brawler",
    "technical_striker",
    "anti_air_specialist",
    "chaos_mixup"
  ],
  moves: ["spinebuster", "counter_slam", "lariat", "roundhouse_burst", "knee_combo", "backfist", "dropkick", "suplex_throw"],
  finishers: ["sitout_powerbomb", "storm_drop", "flash_high_kick", "super_lariat", "driver_drop", "skybreaker"],
  super_finishers: ["", "storm_drop", "chaos_driver", "critical_burst", "last_stand_bomb"],
  taunt_style: ["cold_stare", "hands_up", "point_to_camera", "laugh", "silent_nod"],
  intro_style: ["slow_walk", "confident_walk", "shadow_box", "arms_crossed", "wild_charge"],
  victory_pose: ["arms_folded", "point_to_camera", "kneel_pose", "belt_motion", "roar"],
  preferred_tag_role: ["starter", "hot_tag", "either"]
} as const;

const ARCHETYPE_DEFAULTS: Record<string, Partial<FighterSubmission>> = {
  balanced: {
    classification: { weight_class: "middleweight", archetype: "balanced", stance: "orthodox", division: "both", gender_presentation: "neutral", alignment: "tweener" },
    stats: { point_budget_total: 500, point_budget_used: 500, power: 65, speed: 65, defense: 65, grapple: 60, strike: 65, air: 60, stamina: 60, recovery: 60 },
    ai_profile: { profile_mode: "simple", base_archetype: "balanced", aggression: 55, combo_rate: 55, grapple_rate: 45, strike_rate: 55, air_rate: 45, throw_escape_rate: 60, guard_rate: 55, counter_rate: 50, special_usage: 50, super_usage: 45, risk_tolerance: 50, ring_control: 55, preferred_range: "mid", finish_priority: 55 },
    moveset: { template_base: "template_balanced_01", moveset_style: "balanced_pro", signature_1: "dropkick", signature_2: "backfist", signature_3: "suplex_throw", finisher: "driver_drop", super_finisher: "", taunt_style: "silent_nod", intro_style: "confident_walk", victory_pose: "arms_folded" }
  },
  rushdown: {
    classification: { weight_class: "middleweight", archetype: "rushdown", stance: "switch", division: "singles", gender_presentation: "neutral", alignment: "heel" },
    stats: { point_budget_total: 500, point_budget_used: 500, power: 68, speed: 82, defense: 52, grapple: 45, strike: 82, air: 70, stamina: 55, recovery: 46 },
    ai_profile: { profile_mode: "simple", base_archetype: "rushdown", aggression: 82, combo_rate: 80, grapple_rate: 25, strike_rate: 82, air_rate: 60, throw_escape_rate: 52, guard_rate: 35, counter_rate: 30, special_usage: 68, super_usage: 55, risk_tolerance: 78, ring_control: 62, preferred_range: "close", finish_priority: 76 },
    moveset: { template_base: "template_rush_01", moveset_style: "brawler", signature_1: "roundhouse_burst", signature_2: "knee_combo", signature_3: "dropkick", finisher: "flash_high_kick", super_finisher: "critical_burst", taunt_style: "hands_up", intro_style: "wild_charge", victory_pose: "roar" }
  },
  grappler: {
    classification: { weight_class: "heavyweight", archetype: "grappler", stance: "orthodox", division: "both", gender_presentation: "neutral", alignment: "tweener" },
    stats: { point_budget_total: 500, point_budget_used: 500, power: 80, speed: 45, defense: 74, grapple: 88, strike: 52, air: 35, stamina: 72, recovery: 54 },
    ai_profile: { profile_mode: "simple", base_archetype: "grappler", aggression: 48, combo_rate: 28, grapple_rate: 84, strike_rate: 34, air_rate: 12, throw_escape_rate: 64, guard_rate: 62, counter_rate: 48, special_usage: 44, super_usage: 36, risk_tolerance: 32, ring_control: 58, preferred_range: "close", finish_priority: 66 },
    moveset: { template_base: "template_grapple_01", moveset_style: "power_grapple", signature_1: "spinebuster", signature_2: "suplex_throw", signature_3: "lariat", finisher: "sitout_powerbomb", super_finisher: "storm_drop", taunt_style: "cold_stare", intro_style: "slow_walk", victory_pose: "arms_folded" }
  },
  striker: {
    classification: { weight_class: "middleweight", archetype: "striker", stance: "southpaw", division: "singles", gender_presentation: "neutral", alignment: "face" },
    stats: { point_budget_total: 500, point_budget_used: 500, power: 70, speed: 74, defense: 58, grapple: 42, strike: 88, air: 62, stamina: 58, recovery: 48 },
    ai_profile: { profile_mode: "simple", base_archetype: "striker", aggression: 68, combo_rate: 70, grapple_rate: 20, strike_rate: 85, air_rate: 52, throw_escape_rate: 55, guard_rate: 45, counter_rate: 42, special_usage: 62, super_usage: 52, risk_tolerance: 60, ring_control: 60, preferred_range: "mid", finish_priority: 72 },
    moveset: { template_base: "template_strike_01", moveset_style: "technical_striker", signature_1: "backfist", signature_2: "roundhouse_burst", signature_3: "knee_combo", finisher: "flash_high_kick", super_finisher: "critical_burst", taunt_style: "point_to_camera", intro_style: "shadow_box", victory_pose: "point_to_camera" }
  },
  zoner: {
    classification: { weight_class: "lightweight", archetype: "zoner", stance: "switch", division: "singles", gender_presentation: "neutral", alignment: "heel" },
    stats: { point_budget_total: 500, point_budget_used: 500, power: 56, speed: 76, defense: 54, grapple: 36, strike: 72, air: 78, stamina: 64, recovery: 64 },
    ai_profile: { profile_mode: "simple", base_archetype: "zoner", aggression: 40, combo_rate: 48, grapple_rate: 12, strike_rate: 62, air_rate: 70, throw_escape_rate: 58, guard_rate: 66, counter_rate: 60, special_usage: 74, super_usage: 50, risk_tolerance: 34, ring_control: 82, preferred_range: "far", finish_priority: 58 },
    moveset: { template_base: "template_zone_01", moveset_style: "anti_air_specialist", signature_1: "dropkick", signature_2: "backfist", signature_3: "roundhouse_burst", finisher: "skybreaker", super_finisher: "", taunt_style: "laugh", intro_style: "arms_crossed", victory_pose: "point_to_camera" }
  },
  counter_grappler: {
    classification: { weight_class: "heavyweight", archetype: "counter_grappler", stance: "orthodox", division: "both", gender_presentation: "neutral", alignment: "tweener" },
    stats: { point_budget_total: 500, point_budget_used: 500, power: 78, speed: 60, defense: 84, grapple: 90, strike: 58, air: 35, stamina: 84, recovery: 66 },
    ai_profile: { profile_mode: "simple", base_archetype: "counter_grappler", aggression: 42, combo_rate: 34, grapple_rate: 86, strike_rate: 38, air_rate: 18, throw_escape_rate: 72, guard_rate: 80, counter_rate: 78, special_usage: 40, super_usage: 32, risk_tolerance: 26, ring_control: 70, preferred_range: "close", finish_priority: 64 },
    moveset: { template_base: "template_counter_01", moveset_style: "chain_wrestler", signature_1: "spinebuster", signature_2: "counter_slam", signature_3: "lariat", finisher: "sitout_powerbomb", super_finisher: "storm_drop", taunt_style: "cold_stare", intro_style: "slow_walk", victory_pose: "arms_folded" }
  },
  tank: {
    classification: { weight_class: "super_heavyweight", archetype: "tank", stance: "brawler", division: "both", gender_presentation: "neutral", alignment: "heel" },
    stats: { point_budget_total: 500, point_budget_used: 500, power: 90, speed: 35, defense: 88, grapple: 76, strike: 62, air: 35, stamina: 74, recovery: 40 },
    ai_profile: { profile_mode: "simple", base_archetype: "tank", aggression: 52, combo_rate: 22, grapple_rate: 60, strike_rate: 44, air_rate: 8, throw_escape_rate: 66, guard_rate: 72, counter_rate: 55, special_usage: 38, super_usage: 30, risk_tolerance: 24, ring_control: 54, preferred_range: "close", finish_priority: 72 },
    moveset: { template_base: "template_tank_01", moveset_style: "power_grapple", signature_1: "lariat", signature_2: "spinebuster", signature_3: "suplex_throw", finisher: "super_lariat", super_finisher: "last_stand_bomb", taunt_style: "laugh", intro_style: "slow_walk", victory_pose: "roar" }
  },
  wildcard: {
    classification: { weight_class: "middleweight", archetype: "wildcard", stance: "switch", division: "both", gender_presentation: "neutral", alignment: "tweener" },
    stats: { point_budget_total: 500, point_budget_used: 500, power: 66, speed: 66, defense: 58, grapple: 52, strike: 68, air: 70, stamina: 58, recovery: 62 },
    ai_profile: { profile_mode: "simple", base_archetype: "wildcard", aggression: 62, combo_rate: 58, grapple_rate: 40, strike_rate: 58, air_rate: 56, throw_escape_rate: 54, guard_rate: 46, counter_rate: 44, special_usage: 68, super_usage: 62, risk_tolerance: 72, ring_control: 60, preferred_range: "adaptive", finish_priority: 66 },
    moveset: { template_base: "template_wild_01", moveset_style: "chaos_mixup", signature_1: "backfist", signature_2: "dropkick", signature_3: "counter_slam", finisher: "driver_drop", super_finisher: "chaos_driver", taunt_style: "hands_up", intro_style: "wild_charge", victory_pose: "belt_motion" }
  }
};

const STAT_FIELDS = ["power", "speed", "defense", "grapple", "strike", "air", "stamina", "recovery"] as const;
const AI_FIELDS = [
  "aggression",
  "combo_rate",
  "grapple_rate",
  "strike_rate",
  "air_rate",
  "throw_escape_rate",
  "guard_rate",
  "counter_rate",
  "special_usage",
  "super_usage",
  "risk_tolerance",
  "ring_control",
  "finish_priority"
] as const;

function createEmptyFighter(): FighterSubmission {
  return {
    schema_version: "1.0.0",
    fighter_id: "",
    submission_id: null,
    status: "draft",
    created_at: null,
    updated_at: null,
    base_fighter: null,
    identity: {
      display_name: "",
      nickname: "",
      announcer_name: "",
      hometown: "",
      country: "USA",
      bio_short: "",
      creator_name: "",
      creator_id: ""
    },
    classification: {
      division: "both",
      gender_presentation: "neutral",
      weight_class: "middleweight",
      archetype: "balanced",
      stance: "orthodox",
      alignment: "tweener"
    },
    appearance: {
      body_type: "athletic",
      height_class: "average",
      physique: "defined",
      skin_tone: "medium_1",
      hair_style: "short",
      hair_color: "black",
      mask_style: "none",
      facial_hair: "none",
      gear_top: "vest",
      gear_bottom: "tights",
      gloves: true,
      boots: "wrestling_boots",
      accessory: "none",
      primary_color: "red",
      secondary_color: "black",
      accent_color: "white",
      portrait_style: "intense",
      aura_fx: "none"
    },
    stats: {
      point_budget_total: 500,
      point_budget_used: 500,
      power: 65,
      speed: 65,
      defense: 65,
      grapple: 60,
      strike: 65,
      air: 60,
      stamina: 60,
      recovery: 60
    },
    ai_profile: {
      profile_mode: "simple",
      base_archetype: "balanced",
      aggression: 55,
      combo_rate: 55,
      grapple_rate: 45,
      strike_rate: 55,
      air_rate: 45,
      throw_escape_rate: 60,
      guard_rate: 55,
      counter_rate: 50,
      special_usage: 50,
      super_usage: 45,
      risk_tolerance: 50,
      ring_control: 55,
      preferred_range: "mid",
      finish_priority: 55
    },
    moveset: {
      template_base: "template_balanced_01",
      moveset_style: "balanced_pro",
      signature_1: "dropkick",
      signature_2: "backfist",
      signature_3: "suplex_throw",
      finisher: "driver_drop",
      super_finisher: "",
      taunt_style: "silent_nod",
      intro_style: "confident_walk",
      victory_pose: "arms_folded"
    },
    league_settings: {
      eligible_for_singles: true,
      eligible_for_tag: true,
      preferred_tag_role: "either",
      debut_priority: true,
      can_hold_world_title: true,
      can_hold_tag_title: true
    }
  };
}

function slugifyName(name: string) {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 32);
}

function applyArchetypeDefaults(prev: FighterSubmission, archetype: string): FighterSubmission {
  const defaults = ARCHETYPE_DEFAULTS[archetype] ?? ARCHETYPE_DEFAULTS.balanced;
  return {
    ...prev,
    classification: { ...prev.classification, ...defaults.classification, archetype },
    stats: { ...prev.stats, ...defaults.stats },
    ai_profile: { ...prev.ai_profile, ...defaults.ai_profile, base_archetype: archetype },
    moveset: { ...prev.moveset, ...defaults.moveset }
  };
}

function validateFighter(fighter: FighterSubmission) {
  const errors: string[] = [];
  const statPointsUsed = STAT_FIELDS.reduce((sum, key) => sum + fighter.stats[key], 0);
  const statPoolTotal = fighter.stats.point_budget_total;
  const remaining = statPoolTotal - statPointsUsed;

  if (!fighter.identity.display_name.trim()) errors.push("Display name is required.");
  if (fighter.identity.display_name.trim().length > 24) errors.push("Display name must be 24 characters or less.");
  if (fighter.identity.nickname.trim().length > 32) errors.push("Nickname must be 32 characters or less.");
  if (!fighter.fighter_id || !/^[a-z0-9_]{3,32}$/.test(fighter.fighter_id)) {
    errors.push("Fighter ID must be 3-32 chars using lowercase letters, numbers, and underscores.");
  }

  STAT_FIELDS.forEach((key) => {
    const value = fighter.stats[key];
    if (value < 35 || value > 95) errors.push(`${key} must be between 35 and 95.`);
  });

  const above85 = STAT_FIELDS.filter((key) => fighter.stats[key] > 85).length;
  if (above85 > 2) errors.push("No more than 2 stats can be above 85.");

  const below40 = STAT_FIELDS.filter((key) => fighter.stats[key] < 40).length;
  if (below40 > 1) errors.push("No more than 1 stat can be below 40.");

  if (remaining !== 0) errors.push(`Stat budget must equal ${statPoolTotal}. Currently ${statPointsUsed}.`);
  if (fighter.ai_profile.base_archetype !== fighter.classification.archetype) {
    errors.push("AI archetype must match classification archetype.");
  }

  AI_FIELDS.forEach((key) => {
    const value = fighter.ai_profile[key];
    if (value < 0 || value > 100) errors.push(`${key} must be between 0 and 100.`);
  });

  const sigs = [fighter.moveset.signature_1, fighter.moveset.signature_2, fighter.moveset.signature_3].filter(Boolean);
  if (new Set(sigs).size !== sigs.length) errors.push("Signature moves must be unique.");
  if (!fighter.moveset.finisher) errors.push("Finisher is required.");

  if (fighter.appearance.hair_style === "hooded" && fighter.appearance.mask_style === "full_mask") {
    errors.push("Hooded hair cannot be combined with full mask.");
  }
  if (fighter.appearance.body_type === "giant" && fighter.appearance.gear_top === "armor_light") {
    errors.push("Giant body type cannot use armor_light.");
  }

  return {
    ...fighter,
    stats: {
      ...fighter.stats,
      point_budget_used: statPointsUsed
    },
    validation: {
      is_valid: errors.length === 0,
      errors,
      stat_pool_total: statPoolTotal,
      stat_points_used: statPointsUsed,
      remaining_points: remaining
    }
  };
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ marginBottom: 28, border: "1px solid #24262d", borderRadius: 12, padding: 18, background: "#141821" }}>
      <h2 style={{ marginTop: 0, marginBottom: 14, fontSize: 22 }}>{title}</h2>
      {children}
    </section>
  );
}

function FieldLabel({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 14, fontWeight: 600 }}>
      <span>{label}</span>
      {children}
    </label>
  );
}

function Select({ value, onChange, options }: { value: string; onChange: (value: string) => void; options: readonly string[] }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} style={inputStyle}>
      {options.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  );
}

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: 8,
  border: "1px solid #3a3f4b",
  background: "#0c1018",
  color: "#f1f5f9"
};

const gridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  gap: 14
};

export default function CreatePage() {
  const [fighter, setFighter] = useState<FighterSubmission>(createEmptyFighter());
  const [baseFighters, setBaseFighters] = useState<BaseFighterOption[]>([]);
  const [message, setMessage] = useState("");
  const [isSaving, setIsSaving] = useState(false);

useEffect(() => {
  fetch("/live_roster.json")
    .then((res) => res.json())
    .then((data) => {
      const fighters = (data.base_fighters || []).map((f: any) => ({
        id: f.id,
        display_name: f.name,
        archetype: f.archetype || "unknown",
        author: f.author || "unknown",
        char_folder: f.char_folder,
        def_file: f.def_file,
        def_path: f.def_path,
        customizable: true
      }));

      setBaseFighters(fighters);
    })
    .catch(() => setBaseFighters([]));
}, []);

const validated = useMemo(() => validateFighter(fighter), [fighter]);
const remaining = validated.validation.remaining_points;

  function updateField<T extends string | number | boolean>(path: string, value: T) {
    update((draft) => {
      const parts = path.split(".");
      let cur: any = draft;
      for (let i = 0; i < parts.length - 1; i += 1) cur = cur[parts[i]];
      cur[parts[parts.length - 1]] = value;
    });
  }

  function handleDisplayName(value: string) {
    update((draft) => {
      draft.identity.display_name = value;
      if (!draft.identity.announcer_name) draft.identity.announcer_name = value;
      draft.fighter_id = slugifyName(value);
    });
  }

  function handleArchetypeChange(archetype: string) {
    setFighter((prev) => applyArchetypeDefaults(prev, archetype));
  }

  function handleBaseFighterChange(baseId: string) {
    const selected = baseFighters.find((f) => f.id === baseId) || null;
    update((draft) => {
      if (selected) {
        draft.base_fighter = {
          id: selected.id,
          display_name: selected.display_name,
          archetype: selected.archetype,
          author: selected.author,
          char_folder: selected.char_folder,
          def_file: selected.def_file,
          def_path: selected.def_path
        };
      } else {
        draft.base_fighter = null;
      }
    });
  }

  async function save(status: "draft" | "submitted") {
    setMessage("");
    setIsSaving(true);
    try {
      const now = new Date().toISOString();
      const payload = {
        ...validated,
        status,
        created_at: fighter.created_at ?? now,
        updated_at: now,
        submission_id: fighter.submission_id ?? null
      };

      const res = await fetch("/api/fighters", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setMessage(data.error || "Failed to save fighter.");
        return;
      }

      setMessage(`${status === "submitted" ? "Submitted" : "Saved"}: ${data.path || "success"}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to save fighter.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main style={{ minHeight: "100vh", background: "#090d14", color: "#f8fafc", padding: 24, fontFamily: "Arial, sans-serif" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <header style={{ marginBottom: 24 }}>
          <h1 style={{ marginBottom: 8, fontSize: 38 }}>Create Fighter</h1>
          <p style={{ margin: 0, color: "#94a3b8", maxWidth: 760 }}>
            Pick a native base fighter from the live roster, then customize appearance, stats, AI, and moveset.
          </p>
        </header>

        <Section title="Base Fighter">
          <div style={gridStyle}>
            <FieldLabel label="Choose Base Fighter">
              <select
                style={inputStyle}
                value={fighter.base_fighter?.id || ""}
                onChange={(e) => handleBaseFighterChange(e.target.value)}
              >
                <option value="">-- Select Base Fighter --</option>
                {baseFighters
                  .filter((f) => f.customizable !== false)
                  .map((f) => (
                    <option key={f.id} value={f.id}>
                      {f.display_name} ({f.archetype}) — {f.author}
                    </option>
                  ))}
              </select>
            </FieldLabel>

            <div style={{ background: "#0c1018", border: "1px solid #24262d", borderRadius: 10, padding: 14 }}>
              <strong>Selected Base:</strong>
              <div style={{ marginTop: 8, color: "#cbd5e1" }}>
                {fighter.base_fighter ? (
                  <>
                    <div>{fighter.base_fighter.display_name}</div>
                    <div>Archetype: {fighter.base_fighter.archetype}</div>
                    <div>Author: {fighter.base_fighter.author}</div>
                    <div>Folder: {fighter.base_fighter.char_folder}</div>
                    <div>DEF: {fighter.base_fighter.def_path}</div>
                  </>
                ) : (
                  <div>No base fighter selected. Archetype template fallback will be used.</div>
                )}
              </div>
            </div>
          </div>
        </Section>

        <Section title="Identity">
          <div style={gridStyle}>
            <FieldLabel label="Display Name">
              <input style={inputStyle} value={fighter.identity.display_name} onChange={(e) => handleDisplayName(e.target.value)} />
            </FieldLabel>
            <FieldLabel label="Fighter ID">
              <input style={inputStyle} value={fighter.fighter_id} onChange={(e) => updateField("fighter_id", slugifyName(e.target.value))} />
            </FieldLabel>
            <FieldLabel label="Nickname">
              <input style={inputStyle} value={fighter.identity.nickname} onChange={(e) => updateField("identity.nickname", e.target.value)} />
            </FieldLabel>
            <FieldLabel label="Announcer Name">
              <input style={inputStyle} value={fighter.identity.announcer_name} onChange={(e) => updateField("identity.announcer_name", e.target.value)} />
            </FieldLabel>
            <FieldLabel label="Creator Name">
              <input style={inputStyle} value={fighter.identity.creator_name} onChange={(e) => updateField("identity.creator_name", e.target.value)} />
            </FieldLabel>
            <FieldLabel label="Creator ID">
              <input style={inputStyle} value={fighter.identity.creator_id} onChange={(e) => updateField("identity.creator_id", e.target.value)} />
            </FieldLabel>
            <FieldLabel label="Hometown">
              <input style={inputStyle} value={fighter.identity.hometown} onChange={(e) => updateField("identity.hometown", e.target.value)} />
            </FieldLabel>
            <FieldLabel label="Country">
              <input style={inputStyle} value={fighter.identity.country} onChange={(e) => updateField("identity.country", e.target.value)} />
            </FieldLabel>
          </div>
          <div style={{ marginTop: 14 }}>
            <FieldLabel label="Short Bio">
              <textarea style={{ ...inputStyle, minHeight: 96, resize: "vertical" }} value={fighter.identity.bio_short} onChange={(e) => updateField("identity.bio_short", e.target.value)} />
            </FieldLabel>
          </div>
        </Section>

        <Section title="Classification">
          <div style={gridStyle}>
            <FieldLabel label="Archetype">
              <Select value={fighter.classification.archetype} onChange={handleArchetypeChange} options={ENUMS.archetype} />
            </FieldLabel>
            <FieldLabel label="Division">
              <Select value={fighter.classification.division} onChange={(v) => updateField("classification.division", v)} options={ENUMS.division} />
            </FieldLabel>
            <FieldLabel label="Weight Class">
              <Select value={fighter.classification.weight_class} onChange={(v) => updateField("classification.weight_class", v)} options={ENUMS.weight_class} />
            </FieldLabel>
            <FieldLabel label="Stance">
              <Select value={fighter.classification.stance} onChange={(v) => updateField("classification.stance", v)} options={ENUMS.stance} />
            </FieldLabel>
            <FieldLabel label="Alignment">
              <Select value={fighter.classification.alignment} onChange={(v) => updateField("classification.alignment", v)} options={ENUMS.alignment} />
            </FieldLabel>
            <FieldLabel label="Gender Presentation">
              <Select value={fighter.classification.gender_presentation} onChange={(v) => updateField("classification.gender_presentation", v)} options={ENUMS.gender_presentation} />
            </FieldLabel>
          </div>
        </Section>

        <Section title="Appearance">
          <div style={gridStyle}>
            <FieldLabel label="Body Type"><Select value={fighter.appearance.body_type} onChange={(v) => updateField("appearance.body_type", v)} options={ENUMS.body_type} /></FieldLabel>
            <FieldLabel label="Height Class"><Select value={fighter.appearance.height_class} onChange={(v) => updateField("appearance.height_class", v)} options={ENUMS.height_class} /></FieldLabel>
            <FieldLabel label="Physique"><Select value={fighter.appearance.physique} onChange={(v) => updateField("appearance.physique", v)} options={ENUMS.physique} /></FieldLabel>
            <FieldLabel label="Skin Tone"><Select value={fighter.appearance.skin_tone} onChange={(v) => updateField("appearance.skin_tone", v)} options={ENUMS.skin_tone} /></FieldLabel>
            <FieldLabel label="Hair Style"><Select value={fighter.appearance.hair_style} onChange={(v) => updateField("appearance.hair_style", v)} options={ENUMS.hair_style} /></FieldLabel>
            <FieldLabel label="Hair Color"><Select value={fighter.appearance.hair_color} onChange={(v) => updateField("appearance.hair_color", v)} options={ENUMS.hair_color} /></FieldLabel>
            <FieldLabel label="Mask Style"><Select value={fighter.appearance.mask_style} onChange={(v) => updateField("appearance.mask_style", v)} options={ENUMS.mask_style} /></FieldLabel>
            <FieldLabel label="Facial Hair"><Select value={fighter.appearance.facial_hair} onChange={(v) => updateField("appearance.facial_hair", v)} options={ENUMS.facial_hair} /></FieldLabel>
            <FieldLabel label="Gear Top"><Select value={fighter.appearance.gear_top} onChange={(v) => updateField("appearance.gear_top", v)} options={ENUMS.gear_top} /></FieldLabel>
            <FieldLabel label="Gear Bottom"><Select value={fighter.appearance.gear_bottom} onChange={(v) => updateField("appearance.gear_bottom", v)} options={ENUMS.gear_bottom} /></FieldLabel>
            <FieldLabel label="Boots"><Select value={fighter.appearance.boots} onChange={(v) => updateField("appearance.boots", v)} options={ENUMS.boots} /></FieldLabel>
            <FieldLabel label="Accessory"><Select value={fighter.appearance.accessory} onChange={(v) => updateField("appearance.accessory", v)} options={ENUMS.accessory} /></FieldLabel>
            <FieldLabel label="Primary Color"><Select value={fighter.appearance.primary_color} onChange={(v) => updateField("appearance.primary_color", v)} options={ENUMS.color} /></FieldLabel>
            <FieldLabel label="Secondary Color"><Select value={fighter.appearance.secondary_color} onChange={(v) => updateField("appearance.secondary_color", v)} options={ENUMS.color} /></FieldLabel>
            <FieldLabel label="Accent Color"><Select value={fighter.appearance.accent_color} onChange={(v) => updateField("appearance.accent_color", v)} options={ENUMS.color} /></FieldLabel>
            <FieldLabel label="Portrait Style"><Select value={fighter.appearance.portrait_style} onChange={(v) => updateField("appearance.portrait_style", v)} options={ENUMS.portrait_style} /></FieldLabel>
            <FieldLabel label="Aura FX"><Select value={fighter.appearance.aura_fx} onChange={(v) => updateField("appearance.aura_fx", v)} options={ENUMS.aura_fx} /></FieldLabel>
            <FieldLabel label="Gloves">
              <select style={inputStyle} value={fighter.appearance.gloves ? "true" : "false"} onChange={(e) => updateField("appearance.gloves", e.target.value === "true")}>
                <option value="true">true</option>
                <option value="false">false</option>
              </select>
            </FieldLabel>
          </div>
        </Section>

        <Section title="Stats">
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, marginBottom: 16, flexWrap: "wrap" }}>
            <div style={{ padding: "10px 14px", background: "#0c1018", borderRadius: 10, border: "1px solid #24262d" }}>
              <strong>Total Budget:</strong> {validated.validation.stat_pool_total}
            </div>
            <div style={{ padding: "10px 14px", background: "#0c1018", borderRadius: 10, border: "1px solid #24262d" }}>
              <strong>Points Used:</strong> {validated.validation.stat_points_used}
            </div>
            <div style={{ padding: "10px 14px", background: remaining === 0 ? "#062d1f" : "#33250a", borderRadius: 10, border: "1px solid #24262d" }}>
              <strong>Remaining:</strong> {remaining}
            </div>
          </div>
          <div style={gridStyle}>
            {STAT_FIELDS.map((stat) => (
              <div key={stat} style={{ padding: 12, background: "#0c1018", borderRadius: 10, border: "1px solid #24262d" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                  <strong style={{ textTransform: "capitalize" }}>{stat.replace("_", " ")}</strong>
                  <span>{fighter.stats[stat]}</span>
                </div>
                <input
                  style={{ width: "100%" }}
                  type="range"
                  min={35}
                  max={95}
                  value={fighter.stats[stat]}
                  onChange={(e) => updateField(`stats.${stat}`, Number(e.target.value))}
                />
              </div>
            ))}
          </div>
        </Section>

        <Section title="AI Profile">
          <div style={gridStyle}>
            <FieldLabel label="Profile Mode"><Select value={fighter.ai_profile.profile_mode} onChange={(v) => updateField("ai_profile.profile_mode", v)} options={ENUMS.profile_mode} /></FieldLabel>
            <FieldLabel label="Preferred Range"><Select value={fighter.ai_profile.preferred_range} onChange={(v) => updateField("ai_profile.preferred_range", v)} options={ENUMS.preferred_range} /></FieldLabel>
          </div>
          <div style={{ marginTop: 16, ...gridStyle }}>
            {AI_FIELDS.map((field) => (
              <div key={field} style={{ padding: 12, background: "#0c1018", borderRadius: 10, border: "1px solid #24262d" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                  <strong style={{ textTransform: "capitalize" }}>{field.replaceAll("_", " ")}</strong>
                  <span>{fighter.ai_profile[field]}</span>
                </div>
                <input
                  style={{ width: "100%" }}
                  type="range"
                  min={0}
                  max={100}
                  value={fighter.ai_profile[field]}
                  onChange={(e) => updateField(`ai_profile.${field}`, Number(e.target.value))}
                  disabled={fighter.ai_profile.profile_mode === "simple"}
                />
              </div>
            ))}
          </div>
        </Section>

        <Section title="Moveset">
          <div style={gridStyle}>
            <FieldLabel label="Template Base"><Select value={fighter.moveset.template_base} onChange={(v) => updateField("moveset.template_base", v)} options={ENUMS.template_base} /></FieldLabel>
            <FieldLabel label="Moveset Style"><Select value={fighter.moveset.moveset_style} onChange={(v) => updateField("moveset.moveset_style", v)} options={ENUMS.moveset_style} /></FieldLabel>
            <FieldLabel label="Signature 1"><Select value={fighter.moveset.signature_1} onChange={(v) => updateField("moveset.signature_1", v)} options={ENUMS.moves} /></FieldLabel>
            <FieldLabel label="Signature 2"><Select value={fighter.moveset.signature_2} onChange={(v) => updateField("moveset.signature_2", v)} options={ENUMS.moves} /></FieldLabel>
            <FieldLabel label="Signature 3"><Select value={fighter.moveset.signature_3} onChange={(v) => updateField("moveset.signature_3", v)} options={ENUMS.moves} /></FieldLabel>
            <FieldLabel label="Finisher"><Select value={fighter.moveset.finisher} onChange={(v) => updateField("moveset.finisher", v)} options={ENUMS.finishers} /></FieldLabel>
            <FieldLabel label="Super Finisher"><Select value={fighter.moveset.super_finisher} onChange={(v) => updateField("moveset.super_finisher", v)} options={ENUMS.super_finishers} /></FieldLabel>
            <FieldLabel label="Taunt Style"><Select value={fighter.moveset.taunt_style} onChange={(v) => updateField("moveset.taunt_style", v)} options={ENUMS.taunt_style} /></FieldLabel>
            <FieldLabel label="Intro Style"><Select value={fighter.moveset.intro_style} onChange={(v) => updateField("moveset.intro_style", v)} options={ENUMS.intro_style} /></FieldLabel>
            <FieldLabel label="Victory Pose"><Select value={fighter.moveset.victory_pose} onChange={(v) => updateField("moveset.victory_pose", v)} options={ENUMS.victory_pose} /></FieldLabel>
          </div>
        </Section>

        <Section title="League Settings">
          <div style={gridStyle}>
            <FieldLabel label="Eligible for Singles">
              <select style={inputStyle} value={fighter.league_settings.eligible_for_singles ? "true" : "false"} onChange={(e) => updateField("league_settings.eligible_for_singles", e.target.value === "true")}>
                <option value="true">true</option>
                <option value="false">false</option>
              </select>
            </FieldLabel>
            <FieldLabel label="Eligible for Tag">
              <select style={inputStyle} value={fighter.league_settings.eligible_for_tag ? "true" : "false"} onChange={(e) => updateField("league_settings.eligible_for_tag", e.target.value === "true")}>
                <option value="true">true</option>
                <option value="false">false</option>
              </select>
            </FieldLabel>
            <FieldLabel label="Preferred Tag Role"><Select value={fighter.league_settings.preferred_tag_role} onChange={(v) => updateField("league_settings.preferred_tag_role", v)} options={ENUMS.preferred_tag_role} /></FieldLabel>
            <FieldLabel label="Debut Priority">
              <select style={inputStyle} value={fighter.league_settings.debut_priority ? "true" : "false"} onChange={(e) => updateField("league_settings.debut_priority", e.target.value === "true")}>
                <option value="true">true</option>
                <option value="false">false</option>
              </select>
            </FieldLabel>
            <FieldLabel label="Can Hold World Title">
              <select style={inputStyle} value={fighter.league_settings.can_hold_world_title ? "true" : "false"} onChange={(e) => updateField("league_settings.can_hold_world_title", e.target.value === "true")}>
                <option value="true">true</option>
                <option value="false">false</option>
              </select>
            </FieldLabel>
            <FieldLabel label="Can Hold Tag Title">
              <select style={inputStyle} value={fighter.league_settings.can_hold_tag_title ? "true" : "false"} onChange={(e) => updateField("league_settings.can_hold_tag_title", e.target.value === "true")}>
                <option value="true">true</option>
                <option value="false">false</option>
              </select>
            </FieldLabel>
          </div>
        </Section>

        <Section title="Review">
          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 16 }}>
            <div style={{ background: "#0c1018", borderRadius: 10, padding: 16, border: "1px solid #24262d" }}>
              <h3 style={{ marginTop: 0 }}>Fighter Summary</h3>
              <p><strong>Name:</strong> {fighter.identity.display_name || "—"}</p>
              <p><strong>Base Fighter:</strong> {fighter.base_fighter?.display_name || "Archetype Template Fallback"}</p>
              <p><strong>Archetype:</strong> {fighter.classification.archetype}</p>
              <p><strong>Weight Class:</strong> {fighter.classification.weight_class}</p>
              <p><strong>Fight Style:</strong> {fighter.moveset.moveset_style}</p>
              <p><strong>Primary Colors:</strong> {fighter.appearance.primary_color} / {fighter.appearance.secondary_color}</p>
              <p><strong>Preferred Range:</strong> {fighter.ai_profile.preferred_range}</p>
              <p><strong>Finisher:</strong> {fighter.moveset.finisher}</p>
            </div>
            <div style={{ background: "#0c1018", borderRadius: 10, padding: 16, border: "1px solid #24262d" }}>
              <h3 style={{ marginTop: 0 }}>Validation</h3>
              <p style={{ color: validated.validation.is_valid ? "#4ade80" : "#f87171", fontWeight: 700 }}>
                {validated.validation.is_valid ? "Ready to submit" : "Needs fixes"}
              </p>
              {validated.validation.errors.length > 0 ? (
                <ul style={{ paddingLeft: 18, margin: 0 }}>
                  {validated.validation.errors.map((err) => (
                    <li key={err} style={{ marginBottom: 6 }}>{err}</li>
                  ))}
                </ul>
              ) : (
                <p style={{ margin: 0 }}>No validation issues found.</p>
              )}
            </div>
          </div>

          <details style={{ marginTop: 16 }}>
            <summary style={{ cursor: "pointer", fontWeight: 700 }}>Show submission JSON</summary>
            <pre style={{ marginTop: 12, background: "#020617", color: "#e2e8f0", padding: 14, borderRadius: 10, overflow: "auto", border: "1px solid #24262d" }}>
              {JSON.stringify(validated, null, 2)}
            </pre>
          </details>
        </Section>

        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 16 }}>
          <button style={buttonStyleSecondary} onClick={() => save("draft")} disabled={isSaving}>
            {isSaving ? "Saving..." : "Save Draft"}
          </button>
          <button style={buttonStylePrimary} onClick={() => save("submitted")} disabled={isSaving || !validated.validation.is_valid}>
            {isSaving ? "Submitting..." : "Submit Fighter"}
          </button>
        </div>

        {message && (
          <div style={{ padding: 14, borderRadius: 10, background: "#0c1018", border: "1px solid #24262d", color: "#cbd5e1" }}>
            {message}
          </div>
        )}
      </div>
    </main>
  );
}

const buttonStylePrimary: React.CSSProperties = {
  padding: "12px 18px",
  borderRadius: 10,
  border: "1px solid #2563eb",
  background: "#2563eb",
  color: "white",
  fontWeight: 700,
  cursor: "pointer"
};

const buttonStyleSecondary: React.CSSProperties = {
  padding: "12px 18px",
  borderRadius: 10,
  border: "1px solid #475569",
  background: "#0f172a",
  color: "white",
  fontWeight: 700,
  cursor: "pointer"
};
