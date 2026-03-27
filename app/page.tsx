import Link from "next/link";

export default function HomePage() {
  return (
    <main style={{ padding: 24, fontFamily: "Arial, sans-serif" }}>
      <h1>MUFC Fighter Builder</h1>
      <p>Create a fighter draft for your AI fight league.</p>
      <Link href="/create">Create Fighter</Link>
    </main>
  );
}