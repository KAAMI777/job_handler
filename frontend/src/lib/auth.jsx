import { useCallback, useEffect, useMemo, useState } from "react";

import { api } from "./api";
import { authClient, authConfigured } from "./auth-client";
import { AuthContext } from "./auth-context.js";

function usernameFor(user) {
  return (
    user?.user_metadata?.username ||
    user?.email?.split("@")[0] ||
    "guest"
  );
}

/**
 * Tracks the Supabase session and exposes register / sign-in / sign-out helpers.
 *
 * Register and login go through our own API (`/api/v1/auth/*`), which wraps Supabase so
 * the username is stored on the account. The returned tokens are then installed as the
 * Supabase session here, so refresh and persistence keep working via @supabase/auth-js.
 *
 * When Supabase is not configured (`authConfigured` is false) the app runs open:
 * `authRequired` is false, `loading` is false, and there is never a gate.
 */
export function AuthProvider({ children }) {
  // undefined = still resolving the initial session; null = signed out.
  const [session, setSession] = useState(authConfigured ? undefined : null);

  useEffect(() => {
    if (!authConfigured) return undefined;

    authClient.getSession().then(({ data }) => setSession(data.session ?? null));
    const { data: sub } = authClient.onAuthStateChange((_event, next) => {
      setSession(next ?? null);
    });
    return () => sub.subscription.unsubscribe();
  }, []);

  // Turn an /api/v1/auth/* response into a live Supabase session.
  const install = useCallback(async (result) => {
    if (!result?.access_token) return { confirmationRequired: true };
    const { error } = await authClient.setSession({
      access_token: result.access_token,
      refresh_token: result.refresh_token,
    });
    if (error) throw error;
    return { confirmationRequired: false };
  }, []);

  const value = useMemo(() => {
    const user = session?.user ?? null;
    return {
      authRequired: authConfigured,
      loading: session === undefined,
      session: session ?? null,
      user,
      username: usernameFor(user),
      register: async ({ username, email, password }) =>
        install(await api.register({ username, email, password })),
      signIn: async ({ email, password }) => install(await api.login({ email, password })),
      signOut: () => authClient.signOut(),
    };
  }, [session, install]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
