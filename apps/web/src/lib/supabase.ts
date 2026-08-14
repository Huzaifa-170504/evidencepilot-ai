import { createClient } from "@supabase/supabase-js";

import type { Database } from "../types/database";

// These are public client identifiers, not secrets. RLS is the authorization boundary.
// Build-time variables override them for forks and alternate deployments.
const productionSupabaseUrl = "https://dsbxndbbpryisxevjjgc.supabase.co";
const productionSupabasePublishableKey = "sb_publishable_mg25sq4oLUhsSrJiczSf9A_iU0FVRGI";
const supabaseUrl =
  import.meta.env.VITE_SUPABASE_URL?.trim() ||
  (import.meta.env.PROD ? productionSupabaseUrl : "");
const supabasePublishableKey =
  import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY?.trim() ||
  (import.meta.env.PROD ? productionSupabasePublishableKey : "");

export const supabaseConfigured = Boolean(supabaseUrl && supabasePublishableKey);

export const supabase = supabaseConfigured
  ? createClient<Database>(supabaseUrl, supabasePublishableKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    })
  : null;
