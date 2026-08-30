// Auth client. We only use Supabase for authentication, so this pulls in
// @supabase/auth-js directly rather than the full supabase-js SDK (which would also
// bundle the realtime / postgrest / storage clients we never touch).
//
// Auth is opt-in: with the env vars absent (local dev, or before auth is switched on)
// `authClient` is null and `authConfigured` is false, and the app runs open — mirroring
// the backend's AUTH_ENABLED flag.
import { AuthClient } from "@supabase/auth-js";

const url = import.meta.env.VITE_SUPABASE_URL;
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const authConfigured = Boolean(url && anonKey);

export const authClient = authConfigured
  ? new AuthClient({
      url: `${url.replace(/\/+$/, "")}/auth/v1`,
      headers: { apikey: anonKey, Authorization: `Bearer ${anonKey}` },
      storageKey: "sb-job-agent-auth-token",
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true,
    })
  : null;
