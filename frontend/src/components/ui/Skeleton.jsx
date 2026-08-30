import styles from "./Skeleton.module.css";

/** @param {{ w?: string, h?: string, lines?: number }} props */
export default function Skeleton({ w = "100%", h = "1em", lines = 1, className = "" }) {
  if (lines > 1) {
    return (
      <div className={`${styles.stack} ${className}`}>
        {Array.from({ length: lines }, (_, i) => (
          <span
            key={i}
            className={styles.bar}
            style={{ width: i === lines - 1 ? "62%" : w, height: h }}
          />
        ))}
      </div>
    );
  }
  return <span className={`${styles.bar} ${className}`} style={{ width: w, height: h }} />;
}
