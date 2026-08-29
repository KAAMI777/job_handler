import { useState } from "react";

import { useToast } from "@/components/ui/toast-context.js";
import Button from "@/components/ui/Button.jsx";
import EmptyState from "@/components/ui/EmptyState.jsx";
import Field from "@/components/ui/Field.jsx";
import Skeleton from "@/components/ui/Skeleton.jsx";
import Tag from "@/components/ui/Tag.jsx";
import {
  useAddCompany,
  useCompanies,
  useDeleteCompany,
  useResolveAts,
  useSetCompanyActive,
} from "@/hooks/queries";
import { relativeTime } from "@/lib/time";

import styles from "./profile.module.css";

const PARSER_TYPES = [
  "greenhouse",
  "lever",
  "ashby",
  "workday",
  "smartrecruiters",
  "amazon",
  "netflix",
];

function AddCompanyForm() {
  const [url, setUrl] = useState("");
  const [name, setName] = useState("");
  const [resolved, setResolved] = useState(null);
  const [manualParser, setManualParser] = useState("");
  const [error, setError] = useState("");
  const resolveAts = useResolveAts();
  const addCompany = useAddCompany();
  const toast = useToast();

  const reset = () => {
    setUrl("");
    setName("");
    setResolved(null);
    setManualParser("");
    setError("");
  };

  const preview = async () => {
    setError("");
    setResolved(null);
    try {
      const r = await resolveAts.mutateAsync(url);
      setResolved(r);
    } catch {
      setError("Could not detect the ATS. Pick the type below and paste the board URL.");
    }
  };

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    const payload = { name: name.trim(), career_url: url.trim() };
    if (!resolved && manualParser) payload.parser_type = manualParser;
    try {
      await addCompany.mutateAsync(payload);
      toast.push(`${payload.name} added`, { tone: "ok" });
      reset();
    } catch (err) {
      setError(
        err?.status === 409
          ? "That board is already tracked."
          : err?.body?.detail || "Could not add that company.",
      );
    }
  };

  return (
    <form className={styles.addForm} onSubmit={submit}>
      <Field
        label="careers link"
        placeholder="https://www.figma.com/careers/"
        value={url}
        onChange={(e) => {
          setUrl(e.target.value);
          setResolved(null);
        }}
        required
        inputMode="url"
      />
      <div className={styles.addRow}>
        <Field
          label="display name"
          placeholder="Figma"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <Button type="button" onClick={preview} loading={resolveAts.isPending} disabled={!url}>
          detect ats
        </Button>
      </div>

      {resolved && (
        <p className={styles.resolved}>
          detected <Tag tone="accent">{resolved.parser_type}</Tag> ·{" "}
          <span className={styles.resolvedUrl}>{resolved.career_url}</span>
        </p>
      )}
      {!resolved && (
        <Field
          as="select"
          label="ats type — set only if detection fails"
          value={manualParser}
          onChange={(e) => setManualParser(e.target.value)}
        >
          <option value="">auto-detect</option>
          {PARSER_TYPES.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </Field>
      )}

      {error && <p className={styles.formError}>! {error}</p>}

      <Button
        type="submit"
        variant="primary"
        loading={addCompany.isPending}
        disabled={!url.trim() || !name.trim()}
      >
        add company
      </Button>
    </form>
  );
}

export default function CompaniesPanel() {
  const { data: companies, isLoading } = useCompanies();
  const setActive = useSetCompanyActive();
  const del = useDeleteCompany();
  const toast = useToast();

  const remove = async (c) => {
    if (!window.confirm(`Remove ${c.name} and its scraped roles?`)) return;
    await del.mutateAsync(c.id);
    toast.push(`${c.name} removed`);
  };

  return (
    <div className={styles.stack}>
      <AddCompanyForm />

      <div className={styles.divider} />

      {isLoading && <Skeleton lines={4} h="2.2em" />}
      {!isLoading && companies?.length === 0 && (
        <EmptyState command="companies --list" hint="Add a company above to start the graph." />
      )}
      <ul className={styles.companyList}>
        {companies?.map((c) => (
          <li key={c.id} className={styles.companyItem} data-inactive={!c.active || undefined}>
            <div className={styles.companyInfo}>
              <span className={styles.companyName}>{c.name}</span>
              <span className={styles.companyMeta}>
                <Tag>{c.parser_type}</Tag>
                {c.last_scraped_at ? (
                  <span
                    className={styles.health}
                    data-bad={c.consecutive_failures > 0 || undefined}
                  >
                    {c.consecutive_failures > 0
                      ? `${c.consecutive_failures} failed`
                      : `ok · ${relativeTime(c.last_scraped_at)}`}
                  </span>
                ) : (
                  <span className={styles.health}>not scanned yet</span>
                )}
              </span>
            </div>
            <div className={styles.companyActions}>
              <button
                type="button"
                className={styles.linkBtn}
                onClick={() => setActive.mutate({ id: c.id, active: !c.active })}
              >
                {c.active ? "disable" : "enable"}
              </button>
              <button
                type="button"
                className={`${styles.linkBtn} ${styles.danger}`}
                onClick={() => remove(c)}
              >
                remove
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
