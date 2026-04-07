import assetRegistry from "../config/fighter_asset_registry.json";
import enums from "../config/fighter_enums.json";
import rules from "../config/fighter_validation_rules.json";

type Dict = Record<string, any>;

const REQUIRED_TOP_LEVEL = [
  "fighter_id",
  "identity",
  "classification",
  "appearance",
  "stats",
  "ai_profile",
  "moveset",
] as const;

const REQUIRED_STATS = (rules as Dict).stat_rules.point_budget_fields as string[];
const REQUIRED_AI = [
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
  "finish_priority",
] as const;

function slugify(value: unknown) {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[-\s]+/g, "_")
    .replace(/[^a-z0-9_]/g, "");
}

function includesValue(options: unknown, value: unknown) {
  return Array.isArray(options) && options.includes(value);
}

function validateEnumSection(section: string, values: Dict, errors: string[]) {
  const enumSection = (enums as Dict)[section];
  if (!enumSection || typeof enumSection !== "object") {
    return;
  }

  for (const [key, value] of Object.entries(values)) {
    if (!(key in enumSection)) {
      continue;
    }
    if (!includesValue(enumSection[key], value)) {
      errors.push(`Invalid ${section}.${key}: ${value}`);
    }
  }
}

export function validateSubmittedFighter(fighter: Dict): string[] {
  const errors: string[] = [];

  for (const key of REQUIRED_TOP_LEVEL) {
    if (!(key in fighter) || typeof fighter[key] !== "object" || fighter[key] === null) {
      errors.push(`Missing required section: ${key}`);
    }
  }

  if (errors.length > 0) {
    return errors;
  }

  const fighterId = String(fighter.fighter_id ?? "").trim();
  const displayName = String(fighter.identity?.display_name ?? "").trim();
  const archetype = String(fighter.classification?.archetype ?? "");
  const alignment = String(fighter.classification?.alignment ?? "");
  const stats = fighter.stats as Dict;
  const aiProfile = fighter.ai_profile as Dict;
  const assembly = (fighter.assembly ?? {}) as Dict;
  const moveset = fighter.moveset as Dict;

  if (!new RegExp((rules as Dict).identity_rules.fighter_id.pattern).test(fighterId)) {
    errors.push("fighter_id must be 3-32 lowercase letters, numbers, or underscores.");
  }

  if (!displayName) {
    errors.push("identity.display_name is required.");
  }

  validateEnumSection("classification", fighter.classification, errors);
  validateEnumSection("appearance", fighter.appearance, errors);
  validateEnumSection("moveset", {
    template_base: moveset.template_base,
    moveset_style: moveset.moveset_style,
    taunt_style: moveset.taunt_style,
    intro_style: moveset.intro_style,
    victory_pose: moveset.victory_pose,
  }, errors);
  validateEnumSection("ai_profile", {
    profile_mode: aiProfile.profile_mode,
    preferred_range: aiProfile.preferred_range,
  }, errors);

  const assemblyEnums = (enums as Dict).assembly ?? {};
  for (const key of Object.keys(assembly)) {
    if (assemblyEnums[key] && !includesValue(assemblyEnums[key], assembly[key])) {
      errors.push(`Invalid assembly.${key}: ${assembly[key]}`);
    }
  }

  let total = 0;
  const minStat = Number((rules as Dict).stat_rules.minimum_per_stat);
  const maxStat = Number((rules as Dict).stat_rules.maximum_per_stat);
  const targetTotal = Number((rules as Dict).stat_rules.point_budget_total);
  for (const stat of REQUIRED_STATS) {
    const value = Number(stats[stat]);
    if (!Number.isFinite(value)) {
      errors.push(`Stat ${stat} must be numeric.`);
      continue;
    }
    if (value < minStat || value > maxStat) {
      errors.push(`Stat ${stat} must be between ${minStat} and ${maxStat}.`);
    }
    total += value;
  }
  if (total !== targetTotal) {
    errors.push(`Stat budget must equal ${targetTotal}.`);
  }

  if (String(aiProfile.base_archetype ?? "") !== archetype) {
    errors.push("ai_profile.base_archetype must match classification.archetype.");
  }

  for (const field of REQUIRED_AI) {
    const value = Number(aiProfile[field]);
    if (!Number.isFinite(value) || value < 0 || value > 100) {
      errors.push(`AI field ${field} must be between 0 and 100.`);
    }
  }

  if ((rules as Dict).moveset_rules.signature_moves_must_be_unique) {
    const signatures = [moveset.signature_1, moveset.signature_2, moveset.signature_3].filter(Boolean);
    if (new Set(signatures).size !== signatures.length) {
      errors.push("Signature moves must be unique.");
    }
  }

  const templates = (assetRegistry as Dict).templates ?? {};
  const templateCfg = templates[moveset.template_base];
  if (!templateCfg) {
    errors.push(`Unknown template_base: ${moveset.template_base}`);
  } else {
    if (Array.isArray(templateCfg.archetypes) && !templateCfg.archetypes.includes(archetype)) {
      errors.push(`moveset.template_base is incompatible with archetype ${archetype}.`);
    }
    if (
      Array.isArray(templateCfg.allowed_moveset_styles) &&
      !templateCfg.allowed_moveset_styles.includes(moveset.moveset_style)
    ) {
      errors.push(`moveset.moveset_style is not allowed for ${moveset.template_base}.`);
    }
  }

  const disallowed = ((assetRegistry as Dict).compatibility_rules?.disallowed_combinations ?? []) as Dict[];
  for (const combo of disallowed) {
    const [sectionA, fieldA] = String(combo.field_a).split(".");
    const [sectionB, fieldB] = String(combo.field_b).split(".");
    if (fighter[sectionA]?.[fieldA] === combo.value_a && fighter[sectionB]?.[fieldB] === combo.value_b) {
      errors.push(combo.reason ?? `${combo.field_a} cannot be combined with ${combo.field_b}.`);
    }
  }

  if (Object.keys(assembly).length > 0) {
    const registry = ((assetRegistry as Dict).assembly_modules ?? {}) as Dict;
    const bodyClass = slugify(assembly.body_class);
    const bodyCfg = registry.body_class?.[bodyClass];
    if (!bodyCfg) {
      errors.push(`Unknown assembly.body_class: ${assembly.body_class}`);
    } else {
      const allowedArchetypes = Array.isArray(bodyCfg.allowed_archetypes)
        ? bodyCfg.allowed_archetypes.map(slugify)
        : [];
      if (allowedArchetypes.length > 0 && !allowedArchetypes.includes(slugify(archetype))) {
        errors.push(`Body class ${assembly.body_class} is incompatible with archetype ${archetype}.`);
      }
    }

    const moduleChecks: Array<[string, string, string]> = [
      ["locomotion_package", "allowed_body_classes", bodyClass],
      ["strike_package", "allowed_archetypes", slugify(archetype)],
      ["grapple_package", "allowed_archetypes", slugify(archetype)],
      ["special_package", "allowed_archetypes", slugify(archetype)],
      ["intro_package", "allowed_alignments", slugify(alignment)],
      ["victory_package", "allowed_alignments", slugify(alignment)],
    ];

    for (const [name, ruleKey, expected] of moduleChecks) {
      const key = slugify(assembly[name]);
      const cfg = registry[name]?.[key];
      if (!cfg) {
        errors.push(`Unknown assembly.${name}: ${assembly[name]}`);
        continue;
      }
      const allowed = Array.isArray(cfg[ruleKey]) ? cfg[ruleKey].map(slugify) : [];
      if (allowed.length > 0 && !allowed.includes(expected)) {
        errors.push(`Assembly ${name}=${assembly[name]} is incompatible with ${expected}.`);
      }
    }
  }

  return errors;
}
