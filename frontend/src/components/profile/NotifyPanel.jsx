import { useState } from "react";

import { useToast } from "@/components/ui/toast-context.js";
import Button from "@/components/ui/Button.jsx";
import Field from "@/components/ui/Field.jsx";
import Skeleton from "@/components/ui/Skeleton.jsx";
import { useSettings, useUpdateSettings } from "@/hooks/queries";

import styles from "./profile.module.css";

function NotifyForm({ initial }) {
  const update = useUpdateSettings();
  const toast = useToast();

  const [email, setEmail] = useState(initial.notify_email ?? "");
  const [minScore, setMinScore] = useState(initial.notify_min_score ?? 0);
  const [highOnly, setHighOnly] = useState((initial.notify_min_score ?? 0) >= 40);

  const save = async (e) => {
    e.preventDefault();
    await update.mutateAsync({
      notify_email: email.trim() || null,
      notify_min_score: highOnly ? Math.max(minScore, 40) : minScore,
    });
    toast.push("notification settings saved", { tone: "ok" });
  };

  return (
    <form className={styles.stack} onSubmit={save}>
      <p className={styles.note}>
        after each scan, an email digest of the new relevant roles (grouped by company)
      </p>
      <Field
        label="digest email"
        type="email"
        placeholder="you@example.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <label className={styles.check}>
        <input
          type="checkbox"
          checked={highOnly}
          onChange={(e) => {
            setHighOnly(e.target.checked);
            if (e.target.checked) setMinScore((s) => Math.max(s, 40));
          }}
        />
        high-score matches only (score ≥ 40)
      </label>

      {!highOnly && (
        <Field
          label={`minimum score — ${minScore}`}
          type="range"
          min={0}
          max={100}
          step={5}
          value={minScore}
          onChange={(e) => setMinScore(Number(e.target.value))}
        />
      )}

      <Button type="submit" variant="primary" loading={update.isPending}>
        save
      </Button>
    </form>
  );
}

export default function NotifyPanel() {
  const { data, isLoading } = useSettings();
  if (isLoading || !data) return <Skeleton lines={3} h="2.2em" />;
  return <NotifyForm initial={data} />;
}
