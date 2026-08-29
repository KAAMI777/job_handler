import { Handle, Position } from "@xyflow/react";

import styles from "./nodes.module.css";

const hidden = { opacity: 0, pointerEvents: "none" };

export default function JobsNode({ data }) {
  return (
    <div className={`${styles.node} ${styles.jobs}`}>
      <Handle type="target" position={Position.Top} style={hidden} isConnectable={false} />
      <span className={styles.jobsMark}>◈</span>
      <span className={styles.jobsLabel}>JOBS</span>
      <span className={styles.jobsMeta}>{data.count} tracked</span>
      <Handle type="source" position={Position.Bottom} style={hidden} isConnectable={false} />
    </div>
  );
}
