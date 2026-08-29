import { NavLink, Outlet } from "react-router-dom";

import { useHealth } from "@/hooks/queries";

import styles from "./Layout.module.css";

function ConnectionDot() {
  const { data, isError, isLoading } = useHealth();
  const state = isLoading ? "wait" : isError || data?.database !== "connected" ? "down" : "up";
  const label = { wait: "connecting", down: "backend offline", up: "connected" }[state];
  return (
    <span className={styles.conn} data-state={state} title={label}>
      <span className={styles.dot} aria-hidden="true" />
      <span className={styles.connLabel}>{label}</span>
    </span>
  );
}

/** Shared shell for /graph and /profile. Hero renders without it. */
export default function Layout({ transparentBar = false }) {
  return (
    <div className={styles.shell} data-transparent={transparentBar || undefined}>
      <header className={styles.bar}>
        <NavLink to="/" className={styles.brand}>
          <span className={styles.prompt}>{">"}</span>job_agent
        </NavLink>
        <nav className={styles.nav}>
          <NavLink to="/graph" className={({ isActive }) => (isActive ? styles.active : "")}>
            graph
          </NavLink>
          <NavLink to="/profile" className={({ isActive }) => (isActive ? styles.active : "")}>
            profile
          </NavLink>
        </nav>
        <ConnectionDot />
      </header>
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}
