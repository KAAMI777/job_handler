import { ReactFlowProvider } from "@xyflow/react";
import { motion } from "framer-motion";
import { useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";

import CompanyRolesPanel from "@/components/graph/CompanyRolesPanel.jsx";
import GraphCanvas from "@/components/graph/GraphCanvas.jsx";
import styles from "@/components/graph/graph.module.css";
import CommandLine from "@/components/terminal/CommandLine.jsx";
import Button from "@/components/ui/Button.jsx";
import EmptyState from "@/components/ui/EmptyState.jsx";
import { useCompanies, useJobs } from "@/hooks/queries";
import { hoursAgo, JOB_VISIBILITY_HOURS } from "@/lib/time";

const PULSE_HOURS = 8;

export default function Graph() {
  const companiesQ = useCompanies();
  const companies = useMemo(
    () => [...(companiesQ.data ?? [])].sort((a, b) => a.id - b.id),
    [companiesQ.data],
  );

  const jobsQ = useJobs({ within_hours: JOB_VISIBILITY_HOURS, limit: 200 });

  const { roleCountByCompany, pulseIds } = useMemo(() => {
    const counts = {};
    const pulse = new Set();
    for (const job of jobsQ.data?.items ?? []) {
      counts[job.company_id] = (counts[job.company_id] ?? 0) + 1;
      if (hoursAgo(job.first_seen_at) <= PULSE_HOURS) pulse.add(job.company_id);
    }
    return { roleCountByCompany: counts, pulseIds: pulse };
  }, [jobsQ.data]);

  const [selectedId, setSelectedId] = useState(null);
  const selectedCompany = companies.find((c) => c.id === selectedId) ?? null;
  const resetRef = useRef(null);

  const loading = companiesQ.isLoading;
  const empty = !loading && companies.length === 0;

  return (
    <motion.div
      className={styles.canvas}
      style={{ position: "absolute" }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
    >
      {loading && (
        <div className={styles.center}>
          <CommandLine command="scan_companies.sh --last=6h" running />
        </div>
      )}

      {empty && (
        <div className={styles.center}>
          <EmptyState
            command="render_graph --companies"
            hint="No companies tracked yet. Add one from your profile and the graph builds itself."
            action={
              <Button as={Link} to="/profile" variant="primary">
                add companies
              </Button>
            }
          />
        </div>
      )}

      {!loading && !empty && (
        <>
          <div className={styles.toolbar}>
            <span className={styles.status}>
              <span className={styles.statusPrompt}>$</span>
              {companies.length} companies · {jobsQ.data?.total ?? 0} roles in {JOB_VISIBILITY_HOURS}h
            </span>
            <Button size="sm" onClick={() => resetRef.current?.reset()}>
              reset layout
            </Button>
          </div>

          <ReactFlowProvider>
            <GraphCanvas
              companies={companies}
              roleCountByCompany={roleCountByCompany}
              pulseIds={pulseIds}
              selectedId={selectedId}
              onSelectCompany={setSelectedId}
              resetRef={resetRef}
            />
          </ReactFlowProvider>
        </>
      )}

      <CompanyRolesPanel company={selectedCompany} onClose={() => setSelectedId(null)} />
    </motion.div>
  );
}
