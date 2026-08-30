import {
  motion,
  useMotionValue,
  useReducedMotion,
  useSpring,
  useTransform,
} from "framer-motion";

import AppBackdrop from "./AppBackdrop.jsx";
import styles from "./AuthShell.module.css";

/**
 * Frosted-glass auth card floating over a blurred view of the app.
 * Shared by the login and register pages.
 *
 * @param {{ title: string, children: React.ReactNode, footer?: React.ReactNode }} props
 */
export default function AuthShell({ title, children, footer }) {
  const reduce = useReducedMotion();

  // Pointer position within the card, -0.5 … 0.5 on each axis.
  const px = useMotionValue(0);
  const py = useMotionValue(0);
  const rotateX = useSpring(useTransform(py, [-0.5, 0.5], [5.5, -5.5]), {
    stiffness: 140,
    damping: 18,
  });
  const rotateY = useSpring(useTransform(px, [-0.5, 0.5], [-7, 7]), {
    stiffness: 140,
    damping: 18,
  });

  function handleMove(event) {
    if (reduce) return;
    const rect = event.currentTarget.getBoundingClientRect();
    px.set((event.clientX - rect.left) / rect.width - 0.5);
    py.set((event.clientY - rect.top) / rect.height - 0.5);
  }
  function reset() {
    px.set(0);
    py.set(0);
  }

  return (
    <main className={styles.wrap}>
      <AppBackdrop />
      <motion.div
        className={styles.tilt}
        onMouseMove={handleMove}
        onMouseLeave={reset}
        style={reduce ? undefined : { rotateX, rotateY }}
        initial={{ opacity: 0, y: 16, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.42, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className={styles.card}>
          <div className={styles.sheen} aria-hidden="true" />
          <div className={styles.edge} aria-hidden="true" />
          <header className={styles.head}>
            <span className={styles.prompt}>{">"}</span>
            <span className={styles.title}>{title}</span>
          </header>
          <div className={styles.content}>{children}</div>
          {footer && <div className={styles.footer}>{footer}</div>}
        </div>
      </motion.div>
    </main>
  );
}
