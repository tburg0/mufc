import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

async function readJsonFiles(dir: string) {
  await fs.mkdir(dir, { recursive: true });
  const files = await fs.readdir(dir);
  const jsonFiles = files.filter((f) => f.endsWith(".json"));

  const items = await Promise.all(
    jsonFiles.map(async (file) => {
      const full = path.join(dir, file);
      const raw = await fs.readFile(full, "utf8");
      const data = JSON.parse(raw);

      return {
        fighter_id: data.fighter_id,
        status: data.status,
        name: data.identity?.name ?? "",
        creator_name: data.identity?.creator_name ?? "",
        archetype: data.build?.archetype ?? "",
        stats: data.build?.stats ?? {},
        path: full,
        data
      };
    })
  );

  return items;
}

export async function GET() {
  try {
    const root = process.cwd();
    const draftsDir = path.join(root, "submissions", "drafts");
    const approvedDir = path.join(root, "submissions", "approved");

    const drafts = await readJsonFiles(draftsDir);
    const approved = await readJsonFiles(approvedDir);

    const mergedMap = new Map<string, any>();

    for (const item of [...drafts, ...approved]) {
      mergedMap.set(item.fighter_id, item);
    }

    const submissions = Array.from(mergedMap.values()).sort((a, b) =>
      a.name.localeCompare(b.name)
    );

    return NextResponse.json({ submissions });
  } catch (err: any) {
    return NextResponse.json(
      {
        error: "Failed to load submissions.",
        details: err?.message || String(err)
      },
      { status: 500 }
    );
  }
}