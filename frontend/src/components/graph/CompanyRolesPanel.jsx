import { AnimatePresence, motion } from "framer-motion";
import { useMemo, useState } from "react";

import JobRow from "@/components/job/JobRow.jsx";
import EmptyState from "@/components/ui/EmptyState.jsx";
import Skeleton from "@/components/ui/Skeleton.jsx";
import { useJobs, useSavedJobs, useSaveJob, useUnsaveJob } from "@/hooks/queries";
import { JOB_VISIBILITY_HOURS } from "@/lib/time";

import styles from "./CompanyRolesPanel.module.css";

const EASE = [0.16, 1, 0.3, 1];

export default function CompanyRolesPanel({ company, onClose }) {
  const [sort, setSort] = useState("score");
  const { data, isLoading, isError } = useJobs({
    company_id: company?.id,
    within_hours: JOB_VISIBILITY_HOURS,
    limit: 100,
  });
  const { data: saved = [] } = useSavedJobs();
  const saveJob = useSaveJob();
  const unsaveJob = useUnsaveJob();

  const savedByJob = useMemo(
    () => Object.fromEntries(saved.map((s) => [s.job_id, s.status])),
    [saved],
  );

  const roles = useMemo(() => {
    const items = data?.items ?? [];
    return [...items].sort((a, b) =>
      sort === "score"
        ? b.score - a.score || b.first_seen_at.localeCompare(a.first_seen_at)
        : b.first_seen_at.localeCompare(a.first_seen_at),
    );
  }, [data, sort]);

  const handleSave = (jobId, next) => {
    if (next == null) unsaveJob.mutate(jobId);
    else saveJob.mutate({ jobId, status: next });
  };

  return (
    <AnimatePresence>
      {company && (
        <>
          <motion.div
            className={styles.scrim}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            onClick={onClose}
          />
          <motion.aside
            className={styles.panel}
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ duration: 0.28, ease: EASE }}
            aria-label={`Open roles at ${company.name}`}
          >
            <header className={styles.head}>
              <h2 className={styles.name}>
                <span className={styles.prompt}>{">"}</span>
                {company.name}
              </h2>
              <button type="button" className={styles.close} onClick={onClose} aria-label="Close">
                ✕
              </button>
            </header>

            <div className={styles.sub}>
              <span className={styles.window}>roles found in the last {JOB_VISIBILITY_HOURS}h</span>
              <div className={styles.sortToggle} role="group" aria-label="Sort roles">
                <button data-on={sort === "score" || undefined} onClick={() => setSort("score")}>
                  score
                </button>
                <button data-on={sort === "recent" || undefined} onClick={() => setSort("recent")}>
                  recent
                </button>
              </div>
            </div>

            <div className={styles.body}>
              {isLoading && <Skeleton lines={5} h="2.4em" />}
              {isError && (
                <p className={styles.err}>! could not load roles for {company.name}</p>
              )}
              {!isLoading && !isError && roles.length === 0 && (
                <EmptyState
                  command={`roles --company=${company.name.toLowerCase().replace(/\s+/g, "_")} --window=${JOB_VISIBILITY_HOURS}h`}
                  hint="No matching roles in the visibility window. New postings appear here after the next scan."
                />
              )}
              {roles.map((job) => (
                <JobRow
                  key={job.id}
                  job={job}
                  saved={savedByJob[job.id] ?? null}
                  onSave={(next) => handleSave(job.id, next)}
                />
              ))}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
