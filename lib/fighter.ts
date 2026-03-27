export type FighterDraft = {
  version: 1;
  fighter_id: string;
  status: "draft" | "submitted";
  identity: {
    name: string;
    nickname: string;
    creator_name: string;
    hometown: string;
    bio: string;
    intro_quote: string;
    win_quote: string;
  };
  visuals: {
    portrait_file: string;
    palette: string;
    body_template: string;
    stance_template: string;
    emblem: string;
  };
  build: {
    archetype: string;
    stats: {
      power: number;
      defense: number;
      speed: number;
      health: number;
      aggression: number;
    };
    move_package: string;
    trait: string;
    super_style: string;
  };
  validation: {
    stat_min: number;
    stat_max: number;
    stat_pool_total: number;
    stat_points_used: number;
    is_valid: boolean;
    errors: string[];
  };
  submission: {
    submitted_at: string | null;
    approved_at: string | null;
    review_notes: string;
  };
};

export function slugifyName(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-");
}

export function createEmptyFighter(): FighterDraft {
  return {
    version: 1,
    fighter_id: "",
    status: "draft",
    identity: {
      name: "",
      nickname: "",
      creator_name: "",
      hometown: "",
      bio: "",
      intro_quote: "",
      win_quote: ""
    },
    visuals: {
      portrait_file: "",
      palette: "",
      body_template: "",
      stance_template: "",
      emblem: ""
    },
    build: {
      archetype: "",
      stats: {
        power: 76,
        defense: 76,
        speed: 76,
        health: 76,
        aggression: 76
      },
      move_package: "",
      trait: "",
      super_style: ""
    },
    validation: {
      stat_min: 50,
      stat_max: 100,
      stat_pool_total: 380,
      stat_points_used: 380,
      is_valid: false,
      errors: []
    },
    submission: {
      submitted_at: null,
      approved_at: null,
      review_notes: ""
    }
  };
}