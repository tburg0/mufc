import { NextRequest, NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";
import { spawn } from "child_process";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function runPython(scriptPath: string, args: string[] = []) {
  return new Promise<{ code: number | null; stdout: string; stderr: string }>((resolve) => {
    const commands =
      process.platform === "win32"
        ? ["py", "-3", scriptPath, ...args]
        : ["python3", scriptPath, ...args];

    const child = spawn(commands[0], commands.slice(1), {
      cwd: process.cwd(),
      shell: false
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (d) => (stdout += d.toString()));
    child.stderr.on("data", (d) => (stderr += d.toString()));

    child.on("error", (err) => {
      stderr += err.message;
      resolve({ code: -1, stdout, stderr });
    });

    child.on("close", (code) => resolve({ code, stdout, stderr }));
  });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { fighter_id, action } = body as {
      fighter_id: string;
      action: "approve" | "reject";
    };

    if (!fighter_id || !action) {
      return NextResponse.json(
        { error: "fighter_id and action are required." },
        { status: 400 }
      );
    }

    const root = process.cwd();
    const draftsDir = path.join(root, "submissions", "drafts");
    const approvedDir = path.join(root, "submissions", "approved");

    await fs.mkdir(draftsDir, { recursive: true });
    await fs.mkdir(approvedDir, { recursive: true });

    const draftPath = path.join(draftsDir, `${fighter_id}.json`);

    let raw: string;
    try {
      raw = await fs.readFile(draftPath, "utf8");
    } catch {
      return NextResponse.json(
        { error: `Draft not found: ${draftPath}` },
        { status: 404 }
      );
    }

    const fighter = JSON.parse(raw);

    if (action === "reject") {
      fighter.status = "rejected";
      fighter.submission = {
        ...fighter.submission,
        review_notes: fighter.submission?.review_notes || "Rejected by admin."
      };

      await fs.writeFile(draftPath, JSON.stringify(fighter, null, 2), "utf8");

      return NextResponse.json({
        ok: true,
        message: `Rejected ${fighter_id}`
      });
    }

    // approve path
    fighter.status = "approved";
    fighter.submission = {
      ...fighter.submission,
      review_notes: fighter.submission?.review_notes || ""
    };

    await fs.writeFile(draftPath, JSON.stringify(fighter, null, 2), "utf8");

    const script = path.join(root, "scripts", "generate_one_fighter.py");
    const result = await runPython(script, [fighter_id]);

    if (result.code !== 0) {
      return NextResponse.json(
        {
          error: "Generator failed.",
          command_hint:
            process.platform === "win32"
              ? `py -3 "${script}" ${fighter_id}`
              : `python3 "${script}" ${fighter_id}`,
          stdout: result.stdout,
          stderr: result.stderr
        },
        { status: 500 }
      );
    }

    return NextResponse.json({
      ok: true,
      message: `Approved ${fighter_id}`,
      stdout: result.stdout
    });
  } catch (err: any) {
    return NextResponse.json(
      {
        error: "Review action failed.",
        details: err?.message || String(err)
      },
      { status: 500 }
    );
  }
}