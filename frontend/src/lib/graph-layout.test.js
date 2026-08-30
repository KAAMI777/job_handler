import { describe, expect, it } from "vitest";

import { chunkFamilies, computeLayout, FAMILY_CAPACITY } from "./graph-layout.js";

const makeCompanies = (n) => Array.from({ length: n }, (_, i) => ({ id: i + 1, name: `co${i}` }));

describe("graph layout", () => {
  it("chunks companies into families of 8", () => {
    expect(chunkFamilies(makeCompanies(9))).toHaveLength(2);
    expect(chunkFamilies(makeCompanies(8))).toHaveLength(1);
    expect(chunkFamilies([])).toEqual([[]]);
  });

  it("adds a family node when the 9th company arrives", () => {
    const before = computeLayout(makeCompanies(8)).nodes.filter((n) => n.type === "family");
    const after = computeLayout(makeCompanies(9)).nodes.filter((n) => n.type === "family");
    expect(before).toHaveLength(1);
    expect(after).toHaveLength(2);
  });

  it("is deterministic — same input, identical positions", () => {
    const a = computeLayout(makeCompanies(20));
    const b = computeLayout(makeCompanies(20));
    expect(a.nodes.map((n) => n.position)).toEqual(b.nodes.map((n) => n.position));
  });

  it("centers JOBS and links every company through its family", () => {
    const { nodes, edges } = computeLayout(makeCompanies(FAMILY_CAPACITY + 1));
    const jobs = nodes.find((n) => n.id === "jobs");
    expect(jobs.position).toEqual({ x: 0, y: 0 });
    const companyNodes = nodes.filter((n) => n.type === "company");
    expect(companyNodes).toHaveLength(FAMILY_CAPACITY + 1);
    for (const c of companyNodes) {
      expect(edges.some((e) => e.target === c.id && e.source.startsWith("family-"))).toBe(true);
    }
  });
});
