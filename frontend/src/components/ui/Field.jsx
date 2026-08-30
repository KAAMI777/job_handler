import { useId } from "react";

import styles from "./Field.module.css";

/**
 * @param {{ label: string, error?: string, hint?: string, as?: "input"|"select" }} props
 */
export default function Field({
  label,
  error,
  hint,
  as = "input",
  className = "",
  children,
  ...rest
}) {
  const id = useId();
  const Control = as;
  return (
    <label className={`${styles.field} ${className}`} htmlFor={id}>
      <span className={styles.label}>{label}</span>
      <Control
        id={id}
        className={styles.control}
        data-invalid={error ? "" : undefined}
        aria-invalid={error ? "true" : undefined}
        aria-describedby={error ? `${id}-err` : undefined}
        {...rest}
      >
        {children}
      </Control>
      {error ? (
        <span id={`${id}-err`} className={styles.error}>
          ! {error}
        </span>
      ) : hint ? (
        <span className={styles.hint}>{hint}</span>
      ) : null}
    </label>
  );
}
