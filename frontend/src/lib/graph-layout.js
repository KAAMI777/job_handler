/* Deterministic radial layout for the discovery graph.
 *
 * JOBS (center) -> FAMILY nodes on concentric rings -> up to 8 company nodes
 * orbiting each family. Positions are recomputed from this formula on every
 * load; a drag only mutates React Flow's local state and is never persisted.
 */

export const FAMILY_CAPACITY = 8;

const RING_0_RADIUS = 360;
const RING_GAP = 340;
const RING_0_FAMILIES = 6; // families that fit on the innermost ring
const RING_FAMILY_GROWTH = 3; // extra family slots per outer ring
const COMPANY_ORBIT = 200;
const FAN_ARC = Math.PI * 0.62; // spread of a family's members, fanned outward

const TAU = Math.PI * 2;

export function chunkFamilies(companies) {
  const families = [];
  for (let i = 0; i < companies.length; i += FAMILY_CAPACITY) {
    families.push(companies.slice(i, i + FAMILY_CAPACITY));
  }
  return families.length ? families : [[]];
}

function ringFor(familyIndex) {
  let ring = 0;
  let placed = 0;
  for (;;) {
    const capacity = RING_0_FAMILIES + ring * RING_FAMILY_GROWTH;
    if (familyIndex < placed + capacity) {
      return { ring, slot: familyIndex - placed, capacity };
    }
    placed += capacity;
    ring += 1;
  }
}

/** @param {{id:number,name:string}[]} companies - sorted oldest-first (stable) */
export function computeLayout(companies) {
  const families = chunkFamilies(companies);
  const nodes = [
    { id: "jobs", type: "jobs", position: { x: 0, y: 0 }, data: { count: companies.length }, draggable: true },
  ];
  const edges = [];

  families.forEach((members, familyIndex) => {
    const { ring, slot, capacity } = ringFor(familyIndex);
    const radius = RING_0_RADIUS + ring * RING_GAP;
    // Offset every other ring by half a slot so families don't line up radially.
    const angle = (slot / capacity) * TAU + (ring % 2 ? Math.PI / capacity : 0);
    const fx = Math.cos(angle) * radius;
    const fy = Math.sin(angle) * radius;
    const familyId = `family-${familyIndex}`;

    nodes.push({
      id: familyId,
      type: "family",
      position: { x: fx, y: fy },
      data: { index: familyIndex, count: members.length, isFull: members.length === FAMILY_CAPACITY },
      draggable: true,
    });
    edges.push({ id: `e-jobs-${familyId}`, source: "jobs", target: familyId, type: "glow" });

    const n = members.length;
    members.forEach((company, j) => {
      // Fan the members through an arc centred on the outward radial direction,
      // so a family reads as a cluster hanging off its ring position.
      const spread = n > 1 ? (j / (n - 1) - 0.5) * FAN_ARC : 0;
      const ca = angle + spread;
      const cx = fx + Math.cos(ca) * COMPANY_ORBIT;
      const cy = fy + Math.sin(ca) * COMPANY_ORBIT;
      const companyId = `company-${company.id}`;
      nodes.push({
        id: companyId,
        type: "company",
        position: { x: cx, y: cy },
        data: { company, familyIndex },
        draggable: true,
      });
      edges.push({
        id: `e-${familyId}-${companyId}`,
        source: familyId,
        target: companyId,
        type: "glow",
        data: { faint: true, agent: company.source_url == null && company.discovered_by === "agent" },
      });
    });
  });

  return { nodes, edges };
}
