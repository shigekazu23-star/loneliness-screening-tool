# ---- Integration tests for the Flask API ----
# Exercise the security-relevant paths end to end: registration, login,
# the consent gate in front of data collection, role-based access, and
# immediate effect of consent revocation on the caregiver view.

import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(db_path=str(tmp_path / "test.db"))
    app.testing = True
    return app.test_client()


def register_and_login(client, username, role):
    client.post(
        "/api/register",
        json={
            "username": username,
            "password": "Passw0rd!demo",
            "role": role,
            "display_name": username,
        },
    )
    token = client.post(
        "/api/login",
        json={"username": username, "password": "Passw0rd!demo"},
    ).get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    assert client.get("/api/health").status_code == 200


def test_register_rejects_weak_password(client):
    res = client.post(
        "/api/register",
        json={"username": "x", "password": "short", "role": "older_adult"},
    )
    assert res.status_code == 400


def test_login_rejects_bad_credentials(client):
    register_and_login(client, "hana", "older_adult")
    res = client.post(
        "/api/login", json={"username": "hana", "password": "wrongwrong"}
    )
    assert res.status_code == 401


def test_response_requires_consent(client):
    headers = register_and_login(client, "hana", "older_adult")
    res = client.post(
        "/api/responses", json={"q1": 1, "q2": 1, "q3": 1}, headers=headers
    )
    assert res.status_code == 403  # consent gate before data collection


def test_submit_after_consent_returns_score_and_flag(client):
    headers = register_and_login(client, "hana", "older_adult")
    client.post("/api/consent", headers=headers)
    res = client.post(
        "/api/responses", json={"q1": 2, "q2": 1, "q3": 3}, headers=headers
    )
    assert res.status_code == 201
    body = res.get_json()
    assert body["score"] == 6
    assert body["flag"]["level"] == "none"  # single score never flags


def test_invalid_answers_rejected(client):
    headers = register_and_login(client, "hana", "older_adult")
    client.post("/api/consent", headers=headers)
    res = client.post(
        "/api/responses", json={"q1": 9, "q2": 1, "q3": 1}, headers=headers
    )
    assert res.status_code == 400


def test_rbac_blocks_older_adult_from_caregiver_view(client):
    headers = register_and_login(client, "hana", "older_adult")
    res = client.get("/api/caregiver/overview", headers=headers)
    assert res.status_code == 403


def test_caregiver_link_requires_consent(client):
    register_and_login(client, "hana", "older_adult")
    caregiver = register_and_login(client, "kaigo", "caregiver")
    res = client.post(
        "/api/caregiver/link", json={"username": "hana"}, headers=caregiver
    )
    assert res.status_code == 403  # no consent, no link


def test_revocation_hides_data_from_caregiver_immediately(client):
    older = register_and_login(client, "hana", "older_adult")
    client.post("/api/consent", headers=older)
    client.post(
        "/api/responses", json={"q1": 2, "q2": 2, "q3": 2}, headers=older
    )
    caregiver = register_and_login(client, "kaigo", "caregiver")
    client.post(
        "/api/caregiver/link", json={"username": "hana"}, headers=caregiver
    )
    before = client.get(
        "/api/caregiver/overview", headers=caregiver
    ).get_json()
    assert len(before["people"]) == 1

    client.delete("/api/consent", headers=older)  # revocable consent (M2)
    after = client.get(
        "/api/caregiver/overview", headers=caregiver
    ).get_json()
    assert len(after["people"]) == 0
