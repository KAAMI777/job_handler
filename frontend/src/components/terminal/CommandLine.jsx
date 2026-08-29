import styles from "./CommandLine.module.css";

/**
 * A shell command line used for loading / status.
 * @param {{ command: string, running?: boolean, exit?: number|null }} props
 */
export default function CommandLine({ command, running = false, exit = null }) {
  return (
    <code className={styles.line} data-running={running || undefined}>
      <span className={styles.dollar}>$</span>
      <span className={styles.cmd}>{command}</span>
      {running && <span className={styles.dots} aria-hidden="true" />}
      {exit != null && (
        <span className={styles.exit} data-ok={exit === 0 || undefined}>
          exit {exit}
        </span>
      )}
    </code>
  );
}
