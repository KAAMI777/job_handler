import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import AuthShell from "@/components/auth/AuthShell.jsx";
import Button from "@/components/ui/Button.jsx";
import Field from "@/components/ui/Field.jsx";
import { useToast } from "@/components/ui/toast-context.js";
import { useAuth } from "@/lib/auth-context.js";

import styles from "./auth.module.css";

export default function Register() {
  const { authRequired, loading, session, register } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  if (!authRequired || (!loading && session)) {
    return <Navigate to="/graph" replace />;
  }

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const { confirmationRequired } = await register({ username, email, password });
      if (confirmationRequired) {
        toast.push("account created — check your inbox to confirm", { tone: "ok" });
        navigate("/login", { replace: true });
      } else {
        navigate("/graph", { replace: true });
      }
    } catch (err) {
      setError(err?.body?.detail ?? err?.message ?? "could not create account");
      setBusy(false);
    }
  }

  return (
    <AuthShell
      title="create account"
      footer={
        <>
          already have an account? <Link to="/login">sign in →</Link>
        </>
      }
    >
      <form className={styles.form} onSubmit={onSubmit}>
        <Field
          label="username"
          name="username"
          autoComplete="username"
          required
          minLength={3}
          maxLength={32}
          pattern="[A-Za-z0-9._\-]+"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
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
          autoComplete="new-password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          hint="at least 8 characters"
        />

        {error && <p className={styles.error}>! {error}</p>}

        <Button type="submit" variant="primary" loading={busy} className={styles.submit}>
          create account
        </Button>
      </form>
    </AuthShell>
  );
}
