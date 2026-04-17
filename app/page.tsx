import Link from "next/link";

export default function HomePage() {
  return (
    <main className="landing-shell">
      <section className="landing-hero">
        <div className="landing-card">
          <div className="landing-kicker">MUFC League Tools</div>
          <h1 className="landing-title">Creator-first fighters for a nonstop AI wrestling stream.</h1>
          <p className="landing-lede">
            Build fighters for singles, tag, title matches, and tournament storylines, then push them into the live roster pipeline.
          </p>
          <div className="landing-actions">
            <Link className="landing-button primary" href="/create">Open Fighter Builder</Link>
          </div>
        </div>
        <div className="landing-card">
          <div className="builder-kicker">What Changed</div>
          <div className="builder-summary-list">
            <div><span>Primary Model</span><strong>Modular fighter assembly</strong></div>
            <div><span>Legacy Support</span><strong>Optional roster-based fallback</strong></div>
            <div><span>Goal</span><strong>Make created fighters feel authored, not cloned</strong></div>
          </div>
        </div>
      </section>
    </main>
  );
}
