"""Best-effort country detection from an ATS location string.

Deliberately small and rule-based: the aggregator only needs to tell "India / remote
in India or Asia" apart from everything else. Unknown strings return ``None`` and are
treated as non-India by the matcher (still stored, just not marked relevant).
"""

import re

_INDIA_CITIES = {
    "bengaluru",
    "bangalore",
    "mumbai",
    "pune",
    "hyderabad",
    "chennai",
    "delhi",
    "new delhi",
    "gurgaon",
    "gurugram",
    "noida",
    "kolkata",
    "ahmedabad",
    "jaipur",
    "kochi",
    "cochin",
    "thiruvananthapuram",
    "trivandrum",
    "chandigarh",
    "indore",
    "coimbatore",
}

_REMOTE = re.compile(r"\bremote\b", re.IGNORECASE)
_ASIA_HINT = re.compile(r"\b(india|asia|apac|ind)\b", re.IGNORECASE)


def detect_country(location: str | None) -> str | None:
    """Return ``"India"`` for Indian locations (incl. remote-in-India/Asia), else a
    coarse label or ``None`` when undeterminable."""
    if not location:
        return None

    text = location.strip().lower()
    if "india" in text:
        return "India"
    if any(re.search(rf"\b{re.escape(city)}\b", text) for city in _INDIA_CITIES):
        return "India"
    if _REMOTE.search(location) and _ASIA_HINT.search(location):
        return "India"

    if _REMOTE.search(location):
        return "Remote"
    return None


def is_india(location: str | None) -> bool:
    return detect_country(location) == "India"
