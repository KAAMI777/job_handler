import { motion, useReducedMotion } from "framer-motion";
import { useState } from "react";
import { Link } from "react-router-dom";

import Starfield from "@/components/hero/Starfield.jsx";
import BootSequence from "@/components/terminal/BootSequence.jsx";

import styles from "./Hero.module.css";

export default function Hero() {
  const reduce = useReducedMotion();
  const [booted, setBooted] = useState(reduce);

  return (
    <motion.main
      className={styles.hero}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
    >
      <Starfield />

      <div className={styles.frame}>
        <header className={styles.brand}>
          <span className={styles.mark}>◈</span>
          <span className={styles.name}>job_agent</span>
        </header>

        <BootSequence onDone={() => setBooted(true)} />

        <motion.p
          className={styles.blurb}
          initial={reduce ? false : { opacity: 0, y: 6 }}
          animate={booted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
        >
          A job-discovery graph. It watches the companies you pick — and the ones it finds on
          its own — pulls every open software role in India, scores each against your keywords,
          and drops the new matches into your inbox every 6&nbsp;hours.
        </motion.p>

        <motion.div
          className={styles.cta}
          initial={reduce ? false : { opacity: 0 }}
          animate={booted ? { opacity: 1 } : {}}
          transition={{ duration: 0.3, delay: reduce ? 0 : 0.15 }}
        >
          <Link to="/graph" className={styles.enter}>
            <span className={styles.prompt}>{">"}</span> enter_graph
            <span className="cursor-blink" aria-hidden="true" />
          </Link>
          <Link to="/profile" className={styles.secondary}>
            or set up your watchlist →
          </Link>
        </motion.div>
      </div>
    </motion.main>
  );
}
