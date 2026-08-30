import { driver } from "driver.js";
import "driver.js/dist/driver.css";

const SEEN_KEY = "job_agent.tour.seen.v1";

function read(key) {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* private mode */
  }
}

export function hasSeenTour() {
  return read(SEEN_KEY) === "1";
}

const STEPS = [
  {
    element: '.react-flow__node[data-id="jobs"]',
    popover: {
      title: "your watchlist",
      description:
        "Every company you track connects out from this node — plus any the agent finds on its own.",
    },
  },
  {
    element: ".react-flow__node-company",
    popover: {
      title: "a company",
      description:
        "The badge counts its software roles found in the last 48h. Click a node to open the roles panel.",
    },
  },
  {
    element: '[data-tour="status"]',
    popover: {
      title: "families",
      description:
        "Companies group into families of 8. When one fills up, a new family ring appears automatically.",
    },
  },
  {
    element: '[data-tour="profile-link"]',
    popover: {
      title: "set it up",
      description:
        "Add companies, tune the matching keywords, and turn on email alerts from your profile.",
      side: "bottom",
      align: "end",
    },
  },
];

export function createTour() {
  return driver({
    showProgress: true,
    allowClose: true,
    overlayColor: "rgba(3, 6, 9, 0.72)",
    stagePadding: 6,
    stageRadius: 6,
    popoverClass: "ja-tour",
    nextBtnText: "next ›",
    prevBtnText: "‹ back",
    doneBtnText: "done",
    steps: STEPS,
    onDestroyed: () => write(SEEN_KEY, "1"),
  });
}

/** Run once on first visit when the graph actually has nodes. */
export function maybeStartTour() {
  if (hasSeenTour()) return;
  if (!document.querySelector(".react-flow__node-company")) return;
  createTour().drive();
}
