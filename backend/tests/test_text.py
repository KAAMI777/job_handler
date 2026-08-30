from app.scrapers.types import JobPosting
from app.utils.text import clean_description


def test_strips_html_and_collapses_whitespace():
    assert clean_description("<p>Hello   <b>world</b></p>\n\n") == "Hello world"


def test_none_and_empty():
    assert clean_description(None) is None
    assert clean_description("   <br/> ") is None


def test_truncates_long_text():
    out = clean_description("x " * 2000, max_len=50)
    assert out is not None and len(out) <= 51 and out.endswith("…")


def test_job_posting_trims_description_on_construction():
    posting = JobPosting(
        source="x",
        title="Engineer",
        apply_url="https://x.com/1",
        description="<div>Big <span>role</span></div>" + "y" * 5000,
    )
    assert posting.description is not None
    assert "<" not in posting.description
    assert len(posting.description) <= 1501
