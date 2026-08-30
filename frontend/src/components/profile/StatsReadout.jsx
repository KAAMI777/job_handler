import { useStats } from "@/hooks/queries";

import styles from "./profile.module.css";

const PARTS = [
  { key: "jobs_this_week", label: "roles/7d" },
  { key: "high_score_jobs", label: "high-score" },
  { key: "total_relevant_jobs", label: "open" },
  { key: "active_companies", label: "companies" },
];

export default function StatsReadout() {
  const { data } = useStats();
  return (
    <code className={styles.readout} aria-label="summary">
      <span className={styles.readoutDollar}>$</span> stat
      {PARTS.map((p) => (
        <span key={p.key} className={styles.readoutPart}>
          {" "}
          --{p.label}=<b data-numeric>{data?.[p.key] ?? "…"}</b>
        </span>
      ))}
    </code>
  );
}
