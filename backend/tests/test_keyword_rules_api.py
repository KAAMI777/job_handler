from tests.conftest import requires_db

pytestmark = requires_db

RULE = {"role": "backend", "keyword": "django", "weight": 3}


def test_seed_rules_are_listed(api_client):
    # The seed migration inserts a starter set.
    rules = api_client.get("/api/v1/keyword-rules").json()
    assert len(rules) >= 5
    assert {"software_engineer", "backend", "frontend"} <= {r["role"] for r in rules}


def test_create_update_delete(api_client):
    created = api_client.post("/api/v1/keyword-rules", json=RULE)
    assert created.status_code == 201
    rule_id = created.json()["id"]
    assert created.json()["weight"] == 3

    patched = api_client.patch(f"/api/v1/keyword-rules/{rule_id}", json={"is_active": False})
    assert patched.status_code == 200 and patched.json()["is_active"] is False

    assert api_client.delete(f"/api/v1/keyword-rules/{rule_id}").status_code == 204
    gone = api_client.patch(f"/api/v1/keyword-rules/{rule_id}", json={"weight": 1})
    assert gone.status_code == 404


def test_duplicate_role_keyword_is_409(api_client):
    assert api_client.post("/api/v1/keyword-rules", json=RULE).status_code == 201
    assert api_client.post("/api/v1/keyword-rules", json=RULE).status_code == 409
