import pytest


@pytest.fixture
def without_wonder_service(monkeypatch):
    """Skip the multi-second Wonder load in HTTP tests that never call Wonder routes."""
    from towards_victory_editor_web import server

    def unavailable(_operation_store):
        raise RuntimeError("Wonder service is not loaded in this test")

    monkeypatch.setattr(server, "WonderResourceService", unavailable)
