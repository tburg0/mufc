import { NextRequest, NextResponse } from "next/server";
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
    const { fighter_id } = body as { fighter_id: string };

    if (!fighter_id) {
      return NextResponse.json(
        { error: "fighter_id is required." },
        { status: 400 }
      );
    }

    const root = process.cwd();
    const script = path.join(root, "scripts", "publish_fighter.py");

    const result = await runPython(script, [fighter_id]);

    if (result.code !== 0) {
      return NextResponse.json(
        {
          error: "Publish failed.",
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
      message: `Published ${fighter_id}`,
      stdout: result.stdout
    });
  } catch (err: any) {
    return NextResponse.json(
      {
        error: "Publish action failed.",
        details: err?.message || String(err)
      },
      { status: 500 }
    );
  }
}