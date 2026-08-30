import "@xyflow/react/dist/style.css";

import {
  Background,
  BackgroundVariant,
  Controls,
  ReactFlow,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from "@xyflow/react";
import { useCallback, useEffect, useImperativeHandle, useMemo } from "react";

import { computeLayout } from "@/lib/graph-layout";

import GlowEdge from "./GlowEdge.jsx";
import styles from "./graph.module.css";
import CompanyNode from "./nodes/CompanyNode.jsx";
import FamilyNode from "./nodes/FamilyNode.jsx";
import JobsNode from "./nodes/JobsNode.jsx";

const nodeTypes = { jobs: JobsNode, family: FamilyNode, company: CompanyNode };
const edgeTypes = { glow: GlowEdge };

const idSignature = (companies) =>
  companies
    .map((c) => c.id)
    .sort((a, b) => a - b)
    .join(",");

/**
 * @param {{
 *   companies: any[], roleCountByCompany: Record<number, number>,
 *   pulseIds: Set<number>, selectedId: number|null,
 *   onSelectCompany: (id: number|null) => void, resetRef: React.Ref
 * }} props
 */
export default function GraphCanvas({
  companies,
  roleCountByCompany,
  pulseIds,
  selectedId,
  onSelectCompany,
  resetRef,
}) {
  const layout = useMemo(() => computeLayout(companies), [companies]);
  const [nodes, setNodes, onNodesChange] = useNodesState(layout.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layout.edges);
  const { fitView } = useReactFlow();

  const signature = idSignature(companies);

  // Re-seed positions + edges from the deterministic formula whenever the set of
  // companies changes (and on every mount / refresh). Drags are never persisted.
  useEffect(() => {
    const next = computeLayout(companies);
    setNodes(next.nodes);
    setEdges(next.edges);
    const t = setTimeout(() => fitView({ duration: 300, padding: 0.2 }), 60);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [signature]);

  useImperativeHandle(resetRef, () => ({
    reset: () => {
      setNodes(computeLayout(companies).nodes);
      fitView({ duration: 300, padding: 0.18 });
    },
  }));

  // Inject live data (role counts, pulse, selection) without touching positions.
  const decorated = useMemo(
    () =>
      nodes.map((n) => {
        if (n.type === "jobs") return { ...n, data: { count: companies.length } };
        if (n.type !== "company") return n;
        const id = n.data.company.id;
        return {
          ...n,
          selected: id === selectedId,
          data: {
            ...n.data,
            roleCount: roleCountByCompany[id] ?? 0,
            pulse: pulseIds.has(id),
          },
        };
      }),
    [nodes, companies.length, roleCountByCompany, pulseIds, selectedId],
  );

  const handleNodeClick = useCallback(
    (_evt, node) => {
      if (node.type === "company") onSelectCompany(node.data.company.id);
      else onSelectCompany(null);
    },
    [onSelectCompany],
  );

  return (
    <ReactFlow
      className={styles.canvas}
      nodes={decorated}
      edges={edges}
      nodeTypes={nodeTypes}
      edgeTypes={edgeTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={handleNodeClick}
      onPaneClick={() => onSelectCompany(null)}
      nodesConnectable={false}
      nodesFocusable
      minZoom={0.2}
      maxZoom={1.8}
      proOptions={{ hideAttribution: true }}
      fitView
      fitViewOptions={{ padding: 0.18 }}
    >
      <Background variant={BackgroundVariant.Dots} gap={26} size={1} />
      <Controls showInteractive={false} position="bottom-right" />
    </ReactFlow>
  );
}
