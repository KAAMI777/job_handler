import styles from "./Panel.module.css";

/**
 * A terminal-window section.
 * @param {{ title: string, hint?: string, actions?: React.ReactNode }} props
 */
export default function Panel({ title, hint, actions, children, className = "" }) {
  return (
    <section className={`${styles.panel} ${className}`}>
      <header className={styles.head}>
        <span className={styles.dots} aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
        <h2 className={styles.title}>{title}</h2>
        {hint && <span className={styles.hint}>{hint}</span>}
        {actions && <div className={styles.actions}>{actions}</div>}
      </header>
      <div className={styles.body}>{children}</div>
    </section>
  );
}
