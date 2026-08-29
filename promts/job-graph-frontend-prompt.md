# Frontend Build Prompt — Job Discovery Graph App

## 1. Project Summary
Build a frontend for an AI job-discovery tool. The core experience is an interactive **node graph**: a central "JOBS" node connects outward to companies (user-supplied links plus companies an agent discovers autonomously every 6 hours). Clicking a company node reveals the open roles found for it. The app has three pages: a Hero/landing page, the Main graph page, and a Profile Dashboard.

---

## 2. Tech Stack Decision

**Use React Flow (xyflow).** Reasoning:
- Purpose-built for node/edge graphs with pan, zoom, drag, and custom node components out of the box — far less boilerplate than hand-rolling with raw SVG or D3.
- Supports fully custom node renderers, so an "expandable company node" (Razorpay-style pop-open) is a first-class pattern, not a hack.
- Positions are controlled state you own — this directly supports the "resets to original spot on refresh" requirement (see §4).
- Has a large ecosystem (minimap, controls, background grids) that fits the "cool/dynamic" visual goal with little extra work.

*Alternative considered:* D3.js gives more low-level control but means building drag/zoom/hit-testing yourself — not worth it for this use case. Cytoscape.js is good for graph algorithms (shortest path, clustering) which isn't the priority here. **Decision: React Flow.**

---

## 3. Graph Structure & Scaling Rule

```
JOBS (center)
 ├── FAMILY1 (ring 1) → up to 8 company nodes
 ├── FAMILY2 (ring 1) → next 8 company nodes
 ├── FAMILY3 (ring 1) → next 8 company nodes
 └── ... new FAMILY node added automatically every time a family fills up to 8
```

**Layout: fully circular / radial, not linear or zigzag.** Reasoning:
- Radial layout scales indefinitely by just adding another ring — no re-flow of existing nodes needed.
- Keeps visual symmetry and avoids overlap as companies grow into the hundreds.
- Reads naturally as a "network/constellation," which supports the dark, dynamic aesthetic.

**Placement algorithm:**
- FAMILY nodes are placed evenly around JOBS on a fixed-radius circle: `angle = (index / totalFamilies) * 360°`.
- Each FAMILY's up-to-8 company nodes are placed evenly on their own fixed-radius circle around *that* family node (same angle formula, radius = family-orbit-radius).
- Positions are **deterministic and recomputed from this formula on every load** — never persisted from a drag. So: user can drag any node around during a session for exploration, but on refresh everything snaps back to its computed circular position. Store only *data* (which node exists, its family, its job list) in the backend/local state — never store `x, y` from a drag.

---

## 4. Node Interaction Behavior

- **Company node click** → expands in place (or in a side panel) to show that company's open roles.
- **Job visibility rule:** each job stays visible for **48 hours** from when it was found, then is removed from the list — no exceptions. High-score jobs can still be *sorted* to the top while they're within the 48-hour window, but they are not pinned past expiry.
- Expansion/collapse should animate (subtle) rather than hard-cut, to keep the "dynamic" feel.

---

## 5. Pages

1. **Hero Page** — project name, one-paragraph description of what the tool does (auto-discovers jobs from tracked + newly found companies every 6 hours), a "cool" terminal-style intro animation (see theme), and a CTA into the main app.
2. **Main Page** — the graph itself, as specified above.
3. **Profile Dashboard** — recommended contents:
   - Tracked companies list (the links the user manually provided) with add/remove.
   - Field/tag preference selector (see §7).
   - Recent agent-run log ("last scan: 6h ago, found 4 new companies, 11 new roles").
   - Saved/starred jobs and applied-jobs tracker.
   - Personal stats: jobs surfaced this week, high-score jobs count, companies tracked.
   - Notification preferences (e.g., alert me only for high-score matches).

---

## 6. Visual Theme

**Dark, terminal/Linux-inspired, dynamic.**
- Monospace fonts (JetBrains Mono / Fira Code), near-black background, single accent color (terminal green or amber) for text/edges/highlights.
- Command-line flavor touches: loading states styled as `$ scanning_companies.sh --last=6h`, boot-sequence text on the Hero page, blinking cursor accents, subtle scanline/CRT texture (optional, keep subtle so it stays usable).
- Graph edges glow softly like fiber/circuit lines; node "pulse" animation when new jobs are found on it.

---

## 7. Tags / Fields (Extensibility)

- **For now:** hardcode a single field — *Software Engineering* — with its existing tag set.
- **Design for later:** add a field selector in the UI (Software Engineering active; Finance, Commerce, Arts, Medical, etc. shown as selectable but "coming soon" or visually disabled) so the data model already has a `field` attribute per company/job even though only one field's tags are populated in the backend today.

---

## 8. Animation, Aesthetics & Performance

- Build this to be **visually aesthetic and dynamic** — not a static graph. Use motion to make the app feel alive (node pulse on new job found, smooth expand/collapse on click, ambient background movement).
- Add **3D animation** where it enhances the experience (e.g. a subtle 3D tilt/depth on nodes or a 3D particle/starfield backdrop on the Hero page) — but keep it as a light visual layer, not a full 3D scene graph, so it stays performant.
- **Keep the bundle light enough for Vercel** — avoid heavy 3D engines/large dependency chains; prefer lightweight approaches (CSS 3D transforms, a small canvas/WebGL effect, or a minimal Three.js scene limited to one component) over a full always-on 3D renderer for the whole app.
- **Use the following skills for this build:**
  - `framer-motion` — for all UI motion: node expand/collapse, page transitions, hover/press micro-interactions.
  - `impeccable` — apply for overall polish/quality bar across the UI.
  - `taste-skill` — apply for aesthetic/design judgment calls (color, spacing, composition) throughout.

---

## 9. Deliverables / Acceptance Criteria
- [ ] React Flow graph renders JOBS center node, FAMILY rings, and company nodes per the radial algorithm above.
- [ ] Adding a 9th company to a full family auto-creates the next FAMILY node.
- [ ] Dragging a node is possible during a session; refresh restores computed positions.
- [ ] Clicking a company node expands its job list; all jobs expire and are removed at 48h.
- [ ] Three routed pages: Hero, Main (graph), Profile Dashboard.
- [ ] Dark/terminal theme applied consistently across all three pages.
- [ ] Field selector present with Software Engineering active, others visibly "coming soon."
- [ ] Motion (via framer-motion) applied to node expand/collapse and key transitions; a light 3D effect present (e.g. Hero backdrop or node depth) without bloating bundle size; `impeccable` and `taste-skill` applied for overall polish and aesthetic judgment.
