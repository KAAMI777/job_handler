import { Handle, Position } from "@xyflow/react";

import styles from "./nodes.module.css";

const hidden = { opacity: 0, pointerEvents: "none" };

/** data: { company, roleCount, pulse, selected } */
export default function CompanyNode({ data, selected }) {
  const { company, roleCount = 0, pulse } = data;
  return (
    <button
      type="button"
      className={styles.node + " " + styles.company}
      data-selected={selected || undefined}
      data-pulse={pulse || undefined}
      data-has-roles={roleCount > 0 || undefined}
      aria-label={`${company.name}, ${roleCount} open role${roleCount === 1 ? "" : "s"}`}
    >
      <Handle type="target" position={Position.Top} style={hidden} isConnectable={false} />
      <span className={styles.companyDot} aria-hidden="true" />
      <span className={styles.companyName}>{company.name}</span>
      {roleCount > 0 && <span className={styles.companyBadge}>{roleCount}</span>}
      <Handle type="source" position={Position.Bottom} style={hidden} isConnectable={false} />
    </button>
  );
}
