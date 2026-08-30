import { useState } from "react";

import { useToast } from "@/components/ui/toast-context.js";
import Button from "@/components/ui/Button.jsx";
import CommandLine from "@/components/terminal/CommandLine.jsx";
import Skeleton from "@/components/ui/Skeleton.jsx";
import { useScrapeRuns, useStartScrape } from "@/hooks/queries";
import { api } from "@/lib/api";
import { relativeTime } from "@/lib/time";

import styles from "./profile.module.css";

const RUNNING = new Set(["running"]);

export default function RunLogPanel() {
  const { data: runs, isLoading, refetch } = useScrapeRuns(8);
  const startScrape = useStartScrape();
  const toast = useToast();
  const [polling, setPolling] = useState(false);

  const active = runs?.find((r) => RUNNING.has(r.status));

  const run = async () => {
    try {
      const { run_id } = await startScrape.mutateAsync();
      toast.push("scan started", { tone: "ok" });
      setPolling(true);
      // Poll the run to completion, then refresh the log.
      const tick = async () => {
        const r = await api.getScrapeRun(run_id);
        if (RUNNING.has(r.status)) {
          setTimeout(tick, 4000);
        } else {
          setPolling(false);
          refetch();
          toast.push(`scan ${r.status} · +${r.new_jobs} roles`, {
            tone: r.status === "failed" ? "error" : "ok",
          });
        }
      };
      setTimeout(tick, 4000);
    } catch (err) {
      setPolling(false);
      toast.push(
        err?.status === 409 ? "a scan is already running" : "could not start a scan",
        { tone: "error" },
      );
    }
  };

  return (
    <div className={styles.stack}>
      <div className={styles.runHead}>
        <CommandLine
          command="scan_companies.sh --last=6h"
          running={polling || Boolean(active)}
        />
        <Button
          size="sm"
          variant="primary"
          onClick={run}
          loading={startScrape.isPending || polling}
          disabled={Boolean(active)}
        >
          run scan now
        </Button>
      </div>

      {isLoading && <Skeleton lines={4} h="1.6em" />}
      <ol className={styles.runList}>
        {runs?.map((r) => (
          <li key={r.id} className={styles.runItem} data-status={r.status}>
            <span className={styles.runWhen}>{relativeTime(r.started_at)}</span>
            <span className={styles.runStatus}>{r.status}</span>
            <span className={styles.runCounts}>
              {r.companies_checked} checked · +{r.new_jobs} roles
              {r.failed > 0 && <span className={styles.runFail}> · {r.failed} failed</span>}
            </span>
            {r.duration_seconds != null && (
              <span className={styles.runDur}>{r.duration_seconds}s</span>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
