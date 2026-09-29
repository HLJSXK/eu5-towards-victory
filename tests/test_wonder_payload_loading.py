import json
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from towards_victory_editor_web.services import wonder_localization
from towards_victory_editor_web.services.wonder_localization import WonderLocalizationService


@pytest.fixture(scope="module")
def service():
    return WonderLocalizationService()


def test_bootstrap_is_summary_only(service, monkeypatch):
    def fail_detail(_wonder_id):
        raise AssertionError("bootstrap must not build a wonder detail")

    monkeypatch.setattr(service, "get_wonder_payload", fail_detail)
    payload = service.bootstrap_payload()
    assert payload["initial_wonder_id"] == payload["wonders"][0]["id"]
    assert "current_wonder" not in payload
    assert "ritual_designs" not in payload
    assert len(json.dumps(payload, ensure_ascii=False).encode("utf-8")) < 200_000


def test_ritual_catalog_is_summary_only_and_detail_is_preserved(service):
    catalog = service.ritual_design_catalog_payload()
    assert catalog["count"] == len(catalog["wonders"])
    assert len(json.dumps(catalog, ensure_ascii=False).encode("utf-8")) < 200_000
    first = catalog["wonders"][0]
    assert set(first["ritual_design"]) <= {"title", "mode", "listeners"}
    assert "implementation_mapping" not in first["ritual_design"]

    detail = service.ritual_design_payload(first["id"])
    assert detail == service.get_wonder_payload(first["id"])["ritual_design"]
    assert detail["field_labels"] == catalog["field_labels"]
    assert detail["field_labels"]["historical_flavor"] == "历史氛围"
    assert detail["source_path"] == catalog["source_path"]
    assert len(json.dumps(detail, ensure_ascii=False).encode("utf-8")) > len(
        json.dumps(first, ensure_ascii=False).encode("utf-8")
    )


def test_ritual_detail_rejects_generic_wonder(service):
    generic = next(wonder for wonder in service.list_wonders() if not wonder["is_unique"])
    with pytest.raises(ValueError, match="not a unique wonder"):
        service.ritual_design_payload(generic["id"])


def test_unique_wonder_without_ritual_design(service, monkeypatch):
    from towards_victory_editor_web import server

    entries = service.unique_ritual_designs_data["unique_wonders"]
    removed = entries[0]
    monkeypatch.setattr(service, "unique_ritual_designs_data", {"unique_wonders": entries[1:]})
    wonder = service._get_wonder(removed["id"])
    assert service._unique_ritual_design_for_wonder(wonder) is None
    with pytest.raises(KeyError, match="No ritual design"):
        service.ritual_design_payload(removed["id"])
    assert service.ritual_design_catalog_payload()["count"] == len(entries) - 1
    monkeypatch.setattr(server, "WonderLocalizationService", lambda: service)
    with TestClient(server.create_app()) as client:
        assert client.get(f"/api/wonder-localization/ritual-designs/{removed['id']}").status_code == 404


@pytest.mark.parametrize("change", ["missing_id", "wrong_key", "duplicate"])
def test_invalid_ritual_design_source_fails_service_load(service, monkeypatch, change):
    from towards_victory_editor_web import server

    entries = deepcopy(service.unique_ritual_designs_data["unique_wonders"])
    if change == "missing_id":
        del entries[0]["id"]
    elif change == "wrong_key":
        entries[0]["key"] = entries[1]["key"]
    else:
        entries.append(deepcopy(entries[0]))
    monkeypatch.setattr(service, "unique_ritual_designs_data", {"unique_wonders": entries})
    with pytest.raises(RuntimeError, match="unique_wonders") as error:
        service._validate_unique_ritual_designs()

    def fail_load():
        raise error.value

    monkeypatch.setattr(server, "WonderLocalizationService", fail_load)
    with TestClient(server.create_app()) as client:
        response = client.get("/api/wonder-localization/ritual-designs")
        assert response.status_code == 503
        assert "unique_wonders" in response.json()["detail"]


def test_http_summary_detail_and_errors(service, monkeypatch):
    from towards_victory_editor_web import server

    monkeypatch.setattr(server, "WonderLocalizationService", lambda: service)
    with TestClient(server.create_app()) as client:
        bootstrap = client.get("/api/wonder-localization/bootstrap")
        assert bootstrap.status_code == 200
        assert len(bootstrap.content) < 200_000
        assert "current_wonder" not in bootstrap.json()
        catalog = client.get("/api/wonder-localization/ritual-designs")
        assert catalog.status_code == 200
        assert len(catalog.content) < 200_000
        wonder_id = catalog.json()["wonders"][0]["id"]
        detail = client.get(f"/api/wonder-localization/ritual-designs/{wonder_id}")
        assert detail.status_code == 200
        assert detail.json() == service.ritual_design_payload(wonder_id)
        missing_id = max(wonder["id"] for wonder in service.list_wonders()) + 1
        assert client.get(f"/api/wonder-localization/ritual-designs/{missing_id}").status_code == 404
        generic = next(wonder for wonder in service.list_wonders() if not wonder["is_unique"])
        assert client.get(f"/api/wonder-localization/ritual-designs/{generic['id']}").status_code == 400


def test_http_unavailable_service(monkeypatch):
    from towards_victory_editor_web import server

    def fail_load():
        raise ValueError("invalid wonder data")

    monkeypatch.setattr(server, "WonderLocalizationService", fail_load)
    with TestClient(server.create_app()) as client:
        for path in ("bootstrap", "ritual-designs", "ritual-designs/1"):
            response = client.get(f"/api/wonder-localization/{path}")
            assert response.status_code == 503
            assert response.json()["detail"] == "invalid wonder data"


def test_prompt_save_keeps_detail_without_returning_catalog(service, monkeypatch, tmp_path):
    prompt_file = tmp_path / "prompts.yaml"
    monkeypatch.setattr(wonder_localization, "UNIQUE_RITUAL_PROMPTS_FILE", prompt_file)
    monkeypatch.setattr(service, "unique_ritual_prompts_data", {"unique_wonders": []})
    wonder_id = service.ritual_design_catalog_payload()["wonders"][0]["id"]
    payload = service.save_unique_ritual_prompt(wonder_id, "  Implement ritual\r\nwith rewards  ")
    assert payload["prompt"]["prompt"] == "Implement ritual\nwith rewards"
    assert "ritual_designs" not in payload
    assert service.get_wonder_payload(wonder_id)["ritual_prompt"] == payload["prompt"]
    assert "Implement ritual" in prompt_file.read_text(encoding="utf-8")
