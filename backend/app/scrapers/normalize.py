from app.models.enums import EmploymentType

_EMPLOYMENT_ALIASES: dict[str, EmploymentType] = {
    "full-time": EmploymentType.FULL_TIME,
    "full time": EmploymentType.FULL_TIME,
    "fulltime": EmploymentType.FULL_TIME,
    "permanent": EmploymentType.FULL_TIME,
    "regular": EmploymentType.FULL_TIME,
    "part-time": EmploymentType.PART_TIME,
    "part time": EmploymentType.PART_TIME,
    "parttime": EmploymentType.PART_TIME,
    "contract": EmploymentType.CONTRACT,
    "contractor": EmploymentType.CONTRACT,
    "temporary": EmploymentType.CONTRACT,
    "fixed-term": EmploymentType.CONTRACT,
    "intern": EmploymentType.INTERNSHIP,
    "internship": EmploymentType.INTERNSHIP,
    "trainee": EmploymentType.INTERNSHIP,
    "co-op": EmploymentType.INTERNSHIP,
}


def normalize_employment_type(raw: str | None) -> EmploymentType | None:
    """Map an ATS's free-text commitment/type string to an EmploymentType.

    Returns ``None`` when nothing is provided, ``OTHER`` when the value is present
    but unrecognized.
    """
    if not raw:
        return None
    key = raw.strip().lower().replace("_", "-")
    if key in _EMPLOYMENT_ALIASES:
        return _EMPLOYMENT_ALIASES[key]
    key_spaced = key.replace("-", " ")
    return _EMPLOYMENT_ALIASES.get(key_spaced, EmploymentType.OTHER)
