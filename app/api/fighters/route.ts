import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../../lib/supabase";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const fighter = await req.json();

    if (!fighter?.fighter_id) {
      return NextResponse.json({ error: "fighter_id missing" }, { status: 400 });
    }

    const { error } = await supabase.from("fighter_submissions").insert({
      fighter_id: fighter.fighter_id,
      status: fighter.status || "submitted",
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