import { motion, useReducedMotion } from "framer-motion";

import styles from "./BootSequence.module.css";

const LINES = [
  { k: "cmd", text: "./job_agent --init" },
  { k: "ok", text: "mounting company watchlist" },
  { k: "ok", text: "resolving ATS adapters   greenhouse · lever · ashby · workday · +3" },
  { k: "ok", text: "scheduler online   scan interval = 6h" },
  { k: "run", text: "auto-discovery   tracked + newly found companies" },
  { k: "ready", text: "job_agent ready." },
];

const TAG = {
  ok: "[ ok ]",
  run: "[ .. ]",
  cmd: "$",
  ready: "»",
};

export default function BootSequence({ onDone }) {
  const reduce = useReducedMotion();

  return (
    <motion.div
      className={styles.boot}
      initial={reduce ? false : "hidden"}
      animate="show"
      onAnimationComplete={onDone}
      variants={{ show: { transition: { staggerChildren: reduce ? 0 : 0.16 } } }}
    >
      {LINES.map((line, i) => (
        <motion.p
          key={i}
          className={styles.line}
          data-kind={line.k}
          variants={{
            hidden: { opacity: 0, x: -6 },
            show: { opacity: 1, x: 0, transition: { duration: 0.18 } },
          }}
        >
          <span className={styles.tag}>{TAG[line.k]}</span>
          <span className={styles.text}>{line.text}</span>
        </motion.p>
      ))}
    </motion.div>
  );
}
