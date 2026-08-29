import { Handle, Position } from "@xyflow/react";

import styles from "./nodes.module.css";

const hidden = { opacity: 0, pointerEvents: "none" };

export default function FamilyNode({ data }) {
  return (
    <div className={`${styles.node} ${styles.family}`} data-full={data.isFull || undefined}>
      <Handle type="target" position={Position.Top} style={hidden} isConnectable={false} />
      <span className={styles.familyName}>fam.{String(data.index).padStart(2, "0")}</span>
      <span className={styles.familyCount}>
        {data.count}/8
      </span>
      <Handle type="source" position={Position.Bottom} style={hidden} isConnectable={false} />
    </div>
  );
}
