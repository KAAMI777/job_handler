import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { JOB_VISIBILITY_HOURS } from "@/lib/time";

const keys = {
  health: ["health"],
  companies: ["companies"],
  jobs: (params) => ["jobs", params],
  stats: ["stats"],
  runs: ["scrape-runs"],
  rules: ["keyword-rules"],
  saved: (status) => ["saved-jobs", status ?? "all"],
  settings: ["settings"],
};

export function useHealth() {
  return useQuery({ queryKey: keys.health, queryFn: api.health, refetchInterval: 30_000, retry: false });
}

export function useCompanies() {
  return useQuery({ queryKey: keys.companies, queryFn: api.listCompanies });
}

export function useJobs(params = {}) {
  const merged = { within_hours: JOB_VISIBILITY_HOURS, limit: 200, ...params };
  return useQuery({ queryKey: keys.jobs(merged), queryFn: () => api.listJobs(merged) });
}

export function useStats() {
  return useQuery({ queryKey: keys.stats, queryFn: api.stats });
}

export function useScrapeRuns(limit = 10) {
  return useQuery({ queryKey: [...keys.runs, limit], queryFn: () => api.listScrapeRuns(limit) });
}

export function useKeywordRules() {
  return useQuery({ queryKey: keys.rules, queryFn: api.listKeywordRules });
}

export function useSavedJobs(status) {
  return useQuery({ queryKey: keys.saved(status), queryFn: () => api.listSavedJobs(status) });
}

export function useSettings() {
  return useQuery({ queryKey: keys.settings, queryFn: api.getSettings });
}

/* ---------- mutations ---------- */

function useInvalidating(fn, invalidate) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: fn,
    onSuccess: () => invalidate.forEach((k) => qc.invalidateQueries({ queryKey: k })),
  });
}

export function useResolveAts() {
  return useMutation({ mutationFn: api.resolveAts });
}

export function useAddCompany() {
  return useInvalidating(api.createCompany, [keys.companies, keys.stats]);
}

export function useSetCompanyActive() {
  return useInvalidating(
    ({ id, active }) => api.setCompanyActive(id, active),
    [keys.companies, keys.stats],
  );
}

export function useDeleteCompany() {
  return useInvalidating(api.deleteCompany, [keys.companies, keys.stats, ["jobs"]]);
}

export function useStartScrape() {
  return useInvalidating(api.startScrape, [keys.runs]);
}

export function useAddKeywordRule() {
  return useInvalidating(api.createKeywordRule, [keys.rules]);
}

export function useUpdateKeywordRule() {
  return useInvalidating(({ id, ...patch }) => api.updateKeywordRule(id, patch), [keys.rules]);
}

export function useDeleteKeywordRule() {
  return useInvalidating(api.deleteKeywordRule, [keys.rules]);
}

export function useSaveJob() {
  return useInvalidating(({ jobId, status }) => api.saveJob(jobId, status), [["saved-jobs"]]);
}

export function useUnsaveJob() {
  return useInvalidating(api.unsaveJob, [["saved-jobs"]]);
}

export function useUpdateSettings() {
  return useInvalidating(api.updateSettings, [keys.settings]);
}
