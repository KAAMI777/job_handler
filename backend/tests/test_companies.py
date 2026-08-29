from app.models.enums import ParserType
from app.services import company_service
from app.services.ats_resolver import ResolvedAts
from tests.conftest import requires_db

pytestmark = requires_db

VALID = {
    "name": "Acme",
    "career_url": "https://boards.greenhouse.io/acme",
    "parser_type": "greenhouse",
}


def test_create_and_get_company(api_client):
    created = api_client.post("/api/v1/companies", json=VALID)
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "Acme"
    assert body["active"] is True
    assert body["consecutive_failures"] == 0

    fetched = api_client.get(f"/api/v1/companies/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == body["id"]


def test_duplicate_career_url_is_rejected(api_client):
    assert api_client.post("/api/v1/companies", json=VALID).status_code == 201
    dup = api_client.post("/api/v1/companies", json={**VALID, "name": "Acme 2"})
    assert dup.status_code == 409


def test_list_and_active_filter(api_client):
    api_client.post("/api/v1/companies", json=VALID)
    api_client.post(
        "/api/v1/companies",
        json={**VALID, "career_url": "https://jobs.lever.co/beta", "parser_type": "lever"},
    )
    assert len(api_client.get("/api/v1/companies").json()) == 2

    second = api_client.get("/api/v1/companies").json()[1]
    api_client.post(f"/api/v1/companies/{second['id']}/disable")

    active = api_client.get("/api/v1/companies", params={"active_only": True}).json()
    assert len(active) == 1
    assert active[0]["active"] is True


def test_update_url_and_conflict(api_client):
    a = api_client.post("/api/v1/companies", json=VALID).json()
    b = api_client.post(
        "/api/v1/companies",
        json={**VALID, "career_url": "https://jobs.lever.co/beta", "parser_type": "lever"},
    ).json()

    ok = api_client.patch(
        f"/api/v1/companies/{a['id']}", json={"career_url": "https://boards.greenhouse.io/acme-new"}
    )
    assert ok.status_code == 200
    assert ok.json()["career_url"].rstrip("/") == "https://boards.greenhouse.io/acme-new"

    clash = api_client.patch(
        f"/api/v1/companies/{a['id']}", json={"career_url": b["career_url"]}
    )
    assert clash.status_code == 409


def test_create_auto_detects_parser_type(api_client, monkeypatch):
    monkeypatch.setattr(
        company_service.ats_resolver,
        "resolve",
        lambda url: ResolvedAts(ParserType.GREENHOUSE, "https://boards.greenhouse.io/figma"),
    )
    created = api_client.post(
        "/api/v1/companies",
        json={"name": "Figma", "career_url": "https://www.figma.com/careers/"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["parser_type"] == "greenhouse"
    assert body["career_url"] == "https://boards.greenhouse.io/figma"
    assert body["source_url"] == "https://www.figma.com/careers/"


def test_create_422_when_ats_not_detected(api_client, monkeypatch):
    monkeypatch.setattr(company_service.ats_resolver, "resolve", lambda url: None)
    resp = api_client.post(
        "/api/v1/companies",
        json={"name": "Mystery", "career_url": "https://mystery.example/jobs"},
    )
    assert resp.status_code == 422


def test_resolve_endpoint(api_client, monkeypatch):
    from app.api.v1 import companies as companies_api

    monkeypatch.setattr(
        companies_api.ats_resolver,
        "resolve",
        lambda url: ResolvedAts(ParserType.ASHBY, "https://jobs.ashbyhq.com/notion"),
    )
    resp = api_client.post(
        "/api/v1/companies/resolve", json={"url": "https://www.notion.so/careers"}
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "parser_type": "ashby",
        "career_url": "https://jobs.ashbyhq.com/notion",
    }


def test_missing_company_is_404(api_client):
    assert api_client.get("/api/v1/companies/999").status_code == 404
    assert api_client.patch("/api/v1/companies/999", json={"name": "x"}).status_code == 404
    assert api_client.post("/api/v1/companies/999/disable").status_code == 404
    assert api_client.delete("/api/v1/companies/999").status_code == 404


def test_delete_company_removes_it(api_client):
    created = api_client.post("/api/v1/companies", json=VALID).json()
    assert api_client.delete(f"/api/v1/companies/{created['id']}").status_code == 204
    assert api_client.get(f"/api/v1/companies/{created['id']}").status_code == 404
