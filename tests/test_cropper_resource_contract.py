import json

import pytest
from fastapi.testclient import TestClient

from towards_victory_editor_web.services import cropper as cropper_module
from towards_victory_editor_web.services.cropper import CropperService, ImageTask
from towards_victory_editor_web.services.platform import ConflictError


@pytest.fixture
def service(tmp_path):
    data_dir = tmp_path / "data"
    images_dir = tmp_path / "assets"
    data_dir.mkdir()
    images_dir.mkdir()
    png = images_dir / "sample.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + (270).to_bytes(4, "big") + (110).to_bytes(4, "big"))
    task = ImageTask("sample", "Sample", "sample", png, images_dir / "sample.dds", "configured")
    return CropperService(tasks=[task], data_path=data_dir / "wonder_image_crops.json", repo_root=tmp_path)


def base_of(payload):
    return {item["path"]: item["sha256"] for item in payload["change_set"]["base"]}


def test_crop_preview_commit_and_remove(service):
    initial = service.load_resource()
    assert initial["resource"]["source_paths"] == ["data/wonder_image_crops.json"]
    assert initial["draft"]["tasks"][0]["saved"] is False
    base = base_of(initial)
    rect = {"x": 12, "y": 10, "width": 200, "height": 80}
    edits = {"0": rect}
    assert service.validate_edits(edits)["valid"]
    preview = service.preview_edits(edits, base)
    assert preview["diff"][0]["after"]["rect"]["x"] == 12
    assert preview["change_set"]["files"] == ["data/wonder_image_crops.json"]
    assert not service.data_path.exists()

    saved = service.commit_edits(edits, base)
    assert saved["draft"]["tasks"][0]["saved"] is True
    assert base_of(saved) != base
    assert json.loads(service.data_path.read_text())["crops"]["sample"]["rect"]["x"] == 12
    with pytest.raises(ConflictError):
        service.commit_edits(edits, base)

    removed = service.commit_edits({"0": None}, base_of(saved))
    assert removed["draft"]["tasks"][0]["saved"] is False
    assert json.loads(service.data_path.read_text())["crops"] == {}


def test_bad_edits_and_external_change_preserve_source(service):
    initial = service.load_resource()
    base = base_of(initial)
    assert not service.validate_edits({"-1": None})["valid"]
    assert not service.validate_edits({"0": {"x": "nan", "y": 0, "width": 20, "height": 10}})["valid"]
    with pytest.raises(ValueError, match="base must include"):
        service.preview_edits({}, {})
    service.data_path.write_text('{"crops": {}}\n')
    with pytest.raises(ConflictError):
        service.preview_edits({"0": None}, base)
    with pytest.raises(ConflictError):
        service.commit_edits({"0": None}, base)
    assert service.data_path.read_text() == '{"crops": {}}\n'


def test_failed_write_restores_source(service, monkeypatch):
    service.data_path.write_text('{"crops": {}}\n')
    base = base_of(service.load_resource())
    original = service.data_path.read_bytes()

    def failed_write(files):
        for path, content in files.items():
            path.write_bytes(content)
        raise OSError("write failed")

    monkeypatch.setattr(cropper_module, "atomic_write_files", failed_write)
    with pytest.raises(OSError, match="write failed"):
        service.commit_edits({"0": {"x": 0, "y": 0, "width": 270, "height": 110}}, base)
    assert service.data_path.read_bytes() == original
    assert base_of(service.load_resource()) == base


def test_http_resource_contract(service, monkeypatch):
    from towards_victory_editor_web import server

    monkeypatch.setattr(server, "cropper", service)
    with TestClient(server.create_app()) as client:
        assert "editor.wonder_crop" in {item["id"] for item in client.get("/api/tools").json()["tools"]}
        loaded = client.get("/api/resources/editor.wonder_crop")
        assert loaded.status_code == 200
        base = base_of(loaded.json())
        endpoint = "/api/resources/editor.wonder_crop/commit"
        assert client.post(endpoint, json={"edits": {"0": None}}).status_code == 400
        assert client.post(endpoint, json={"edits": {"0": None}, "base": base}).status_code == 200
        invalid = client.post(endpoint, json={"edits": {"99999": None}, "base": base})
        assert invalid.status_code == 400
        assert invalid.json()["detail"] == "Unknown crop image index: 99999"
        assert "log_text" not in invalid.json()
        assert client.post("/api/cropper/0/save", json={"rect": {}}).status_code == 404
