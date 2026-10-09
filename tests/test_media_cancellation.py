from __future__ import annotations

import io
import json
import sys
import threading
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from scripts import generate_dds_icon as icons
from scripts import generate_historical_images as historical
from scripts_engineering_department import generate_wonder_image as wonder
from towards_victory_editor_web.services.platform import OperationCancelled, OperationLog


@pytest.mark.parametrize("kind", ["icon", "wonder", "download"])
@pytest.mark.parametrize("http_error", [False, True])
def test_cancellation_interrupts_retry_wait_without_another_request(kind, http_error):
    operation = OperationLog("media_job")
    waiting = threading.Event()
    calls = []
    def open_request(request, **kwargs):
        calls.append(request.full_url)
        if http_error:
            raise urllib.error.HTTPError(request.full_url, 503, "unavailable", {}, io.BytesIO(b"retry"))
        raise urllib.error.URLError("offline")
    def wait(seconds):
        waiting.set()
        operation.wait(seconds)
    def cancel():
        if waiting.wait(5):
            operation.request_cancel()
    canceller = threading.Thread(target=cancel)
    canceller.start()
    settings = SimpleNamespace(max_attempts=3, initial_delay_seconds=60, backoff_multiplier=2, max_delay_seconds=60)
    opener = SimpleNamespace(open=open_request)
    controls = dict(check_cancelled=operation.check_cancelled, wait=wait)
    try:
        with pytest.raises(OperationCancelled):
            if kind == "icon":
                icons.api_request("test", urllib.request.Request("https://example.invalid/image"), 180, settings, opener, **controls)
            elif kind == "wonder":
                wonder.api_post_json("https://example.invalid/image", "fixture", {}, 180, settings, opener, **controls)
            else:
                wonder.download_bytes("https://example.invalid/image", 180, settings, opener, **controls)
    finally:
        operation.request_cancel()
        canceller.join(5)
    assert len(calls) == 1


@pytest.mark.parametrize("kind", ["icon", "wonder", "historical"])
def test_cancellation_after_response_prevents_image_download(kind, tmp_path, monkeypatch):
    operation = OperationLog("media_job")
    calls = []
    response = json.dumps({"data": [{"url": "https://example.invalid/download"}]}).encode()
    def open_request(request, **kwargs):
        calls.append(request.full_url)
        operation.request_cancel()
        return io.BytesIO(response)
    opener = SimpleNamespace(open=open_request)
    settings = SimpleNamespace(max_attempts=3)
    with pytest.raises(OperationCancelled):
        if kind == "icon":
            payload = icons.api_post_json("https://example.invalid/image", "fixture", {}, 180, settings, opener, check_cancelled=operation.check_cancelled)
            icons.extract_image_bytes(payload, 180, settings, opener, check_cancelled=operation.check_cancelled)
        elif kind == "wonder":
            payload = wonder.api_post_json("https://example.invalid/image", "fixture", {}, 180, settings, opener, check_cancelled=operation.check_cancelled)
            wonder.extract_png_bytes(payload, 180, settings, opener, check_cancelled=operation.check_cancelled)
        else:
            source = tmp_path / "source.png"
            source.write_bytes(b"source")
            monkeypatch.setattr(historical.urllib.request, "urlopen", open_request)
            historical.edit_image({"endpoint": "https://example.invalid/image", "model": "fixture"}, source, "fixture", check_cancelled=operation.check_cancelled)
    assert calls == ["https://example.invalid/image"]


def test_icon_batch_does_not_start_next_task_after_cancellation(monkeypatch):
    operation = OperationLog("media_job")
    calls = []
    task = SimpleNamespace(path_id="test", kind="test", prompt_config={}, image_config={}, output_config={}, target=None, allow_missing_style_reference_dry_run=False)
    def run(*args, **controls):
        calls.append(args)
        operation.request_cancel()
    monkeypatch.setattr(icons, "run_target_generation", run)
    with pytest.raises(OperationCancelled):
        icons.run_generation_tasks({"api": {}, "style_reference": {}}, None, [task, task], check_cancelled=operation.check_cancelled)
    assert len(calls) == 1


