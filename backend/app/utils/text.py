import re

_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")

DESCRIPTION_MAX_LEN = 1500


def clean_description(raw: str | None, *, max_len: int = DESCRIPTION_MAX_LEN) -> str | None:
    """Strip HTML tags, collapse whitespace, and truncate.

    Job descriptions from ATS APIs are often large HTML blobs; we only keep a short
    plain-text preview to bound DB and memory use (the matcher scores on the title).
    """
    if not raw:
        return None
    text = _WS.sub(" ", _TAG.sub(" ", raw)).strip()
    if not text:
        return None
    if len(text) > max_len:
        text = text[:max_len].rstrip() + "…"
    return text
