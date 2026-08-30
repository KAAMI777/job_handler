import styles from "./Tag.module.css";

/** @param {{ tone?: "accent"|"amber"|"muted"|"danger" }} props */
export default function Tag({ tone = "muted", children, className = "", ...rest }) {
  return (
    <span className={`${styles.tag} ${styles[tone]} ${className}`} {...rest}>
      {children}
    </span>
  );
}
