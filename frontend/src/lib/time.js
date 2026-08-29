// Job visibility window from the brief: a role shows for 48h from when it was found.
export const JOB_VISIBILITY_HOURS = 48;

export function hoursAgo(iso) {
  return (Date.now() - new Date(iso).getTime()) / 3_600_000;
}

export function isWithinWindow(iso, hours = JOB_VISIBILITY_HOURS) {
  return hoursAgo(iso) <= hours;
}

export function relativeTime(iso) {
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60_000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.round(hrs / 24);
  return `${days}d ago`;
}
