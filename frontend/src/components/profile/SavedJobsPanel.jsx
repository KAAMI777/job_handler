import { useState } from "react";

import JobRow from "@/components/job/JobRow.jsx";
import EmptyState from "@/components/ui/EmptyState.jsx";
import Skeleton from "@/components/ui/Skeleton.jsx";
import { useSavedJobs, useSaveJob, useUnsaveJob } from "@/hooks/queries";

import styles from "./profile.module.css";

export default function SavedJobsPanel() {
  const [tab, setTab] = useState("saved");
  const { data, isLoading } = useSavedJobs(tab);
  const saveJob = useSaveJob();
  const unsaveJob = useUnsaveJob();

  return (
    <div className={styles.stack}>
      <div className={styles.tabs} role="tablist">
        {["saved", "applied"].map((t) => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            className={styles.tab}
            data-on={tab === t || undefined}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {isLoading && <Skeleton lines={3} h="2.4em" />}
      {!isLoading && (data ?? []).length === 0 && (
        <EmptyState
          command={`saved-jobs --status=${tab}`}
          hint={
            tab === "saved"
              ? "Star roles from the graph and they collect here."
              : "Mark roles applied from the graph or from your saved list."
          }
        />
      )}
      {(data ?? []).map((s) => (
        <JobRow
          key={s.id}
          job={s.job}
          saved={s.status}
          onSave={(next) =>
            next == null
              ? unsaveJob.mutate(s.job_id)
              : saveJob.mutate({ jobId: s.job_id, status: next })
          }
        />
      ))}
    </div>
  );
}
