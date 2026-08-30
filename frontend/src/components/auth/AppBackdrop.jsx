import styles from "./AppBackdrop.module.css";

// A non-interactive, blurred facsimile of the profile dashboard. It sits behind the auth
// cards so signing in reads as an overlay on the app rather than a separate blank screen.
// Deliberately static markup — no data, no queries, nothing to fail.
const COLUMNS = [
  [
    { title: "tracked companies", rows: 5 },
    { title: "field", rows: 2 },
    { title: "saved & applied", rows: 4 },
  ],
  [
    { title: "tag preferences", rows: 6 },
    { title: "agent runs", rows: 3 },
    { title: "notifications", rows: 3 },
  ],
];

function FakePanel({ title, rows }) {
  return (
    <div className={styles.panel}>
      <div className={styles.panelHead}>
        <span className={styles.dots}>
          <i />
          <i />
          <i />
        </span>
        <span className={styles.panelTitle}>{title}</span>
      </div>
      <div className={styles.panelBody}>
        {Array.from({ length: rows }, (_, i) => (
          <span
            key={i}
            className={styles.row}
            style={{ width: `${92 - ((i * 53) % 46)}%` }}
          />
        ))}
      </div>
    </div>
  );
}

export default function AppBackdrop() {
  return (
    <div className={styles.backdrop} aria-hidden="true">
      <div className={styles.app}>
        <div className={styles.bar}>
          <span className={styles.brand}>&gt;job_agent</span>
          <span className={styles.navItem}>graph</span>
          <span className={styles.navItem}>profile</span>
          <span className={styles.dot} />
        </div>
        <div className={styles.page}>
          <div className={styles.readout}>
            $ stat --roles/7d=24 --high-score=6 --open=41 --companies=12
          </div>
          <div className={styles.grid}>
            {COLUMNS.map((col, i) => (
              <div className={styles.col} key={i}>
                {col.map((p) => (
                  <FakePanel key={p.title} {...p} />
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className={styles.veil} />
    </div>
  );
}
