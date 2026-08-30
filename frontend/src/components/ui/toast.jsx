import { AnimatePresence, motion } from "framer-motion";
import { useCallback, useMemo, useState } from "react";

import { ToastContext } from "./toast-context.js";
import styles from "./toast.module.css";

let seq = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const dismiss = useCallback((id) => {
    setToasts((t) => t.filter((x) => x.id !== id));
  }, []);

  const push = useCallback(
    (message, { tone = "info", ttl = 4200 } = {}) => {
      const id = ++seq;
      setToasts((t) => [...t, { id, message, tone }]);
      if (ttl) setTimeout(() => dismiss(id), ttl);
    },
    [dismiss],
  );

  const value = useMemo(() => ({ push, dismiss }), [push, dismiss]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className={styles.stack} role="region" aria-label="Notifications">
        <AnimatePresence initial={false}>
          {toasts.map((t) => (
            <motion.output
              key={t.id}
              className={`${styles.toast} ${styles[t.tone]}`}
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 24 }}
              transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
              onClick={() => dismiss(t.id)}
            >
              <span className={styles.mark}>
                {t.tone === "error" ? "✗" : t.tone === "ok" ? "✓" : "»"}
              </span>
              {t.message}
            </motion.output>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}
