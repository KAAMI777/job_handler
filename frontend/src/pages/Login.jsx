import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import AuthShell from "@/components/auth/AuthShell.jsx";
import Button from "@/components/ui/Button.jsx";
import Field from "@/components/ui/Field.jsx";
import { useAuth } from "@/lib/auth-context.js";

import styles from "./auth.module.css";

export default function Login() {
  const { authRequired, loading, session, signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname ?? "/graph";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  // Auth off, or already signed in — nothing to do here.
  if (!authRequired || (!loading && session)) {
    return <Navigate to={from} replace />;
  }

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await signIn({ email, password });
      navigate(from, { replace: true });
    } catch (err) {
      setError(err?.body?.detail ?? err?.message ?? "sign-in failed");
      setBusy(false);
    }
  }

  return (
    <AuthShell
      title="sign in"
      footer={
        <>
          no account? <Link to="/register">create one →</Link>
        </>
      }
    >
      <form className={styles.form} onSubmit={onSubmit}>
        <Field
          label="email"
          type="email"
          name="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <Field
          label="password"
          type="password"
          name="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <p className={styles.error}>! {error}</p>}

        <Button type="submit" variant="primary" loading={busy} className={styles.submit}>
          sign in
        </Button>
      </form>
    </AuthShell>
  );
}
