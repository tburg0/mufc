"use client";

import { useEffect, useState } from "react";

type Submission = {
  fighter_id: string;
  status: string;
  name: string;
  creator_name: string;
  archetype: string;
  stats: Record<string, number>;
  data: any;
};

export default function AdminPage() {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [selected, setSelected] = useState<Submission | null>(null);
  const [message, setMessage] = useState("");

  async function loadSubmissions() {
    setMessage("");
    const res = await fetch("/api/admin/submissions", { cache: "no-store" });
    const data = await res.json();
    if (!res.ok) {
      setMessage(data.error || "Failed to load submissions.");
      return;
    }
    setSubmissions(data.submissions);
    if (data.submissions.length) {
      const current = selected
        ? data.submissions.find((s: Submission) => s.fighter_id === selected.fighter_id)
        : data.submissions[0];
      setSelected(current || data.submissions[0]);
    } else {
      setSelected(null);
    }
  }

  useEffect(() => {
    loadSubmissions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function review(action: "approve" | "reject") {
    if (!selected) return;
    setMessage("");

    const res = await fetch("/api/admin/review", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        fighter_id: selected.fighter_id,
        action
      })
    });

    const data = await res.json();
    if (!res.ok) {
      setMessage(data.error || "Action failed.");
      return;
    }

    setMessage(data.message || "Done.");
    await loadSubmissions();
  }

  async function publish() {
    if (!selected) return;
    setMessage("");

    const res = await fetch("/api/admin/publish", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        fighter_id: selected.fighter_id
      })
    });

    const data = await res.json();
    if (!res.ok) {
      setMessage(data.error || "Publish failed.");
      return;
    }

    setMessage(data.message || "Published.");
    await loadSubmissions();
  }

  return (
    <main style={{ padding: 24, fontFamily: "Arial, sans-serif" }}>
      <h1>MUFC Admin Review</h1>

      {message && <p>{message}</p>}

      <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 20 }}>
        <div style={{ border: "1px solid #ccc", padding: 12 }}>
          <h2>Submissions</h2>
          {submissions.length === 0 && <p>No submissions found.</p>}

          {submissions.map((s) => (
            <button
              key={s.fighter_id}
              onClick={() => setSelected(s)}
              style={{
                display: "block",
                width: "100%",
                textAlign: "left",
                marginBottom: 8,
                padding: 10,
                background: selected?.fighter_id === s.fighter_id ? "#ddd" : "#fff",
                border: "1px solid #aaa",
                cursor: "pointer"
              }}
            >
              <div><strong>{s.name}</strong></div>
              <div>{s.creator_name}</div>
              <div>{s.archetype}</div>
              <div>Status: {s.status}</div>
            </button>
          ))}
        </div>

        <div style={{ border: "1px solid #ccc", padding: 12 }}>
          <h2>Details</h2>

          {!selected && <p>Select a fighter.</p>}

          {selected && (
            <>
              <p><strong>Name:</strong> {selected.name}</p>
              <p><strong>Creator:</strong> {selected.creator_name}</p>
              <p><strong>Archetype:</strong> {selected.archetype}</p>
              <p><strong>Status:</strong> {selected.status}</p>

              <h3>Stats</h3>
              <ul>
                {Object.entries(selected.stats || {}).map(([k, v]) => (
                  <li key={k}>{k}: {String(v)}</li>
                ))}
              </ul>

              <h3>Full JSON</h3>
              <pre style={{ background: "#111", color: "#eee", padding: 12, overflow: "auto", maxHeight: 500 }}>
                {JSON.stringify(selected.data, null, 2)}
              </pre>

              <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                <button onClick={() => review("approve")}>Approve</button>
                <button onClick={() => review("reject")}>Reject</button>
                <button onClick={publish}>Publish</button>
              </div>
            </>
          )}
        </div>
      </div>
    </main>
  );
}