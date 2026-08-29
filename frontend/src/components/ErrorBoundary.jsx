import { Component } from "react";

import styles from "./ErrorBoundary.module.css";

export default class ErrorBoundary extends Component {
  state = { error: null };

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("Unhandled UI error:", error, info);
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className={styles.wrap} role="alert">
        <pre className={styles.frame}>
          <span className={styles.sig}>SIGSEGV</span> the interface crashed{"\n"}
          {String(this.state.error?.message ?? this.state.error)}
        </pre>
        <button className={styles.reload} onClick={() => window.location.reload()}>
          › reload
        </button>
      </div>
    );
  }
}
