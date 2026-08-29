import { useMemo, useState } from "react";

import Button from "@/components/ui/Button.jsx";
import Field from "@/components/ui/Field.jsx";
import Skeleton from "@/components/ui/Skeleton.jsx";
import {
  useAddKeywordRule,
  useDeleteKeywordRule,
  useKeywordRules,
  useUpdateKeywordRule,
} from "@/hooks/queries";

import styles from "./profile.module.css";

export default function KeywordRulesPanel() {
  const { data: rules, isLoading } = useKeywordRules();
  const add = useAddKeywordRule();
  const update = useUpdateKeywordRule();
  const del = useDeleteKeywordRule();

  const [role, setRole] = useState("");
  const [keyword, setKeyword] = useState("");
  const [weight, setWeight] = useState(1);
  const [error, setError] = useState("");

  const grouped = useMemo(() => {
    const map = new Map();
    for (const r of rules ?? []) {
      if (!map.has(r.role)) map.set(r.role, []);
      map.get(r.role).push(r);
    }
    return [...map.entries()];
  }, [rules]);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await add.mutateAsync({ role: role.trim(), keyword: keyword.trim(), weight: Number(weight) });
      setKeyword("");
    } catch (err) {
      setError(err?.status === 409 ? "That role/keyword pair already exists." : "Could not add.");
    }
  };

  return (
    <div className={styles.stack}>
      <p className={styles.note}>
        the matcher scores a role title by these keywords · changes apply on the next scan
      </p>

      <form className={styles.ruleForm} onSubmit={submit}>
        <Field
          label="role"
          placeholder="backend"
          value={role}
          onChange={(e) => setRole(e.target.value)}
          list="rule-roles"
          required
        />
        <datalist id="rule-roles">
          {grouped.map(([r]) => (
            <option key={r} value={r} />
          ))}
        </datalist>
        <Field
          label="keyword"
          placeholder="django"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          required
        />
        <Field
          label="weight"
          type="number"
          min={1}
          max={100}
          value={weight}
          onChange={(e) => setWeight(e.target.value)}
        />
        <Button type="submit" loading={add.isPending} disabled={!role.trim() || !keyword.trim()}>
          add rule
        </Button>
      </form>
      {error && <p className={styles.formError}>! {error}</p>}

      {isLoading && <Skeleton lines={5} h="1.8em" />}
      <div className={styles.ruleGroups}>
        {grouped.map(([r, items]) => (
          <div key={r} className={styles.ruleGroup}>
            <span className={styles.ruleRole}>{r}</span>
            <ul className={styles.ruleChips}>
              {items.map((rule) => (
                <li
                  key={rule.id}
                  className={styles.ruleChip}
                  data-off={!rule.is_active || undefined}
                >
                  <button
                    type="button"
                    className={styles.ruleToggle}
                    onClick={() => update.mutate({ id: rule.id, is_active: !rule.is_active })}
                    title={rule.is_active ? "disable" : "enable"}
                  >
                    {rule.keyword}
                    <span className={styles.ruleWeight}>×{rule.weight}</span>
                  </button>
                  <button
                    type="button"
                    className={styles.ruleDelete}
                    onClick={() => del.mutate(rule.id)}
                    aria-label={`delete ${rule.keyword}`}
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
