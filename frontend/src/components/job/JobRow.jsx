import Tag from "@/components/ui/Tag.jsx";
import { relativeTime } from "@/lib/time";

import styles from "./JobRow.module.css";

/**
 * @param {{ job: any, saved?: "saved"|"applied"|null,
 *           onSave?: (status: "saved"|"applied"|null) => void }} props
 */
export default function JobRow({ job, saved = null, onSave }) {
  return (
    <article className={styles.row}>
      <div className={styles.main}>
        <div className={styles.headline}>
          <span className={styles.score} data-numeric title={`relevance score ${job.score}`}>
            {String(job.score).padStart(2, "0")}
          </span>
          <h4 className={styles.title}>{job.title}</h4>
        </div>
        <div className={styles.meta}>
          {job.location && <span>{job.location}</span>}
          <span className={styles.sep}>·</span>
          <span>found {relativeTime(job.first_seen_at)}</span>
        </div>
        {job.matched_roles?.length > 0 && (
          <div className={styles.tags}>
            {job.matched_roles.map((r) => (
              <Tag key={r} tone="accent">
                {r}
              </Tag>
            ))}
          </div>
        )}
      </div>

      <div className={styles.actions}>
        {onSave && (
          <div className={styles.saveGroup} role="group" aria-label="Track this job">
            <button
              type="button"
              className={styles.saveBtn}
              data-on={saved === "saved" || undefined}
              onClick={() => onSave(saved === "saved" ? null : "saved")}
            >
              {saved === "saved" ? "★ saved" : "☆ save"}
            </button>
            <button
              type="button"
              className={styles.saveBtn}
              data-on={saved === "applied" || undefined}
              onClick={() => onSave(saved === "applied" ? null : "applied")}
            >
              {saved === "applied" ? "✓ applied" : "applied?"}
            </button>
          </div>
        )}
        <a
          className={styles.apply}
          href={job.apply_url}
          target="_blank"
          rel="noopener noreferrer"
        >
          › apply
        </a>
      </div>
    </article>
  );
}
