from app.utils.hashing import job_hash


def _base(**overrides):
    kwargs = {
        "company_id": 1,
        "external_id": None,
        "title": "Senior Backend Engineer",
        "location": "Bengaluru, India",
        "apply_url": "https://jobs.example.com/123",
    }
    kwargs.update(overrides)
    return job_hash(**kwargs)


def test_hash_is_deterministic():
    assert _base() == _base()


def test_hash_ignores_trivial_formatting():
    assert _base(title="  senior   BACKEND engineer ") == _base()


def test_hash_changes_with_meaningful_fields():
    assert _base(title="Frontend Engineer") != _base()
    assert _base(company_id=2) != _base()


def test_external_id_takes_precedence():
    with_id = _base(external_id="req-42")
    # Title/location no longer affect the hash once an external id is present.
    assert with_id == _base(external_id="req-42", title="Anything", location="Anywhere")
    assert with_id != _base()
