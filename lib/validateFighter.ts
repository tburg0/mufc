import { FighterDraft, slugifyName } from "./fighter";

type PresetMap = {
  archetypes: string[];
  palettes: string[];
  body_templates: string[];
  stance_templates: string[];
  emblems: string[];
  move_packages: string[];
  traits: string[];
  super_styles: string[];
};

export function validateFighter(
  fighter: FighterDraft,
  presets: PresetMap
): FighterDraft {
  const errors: string[] = [];

  const statMin = 50;
  const statMax = 100;
  const statPoolTotal = 380;

  const { power, defense, speed, health, aggression } = fighter.build.stats;
  const total = power + defense + speed + health + aggression;

  if (!fighter.identity.name.trim()) errors.push("Name is required.");
  if (fighter.identity.name.trim().length > 20) errors.push("Name must be 20 characters or fewer.");
  if (!fighter.identity.creator_name.trim()) errors.push("Creator name is required.");

  if (!presets.archetypes.includes(fighter.build.archetype)) errors.push("Invalid archetype.");
  if (!presets.palettes.includes(fighter.visuals.palette)) errors.push("Invalid palette.");
  if (!presets.body_templates.includes(fighter.visuals.body_template)) errors.push("Invalid body template.");
  if (!presets.stance_templates.includes(fighter.visuals.stance_template)) errors.push("Invalid stance template.");
  if (!presets.emblems.includes(fighter.visuals.emblem)) errors.push("Invalid emblem.");
  if (!presets.move_packages.includes(fighter.build.move_package)) errors.push("Invalid move package.");
  if (!presets.traits.includes(fighter.build.trait)) errors.push("Invalid trait.");
  if (!presets.super_styles.includes(fighter.build.super_style)) errors.push("Invalid super style.");

  const stats = [power, defense, speed, health, aggression];
  for (const s of stats) {
    if (s < statMin || s > statMax) {
      errors.push(`All stats must be between ${statMin} and ${statMax}.`);
      break;
    }
  }

  if (total !== statPoolTotal) {
    errors.push(`Stat total must equal ${statPoolTotal}. Current total: ${total}.`);
  }

  const fighter_id = slugifyName(fighter.identity.name);

  return {
    ...fighter,
    fighter_id,
    validation: {
      stat_min: statMin,
      stat_max: statMax,
      stat_pool_total: statPoolTotal,
      stat_points_used: total,
      is_valid: errors.length === 0,
      errors
    }
  };
}