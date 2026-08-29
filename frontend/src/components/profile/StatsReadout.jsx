import Skeleton from "@/components/ui/Skeleton.jsx";
import { useStats } from "@/hooks/queries";

import styles from "./profile.module.css";

const CELLS = [
  { key: "jobs_this_week", label: "relevant roles / 7d" },
  { key: "high_score_jobs", label: "high-score open" },
  { key: "total_relevant_jobs", label: "relevant open" },
  { key: "active_companies", label: "companies active" },
];

export default function StatsReadout() {
  const { data, isLoading } = useStats();
  return (
    <div className={styles.readout} role="list">
      {CELLS.map((c) => (
        <div key={c.key} className={styles.cell} role="listitem">
          <span className={styles.cellNum} data-numeric>
            {isLoading ? <Skeleton w="2ch" h="1.2em" /> : (data?.[c.key] ?? 0)}
          </span>
          <span className={styles.cellLabel}>{c.label}</span>
        </div>
      ))}
    </div>
  );
}
