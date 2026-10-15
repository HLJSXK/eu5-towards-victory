from __future__ import annotations

import io
import json

import pytest

from scripts_engineering_department import generate_wonder_image as wonder


@pytest.mark.parametrize("model,size,quality", [
    ("gpt-image-2.5-sunburst", "1536x1024", "high"),
    ("provider/custom-model", "1025x777", "standard"),
    ("provider/large-model", "4096x512", "hd"),
])
def test_configured_model_and_provider_parameters_reach_request(model, size, quality, monkeypatch):
    monkeypatch.setattr(wonder, "load_wonder_image_tasks", lambda **_: [{
        "key": "grand_cathedral", "name": "tv_wonder_grand_cathedral",
        "prompt": "Oil-painted cartoon cathedral", "is_unique": False,
    }])
    tasks = wonder.load_task_config({
        "defaults": {"model": model, "size": size, "quality": quality},
        "selection": {"include_unique": False},
    })
    payload = wonder.build_payload(tasks[0])
    requests = []

    class Opener:
        def open(self, request, **kwargs):
            requests.append(request)
            return io.BytesIO(b'{"data": [{"b64_json": "fixture"}]}')

    result = wonder.api_post_json(
        "https://example.invalid/v1/images/generations", "fixture", payload, 180,
        wonder.RetrySettings(1, 0, 0, 1), Opener(),
    )
    sent = json.loads(requests[0].data)
    assert sent["model"] == model
    assert sent["size"] == size
    assert sent["quality"] == quality
    assert sent["prompt"] == "Oil-painted cartoon cathedral"
    assert result["data"][0]["b64_json"] == "fixture"


@pytest.mark.parametrize("model", ["", "   ", None, 123])
def test_missing_or_invalid_model_is_rejected(model):
    with pytest.raises(ValueError, match="image.model must be a non-empty string"):
        wonder.build_payload({"model": model, "prompt": "A monument"})


@pytest.mark.parametrize("size", ["auto", "0x1024", "1024x0", "-1x1024"])
def test_pipeline_requires_explicit_positive_dimensions(size):
    with pytest.raises(ValueError):
        wonder.build_payload({"model": "custom-model", "prompt": "A monument", "size": size})


def test_generation_prepares_nested_output_directories_before_request(tmp_path, monkeypatch):
    monkeypatch.setattr(wonder, "REPO_ROOT", tmp_path)
    task = {
        "name": "tv_wonder_construction", "prompt": "A simple painted worksite",
        "png_dir": "assets/generated_wonders/oil_cartoon",
        "dds_dir": "assets/generated_wonders/oil_cartoon/dds",
        "metadata_dir": "data/generated_wonders/oil_cartoon",
    }
    metadata_dir = tmp_path / task["metadata_dir"]
    assert not metadata_dir.exists()

    class RequestReached(Exception):
        pass

    def request(*args, **kwargs):
        for key in ("png_dir", "dds_dir", "metadata_dir"):
            assert (tmp_path / task[key]).is_dir()
        raise RequestReached

    monkeypatch.setattr(wonder, "api_post_json", request)
    with pytest.raises(RequestReached):
        wonder.run_generation({"api": {"api_key": "fixture"}}, [task], {})

    metadata_path = metadata_dir / "nested" / "tv_wonder_construction.json"
    payload = {"prompt": "The actual generation prompt"}
    wonder.write_metadata(metadata_path, payload, {"created": 123}, "revised prompt")
    assert json.loads(metadata_path.read_text(encoding="utf-8")) == {
        "payload": payload, "created": 123, "revised_prompt": "revised prompt",
    }
