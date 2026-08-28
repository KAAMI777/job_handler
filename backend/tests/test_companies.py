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


def test_missing_company_is_404(api_client):
    assert api_client.get("/api/v1/companies/999").status_code == 404
    assert api_client.patch("/api/v1/companies/999", json={"name": "x"}).status_code == 404
    assert api_client.post("/api/v1/companies/999/disable").status_code == 404
