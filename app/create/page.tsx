"use client";

import { useMemo, useState } from "react";
import { createEmptyFighter, FighterDraft } from "../../lib/fighter";
import { validateFighter } from "../../lib/validateFighter";
import { presets } from "../../lib/presets";

export default function CreatePage() {
  const [fighter, setFighter] = useState<FighterDraft>(createEmptyFighter());
  const [message, setMessage] = useState<string>("");

  const validated = useMemo(() => validateFighter(fighter, presets), [fighter]);

  function setField(path: string, value: string | number) {
    setFighter((prev) => {
      const copy = structuredClone(prev) as FighterDraft;
      const parts = path.split(".");
      let cur: any = copy;
      for (let i = 0; i < parts.length - 1; i++) cur = cur[parts[i]];
      cur[parts[parts.length - 1]] = value;
      return copy;
    });
  }

  async function save(status: "draft" | "submitted") {
    setMessage("");
    const payload: FighterDraft = {
      ...validated,
      status,
      submission: {
        ...validated.submission,
        submitted_at: status === "submitted" ? new Date().toISOString() : null
      }
    };

    const res = await fetch("/api/fighters", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) {
      setMessage(data.error || "Failed to save fighter.");
      return;
    }

    setMessage(`${status === "submitted" ? "Submitted" : "Saved"}: ${data.path}`);
  }

  const remaining = validated.validation.stat_pool_total - validated.validation.stat_points_used;

  return (
    <main style={{ padding: 24, fontFamily: "Arial, sans-serif", maxWidth: 900 }}>
      <h1>Create Fighter</h1>

      <h2>Identity</h2>
      <input placeholder="Name" value={fighter.identity.name} onChange={(e)=>setField("identity.name", e.target.value)} />
      <input placeholder="Nickname" value={fighter.identity.nickname} onChange={(e)=>setField("identity.nickname", e.target.value)} />
      <input placeholder="Creator Name" value={fighter.identity.creator_name} onChange={(e)=>setField("identity.creator_name", e.target.value)} />
      <input placeholder="Hometown" value={fighter.identity.hometown} onChange={(e)=>setField("identity.hometown", e.target.value)} />
      <textarea placeholder="Bio" value={fighter.identity.bio} onChange={(e)=>setField("identity.bio", e.target.value)} />
      <input placeholder="Intro Quote" value={fighter.identity.intro_quote} onChange={(e)=>setField("identity.intro_quote", e.target.value)} />
      <input placeholder="Win Quote" value={fighter.identity.win_quote} onChange={(e)=>setField("identity.win_quote", e.target.value)} />

      <h2>Look</h2>
      <input placeholder="Portrait filename" value={fighter.visuals.portrait_file} onChange={(e)=>setField("visuals.portrait_file", e.target.value)} />

      <select value={fighter.visuals.palette} onChange={(e)=>setField("visuals.palette", e.target.value)}>
        <option value="">Select Palette</option>
        {presets.palettes.map((v) => <option key={v} value={v}>{v}</option>)}
      </select>

      <select value={fighter.visuals.body_template} onChange={(e)=>setField("visuals.body_template", e.target.value)}>
        <option value="">Select Body Template</option>
        {presets.body_templates.map((v) => <option key={v} value={v}>{v}</option>)}
      </select>

      <select value={fighter.visuals.stance_template} onChange={(e)=>setField("visuals.stance_template", e.target.value)}>
        <option value="">Select Stance Template</option>
        {presets.stance_templates.map((v) => <option key={v} value={v}>{v}</option>)}
      </select>

      <select value={fighter.visuals.emblem} onChange={(e)=>setField("visuals.emblem", e.target.value)}>
        <option value="">Select Emblem</option>
        {presets.emblems.map((v) => <option key={v} value={v}>{v}</option>)}
      </select>

      <h2>Style</h2>
      <select value={fighter.build.archetype} onChange={(e)=>setField("build.archetype", e.target.value)}>
        <option value="">Select Archetype</option>
        {presets.archetypes.map((v) => <option key={v} value={v}>{v}</option>)}
      </select>

      <select value={fighter.build.move_package} onChange={(e)=>setField("build.move_package", e.target.value)}>
        <option value="">Select Move Package</option>
        {presets.move_packages.map((v) => <option key={v} value={v}>{v}</option>)}
      </select>

      <select value={fighter.build.trait} onChange={(e)=>setField("build.trait", e.target.value)}>
        <option value="">Select Trait</option>
        {presets.traits.map((v) => <option key={v} value={v}>{v}</option>)}
      </select>

      <select value={fighter.build.super_style} onChange={(e)=>setField("build.super_style", e.target.value)}>
        <option value="">Select Super Style</option>
        {presets.super_styles.map((v) => <option key={v} value={v}>{v}</option>)}
      </select>

      <h2>Stats</h2>
      <p>Points remaining: {remaining}</p>

      {(["power","defense","speed","health","aggression"] as const).map((stat) => (
        <div key={stat}>
          <label>{stat}: {fighter.build.stats[stat]}</label>
          <input
            type="range"
            min={50}
            max={100}
            value={fighter.build.stats[stat]}
            onChange={(e)=>setField(`build.stats.${stat}`, Number(e.target.value))}
          />
        </div>
      ))}

      <h2>Review</h2>
      <pre style={{ background: "#111", color: "#eee", padding: 12, overflow: "auto" }}>
        {JSON.stringify(validated, null, 2)}
      </pre>

      {!validated.validation.is_valid && (
        <div style={{ color: "red" }}>
          <h3>Validation Errors</h3>
          <ul>
            {validated.validation.errors.map((err) => <li key={err}>{err}</li>)}
          </ul>
        </div>
      )}

      <div style={{ display: "flex", gap: 12 }}>
        <button onClick={() => save("draft")}>Save Draft</button>
        <button onClick={() => save("submitted")} disabled={!validated.validation.is_valid}>
          Submit Fighter
        </button>
      </div>

      {message && <p>{message}</p>}
    </main>
  );
}