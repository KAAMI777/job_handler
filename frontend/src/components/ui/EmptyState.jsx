import styles from "./EmptyState.module.css";

/**
 * Terminal-flavoured empty state: shows the "command" that produced no output,
 * plus a hint that teaches the next move.
 * @param {{ command: string, hint?: string, action?: React.ReactNode }} props
 */
export default function EmptyState({ command, hint, action }) {
  return (
    <div className={styles.wrap} role="status">
      <code className={styles.command}>
        <span className={styles.prompt}>$</span> {command}
      </code>
      <p className={styles.zero}>0 results</p>
      {hint && <p className={styles.hint}>{hint}</p>}
      {action && <div className={styles.action}>{action}</div>}
    </div>
  );
}
