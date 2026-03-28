MUFC new-model clean set

Contents
- scripts/generate_fighter.py
- scripts/publish_fighter.py
- scripts/import_supabase_submissions.py
- app/create/page.tsx
- app/api/fighters/route.ts

Install
1. Replace the matching files in your repo with these versions.
2. Keep your config files in:
   config/fighter_schema.json
   config/fighter_enums.json
   config/fighter_asset_registry.json
   config/fighter_validation_rules.json
3. Make sure your template characters exist in /chars using names like:
   template_balanced_01
   template_rush_01
   template_grapple_01
   template_strike_01
   template_zone_01
   template_counter_01
   template_tank_01
   template_wild_01

Recommended test flow
1. Submit a fighter from /create
2. Run:
   py scripts\import_supabase_submissions.py
3. Or run directly:
   py scripts\generate_fighter.py <fighter_id>
   py scripts\publish_fighter.py <fighter_id>

Notes
- This set is aligned to the new model:
  fighter_id
  identity
  classification
  appearance
  stats
  ai_profile
  moveset
  league_settings
- Older approved fighters should be resubmitted or migrated.