def test_wonder_batch_does_not_start_next_task_after_cancellation(tmp_path, monkeypatch):
    operation = OperationLog("media_job")
    calls = []
    monkeypatch.setattr(wonder, "resolve_api_key", lambda _: "fixture")
    monkeypatch.setattr(wonder, "REPO_ROOT", tmp_path)
    def skip_task(task):
        calls.append(task)
        operation.request_cancel()
        return "test"
    monkeypatch.setattr(wonder, "wonder_file_stem", skip_task)
    with pytest.raises(OperationCancelled):
        wonder.run_generation({"api": {}, "dds": {}}, [{"name": "one", "enabled": False}, {"name": "two", "enabled": False}], {}, check_cancelled=operation.check_cancelled)
    assert len(calls) == 1


def test_historical_batch_does_not_start_next_image_after_cancellation(tmp_path, monkeypatch):
    operation = OperationLog("media_job")
    calls = []
    monkeypatch.setattr(historical, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(historical, "CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.setattr(historical, "OUTPUT_DIR", tmp_path / "output")
    def edit(*args, **controls):
        calls.append(args)
        operation.request_cancel()
        return b"unused"
    monkeypatch.setattr(historical, "edit_image", edit)
    tasks = [(tmp_path / f"{i}.png", tmp_path / "output" / f"{i}.png") for i in range(2)]
    with pytest.raises(OperationCancelled):
        historical.run_tasks({"overwrite": True, "api_key": "fixture"}, tasks, check_cancelled=operation.check_cancelled)
    assert len(calls) == 1
    assert not any(output.exists() for _, output in tasks)


def test_crop_conversion_stops_dispatch_and_waits_for_active_workers(monkeypatch):
    operation = OperationLog("media_job")
    started, release, shutting_down = (threading.Event() for _ in range(3))
    calls, errors = [], []
    class ObservedPool(ThreadPoolExecutor):
        def shutdown(self, wait=True, *, cancel_futures=False):
            assert wait and cancel_futures
            shutting_down.set()
            super().shutdown(wait=wait, cancel_futures=cancel_futures)
    def worker(job):
        calls.append(job)
        if len(calls) == 2:
            started.set()
        assert release.wait(5)
        return ["converted"]
    monkeypatch.setattr(wonder.os, "cpu_count", lambda: 2)
    monkeypatch.setattr(wonder.concurrent.futures, "ProcessPoolExecutor", ObservedPool)
    monkeypatch.setattr(wonder, "convert_existing_dds_worker", worker)
    def run():
        try:
            wonder.run_parallel_existing_dds_jobs(list(range(10)), check_cancelled=operation.check_cancelled)
        except Exception as error:
            errors.append(error)
    thread = threading.Thread(target=run)
    thread.start()
    try:
        assert started.wait(5)
        operation.request_cancel()
        assert shutting_down.wait(5)
        assert thread.is_alive(), "staging must stay available until workers finish"
    finally:
        release.set()
        thread.join(5)
    assert not thread.is_alive()
    assert len(calls) == 2
    assert len(errors) == 1 and isinstance(errors[0], OperationCancelled)


def test_crop_conversion_dispatches_all_jobs_on_success(monkeypatch):
    monkeypatch.setattr(wonder.concurrent.futures, "ProcessPoolExecutor", ThreadPoolExecutor)
    monkeypatch.setattr(wonder.os, "cpu_count", lambda: 2)
    calls = []
    def worker(job):
        calls.append(job)
        return []
    monkeypatch.setattr(wonder, "convert_existing_dds_worker", worker)
    assert wonder.run_parallel_existing_dds_jobs(list(range(10))) == 10
    assert sorted(calls) == list(range(10))
