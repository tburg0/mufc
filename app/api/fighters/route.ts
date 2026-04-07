import { NextRequest, NextResponse } from "next/server";
import { getSupabaseClient } from "../../../lib/supabase";
import { validateSubmittedFighter } from "../../../lib/fighter-validation";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const supabase = getSupabaseClient();
    const fighter = await req.json();
    const status = fighter.status || "submitted";

    if (!fighter?.fighter_id) {
      return NextResponse.json({ error: "fighter_id missing" }, { status: 400 });
    }

    if (status === "submitted") {
      const errors = validateSubmittedFighter(fighter);
      if (errors.length > 0) {
        return NextResponse.json(
          { error: "Submission failed validation.", details: errors },
          { status: 400 }
        );
      }
    }

    const { error } = await supabase.from("fighter_submissions").insert({
      fighter_id: fighter.fighter_id,
      status,
      fighter_data: fighter
    });

    if (error) {
      return NextResponse.json(
        { error: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json({ ok: true });
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || "Failed to save fighter." },
      { status: 500 }
    );
  }
}
