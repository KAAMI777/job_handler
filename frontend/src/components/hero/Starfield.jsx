import { useEffect, useRef } from "react";

import styles from "./Starfield.module.css";

const STAR_COUNT = 140;
const SPEED = 0.0009;

/** Lightweight 2.5-D starfield on a single canvas. No 3D engine. */
export default function Starfield() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let w, h, dpr, raf;
    const stars = Array.from({ length: STAR_COUNT }, () => ({
      x: Math.random() * 2 - 1,
      y: Math.random() * 2 - 1,
      z: Math.random(),
    }));

    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth;
      h = canvas.clientHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener("resize", resize);

    const draw = (dt) => {
      ctx.clearRect(0, 0, w, h);
      const cx = w / 2;
      const cy = h / 2;
      for (const s of stars) {
        if (!reduce) {
          s.z -= SPEED * dt;
          if (s.z <= 0.02) {
            s.x = Math.random() * 2 - 1;
            s.y = Math.random() * 2 - 1;
            s.z = 1;
          }
        }
        const k = 0.35 / s.z;
        const px = cx + s.x * k * cx;
        const py = cy + s.y * k * cy;
        if (px < 0 || px > w || py < 0 || py > h) continue;
        const size = Math.max(0.4, (1 - s.z) * 1.8);
        const alpha = Math.min(0.7, (1 - s.z) * 0.9);
        ctx.fillStyle = `rgba(120, 240, 170, ${alpha})`;
        ctx.fillRect(px, py, size, size);
      }
    };

    let last = performance.now();
    const loop = (now) => {
      const dt = Math.min(64, now - last);
      last = now;
      draw(dt);
      raf = requestAnimationFrame(loop);
    };

    if (reduce) {
      draw(0);
    } else {
      raf = requestAnimationFrame(loop);
    }

    const onVisibility = () => {
      if (document.hidden) {
        cancelAnimationFrame(raf);
      } else if (!reduce) {
        last = performance.now();
        raf = requestAnimationFrame(loop);
      }
    };
    document.addEventListener("visibilitychange", onVisibility);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, []);

  return <canvas ref={canvasRef} className={styles.field} aria-hidden="true" />;
}
