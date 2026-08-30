import { motion } from "framer-motion";

import CompaniesPanel from "@/components/profile/CompaniesPanel.jsx";
import FieldSelector from "@/components/profile/FieldSelector.jsx";
import KeywordRulesPanel from "@/components/profile/KeywordRulesPanel.jsx";
import NotifyPanel from "@/components/profile/NotifyPanel.jsx";
import RunLogPanel from "@/components/profile/RunLogPanel.jsx";
import SavedJobsPanel from "@/components/profile/SavedJobsPanel.jsx";
import StatsReadout from "@/components/profile/StatsReadout.jsx";
import Panel from "@/components/ui/Panel.jsx";
import { useAuth } from "@/lib/auth-context.js";

import styles from "./Profile.module.css";

export default function Profile() {
  const { username } = useAuth();
  return (
    <motion.div
      className={styles.page}
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
    >
      <header className={styles.top}>
        <div className={styles.identity}>
          <p className={styles.greeting}>
            <span className={styles.host}>guest@site</span>
            <span className={styles.punc}>:</span>
            <span className={styles.path}>~</span>
            <span className={styles.punc}>$</span> hi{" "}
            <span className={styles.name}>{username}</span>
            <span className={`${styles.caret} cursor-blink`} aria-hidden="true" />
          </p>
          <h1 className={styles.h1}>
            <span className={styles.prompt}>{">"}</span> profile
          </h1>
        </div>
        <StatsReadout />
      </header>

      <div className={styles.grid}>
        <div className={styles.col}>
          <Panel title="tracked companies">
            <CompaniesPanel />
          </Panel>
          <Panel title="field">
            <FieldSelector />
          </Panel>
          <Panel title="saved & applied">
            <SavedJobsPanel />
          </Panel>
        </div>

        <div className={styles.col}>
          <Panel title="tag preferences">
            <KeywordRulesPanel />
          </Panel>
          <Panel title="agent runs">
            <RunLogPanel />
          </Panel>
          <Panel title="notifications">
            <NotifyPanel />
          </Panel>
        </div>
      </div>
    </motion.div>
  );
}
