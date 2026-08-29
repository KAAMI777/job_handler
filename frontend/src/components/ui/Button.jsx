import styles from "./Button.module.css";

/**
 * @param {{ variant?: "primary"|"ghost"|"danger", size?: "sm"|"md",
 *           loading?: boolean, as?: any }} props
 */
export default function Button({
  variant = "ghost",
  size = "md",
  loading = false,
  disabled,
  className = "",
  children,
  as: Tag = "button",
  ...rest
}) {
  const isButton = Tag === "button";
  return (
    <Tag
      className={`${styles.btn} ${styles[variant]} ${styles[size]} ${className}`}
      disabled={isButton ? disabled || loading : undefined}
      aria-busy={loading || undefined}
      data-loading={loading || undefined}
      {...rest}
    >
      <span className={styles.mark} aria-hidden="true">
        {loading ? "…" : "›"}
      </span>
      {children}
    </Tag>
  );
}
