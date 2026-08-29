import { BaseEdge, getStraightPath } from "@xyflow/react";

import styles from "./graph.module.css";

/** Straight fibre-optic line, brighter for JOBS→family, faint for family→company. */
export default function GlowEdge({ id, sourceX, sourceY, targetX, targetY, data }) {
  const [path] = getStraightPath({ sourceX, sourceY, targetX, targetY });
  const cls = [styles.edge, data?.faint ? styles.edgeFaint : "", data?.agent ? styles.edgeAgent : ""]
    .filter(Boolean)
    .join(" ");
  return <BaseEdge id={id} path={path} className={cls} />;
}
