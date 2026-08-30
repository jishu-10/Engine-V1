from __future__ import annotations

from fastapi.testclient import TestClient


def test_internal_validation_workflow(client: TestClient) -> None:
    created_a = client.post("/api/v1/users", json={"id": "api_a"})
    created_b = client.post("/api/v1/users", json={"id": "api_b"})
    assert created_a.status_code == 201
    assert created_b.status_code == 201

    prompts = client.get("/api/v1/prompts/onboarding")
    assert prompts.status_code == 200
    prompt_payload = prompts.json()
    assert len(prompt_payload) == 10
    assert prompt_payload[0]["prompt_id"] == "P01"

    for prompt in prompt_payload:
        for user_id, option in [("api_a", "A"), ("api_b", "B")]:
            response = client.post(
                "/api/v1/responses",
                json={
                    "user_id": user_id,
                    "prompt_id": prompt["prompt_id"],
                    "selected_option": option,
                },
            )
            assert response.status_code == 201

    completion = client.get("/api/v1/profile/completion", params={"user_id": "api_a"})
    assert completion.status_code == 200
    assert completion.json()["completion"] == 1.0

    next_prompt = client.get("/api/v1/prompts/next", params={"user_id": "api_a"})
    assert next_prompt.status_code == 200
    assert next_prompt.json()["prompt"] is None

    profile = client.get("/api/v1/profile", params={"user_id": "api_a"})
    assert profile.status_code == 200
    assert profile.json()["profile_completion"] == 1.0

    comparison = client.post(
        "/api/v1/similarity/compare",
        json={"user_a_id": "api_a", "user_b_id": "api_b"},
    )
    assert comparison.status_code == 201
    comparison_payload = comparison.json()
    assert comparison_payload["id"]
    assert comparison_payload["algorithm_version"] == "similarity_v1"
    assert comparison_payload["evidence"]

    fetched = client.get(f"/api/v1/similarity/{comparison_payload['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == comparison_payload["id"]

    explanation = client.post(
        f"/api/v1/similarity/{comparison_payload['id']}/explanation",
        json={"use_llm": False},
    )
    assert explanation.status_code == 201
    assert explanation.json()["generated_by"] == "fallback"

    metrics = client.get("/api/v1/validation/metrics")
    assert metrics.status_code == 200
    assert metrics.json()["users"] == 2
    assert metrics.json()["responses"] == 20


def test_invalid_option_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/responses",
        json={"user_id": "api_bad", "prompt_id": "P01", "selected_option": "Z"},
    )
    assert response.status_code == 422

