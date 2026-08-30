import styles from "./profile.module.css";

const FIELDS = [
  { id: "software_engineering", label: "software engineering", active: true },
  { id: "finance", label: "finance", active: false },
  { id: "commerce", label: "commerce", active: false },
  { id: "arts", label: "arts", active: false },
  { id: "medical", label: "medical", active: false },
];

export default function FieldSelector() {
  return (
    <div className={styles.fields} role="radiogroup" aria-label="Job field">
      {FIELDS.map((f) => (
        <button
          key={f.id}
          type="button"
          role="radio"
          aria-checked={f.active}
          disabled={!f.active}
          className={styles.fieldChip}
          data-active={f.active || undefined}
        >
          {f.label}
          {!f.active && <span className={styles.soon}>// soon</span>}
        </button>
      ))}
    </div>
  );
}
