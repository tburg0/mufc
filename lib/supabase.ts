import { createClient } from "@supabase/supabase-js";

function getEnv(name: string) {
  const value = process.env[name];
  return typeof value === "string" && value.trim() ? value : undefined;
}

export function getSupabaseClient() {
  const supabaseUrl = getEnv("NEXT_PUBLIC_SUPABASE_URL") ?? getEnv("SUPABASE_URL");
  const supabaseKey =
    getEnv("SUPABASE_SERVICE_ROLE_KEY") ?? getEnv("NEXT_PUBLIC_SUPABASE_ANON_KEY");

  if (!supabaseUrl) {
    throw new Error("Supabase URL is missing. Set NEXT_PUBLIC_SUPABASE_URL or SUPABASE_URL.");
  }

  if (!supabaseKey) {
    throw new Error(
      "Supabase key is missing. Set SUPABASE_SERVICE_ROLE_KEY or NEXT_PUBLIC_SUPABASE_ANON_KEY."
    );
  }

  return createClient(supabaseUrl, supabaseKey);
}
