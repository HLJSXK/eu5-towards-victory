from __future__ import annotations

import hashlib
import threading
from dataclasses import replace
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from towards_victory_editor_web.services import wonder_localization
from towards_victory_editor_web.services.wonder_generation import LOCALIZATION_SCRIPTS, wonder_generation_plan
from towards_victory_editor_web.services.common import RollingLog
from towards_victory_editor_web.services.platform import ConflictError, ResourceDescriptor, resource_operation, snapshot_files


SOURCE_ATTRIBUTES = (
    "WONDER_LOCALIZATION_FILE",
    "WONDER_FINAL_BUILDINGS_FILE",
    "WONDER_GENERIC_RITUALS_FILE",
    "WONDER_BASE_MODIFIERS_FILE",
    "WONDER_SITE_RULES_FILE",
    "WONDERS_FILE",
    "UNIQUE_WONDERS_FILE",
)


def _registry(tmp_path, outputs):
    entries = []
    for index, script in enumerate(LOCALIZATION_SCRIPTS.values()):
        # Each real localization generator owns separate files.
        owned = list(outputs[index::2]) or [f"generated/unused_{index}.txt"]
        entries.extend({"script": script, "output": output} for output in owned)
        path = tmp_path / script
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("from pathlib import Path\n" + "\n".join(
            f"Path({output!r}).parent.mkdir(parents=True, exist_ok=True); "
            f"Path({output!r}).write_text('sample = {{}}\\n')" for output in owned
        ))
    (tmp_path / "data/generated_files.yaml").write_text(yaml.safe_dump({"generated": entries}))


@pytest.fixture
def service(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    for index, attribute in enumerate(SOURCE_ATTRIBUTES):
        path = data_dir / f"source_{index}.yaml"
        path.write_bytes(f"source-{index}\n".encode())
        monkeypatch.setattr(wonder_localization, attribute, path)
    monkeypatch.setattr(wonder_localization, "REPO_ROOT", tmp_path)
    _registry(tmp_path, ("generated/localization.yml",))

    service = object.__new__(wonder_localization.WonderLocalizationService)
    service._lock = threading.RLock()
    service._base = snapshot_files(wonder_localization._wonder_source_paths(), repo_root=tmp_path)
    service.wonders_data = {"wonders": []}
    service.mechanics_data = {}
    service.unique_wonders_data = {"unique_wonders": []}
    service.localization_data = {"english": {}, "simp_chinese": {}}
    service.wonders = []
    service.mechanics = {}
    service.event_suffixes = {}
    service._option_catalogs = {}
    service._option_catalog_version = "test"
    service._log = RollingLog()
    service.reload_from_disk = lambda: None
    return service


def _base(service) -> dict[str, str]:
    return {item.path: item.sha256 for item in service._base}


def test_resource_descriptor_and_base_snapshot(service):
    descriptor = service.resource_descriptor().payload()
    base = _base(service)

    assert descriptor["id"] == "editor.wonder"
    assert descriptor["kind"] == "yaml_aggregate"
    assert set(descriptor["source_paths"]) == set(base)
    assert all(len(digest) == 64 for digest in base.values())


def test_validate_does_not_mutate_cached_draft(service):
    service.localization_data = {"english": {"title": "before"}, "simp_chinese": {}}

    def mutate_then_report(_wonder_id, _values, _mechanics):
        service.localization_data["english"]["title"] = "temporary"
        return {"localization": False, "mechanics": False, "wonders": False, "unique": False}

    service._apply_wonder_edits = mutate_then_report
    result = service.validate_resource_edits({1: {"values": {}, "mechanics": {}}})

    assert result["valid"]
    assert service.localization_data["english"]["title"] == "before"


def test_preview_reports_changed_source_file(service):
    source_path = wonder_localization._wonder_source_paths()[0]
    new_content = b"updated\n"
    service._candidate_for_drafts = lambda _drafts: (
        {"localization": True, "mechanics": False, "wonders": False, "unique": False},
        {source_path: new_content},
        [1],
    )

    report = service.preview_resource_edits({}, _base(service))

    relative = str(source_path.relative_to(wonder_localization.REPO_ROOT)).replace("\\", "/")
    assert report["valid"]
    assert report["diff"] == [
        {
            "path": relative,
            "before": service._base[0].sha256,
            "after": hashlib.sha256(new_content).hexdigest(),
        }
    ]


def test_preview_requires_complete_base(service):
    with pytest.raises(ValueError, match="base must include snapshots"):
        service.preview_resource_edits({}, {})


def test_external_source_change_conflicts_with_loaded_base(service):
    source_path = wonder_localization._wonder_source_paths()[0]
    source_path.write_bytes(b"external\n")

    with pytest.raises(ConflictError, match="Resource changed since load"):
        service.preview_resource_edits({}, _base(service))


@pytest.mark.parametrize("failure", ["external_edit", "loader_error"])
def test_reload_does_not_publish_partial_or_stale_state(service, monkeypatch, failure):
    previous_data = service.wonders_data
    previous_base = service._base
    source = wonder_localization.WONDERS_FILE
    monkeypatch.delattr(service, "reload_from_disk")

    def load(loaded):
        loaded.wonders_data = {"raw": source.read_text()}
        loaded._option_catalog_version = "partial"
        if failure == "external_edit":
            source.write_bytes(b"external change after parse\n")
        else:
            raise ValueError("loader failed")

    monkeypatch.setattr(type(service), "_load_from_disk", load)
    error = ConflictError if failure == "external_edit" else ValueError
    with pytest.raises(error):
        service.reload_from_disk()
    assert service.wonders_data is previous_data
    assert service._base is previous_base
    assert service._option_catalog_version == "test"
    if failure == "external_edit":
        with pytest.raises(ConflictError):
            service.commit_resource({}, _base(service), regenerate=False)


def test_repeated_stable_loads_keep_base_and_publish_new_data(service, monkeypatch):
    monkeypatch.delattr(service, "reload_from_disk")
    source = wonder_localization.WONDERS_FILE
    source.write_bytes(b"new content\n")

    def load(loaded):
        loaded.wonders_data = {"raw": source.read_text()}

    monkeypatch.setattr(type(service), "_load_from_disk", load)
    service.reload_from_disk()
    base = _base(service)
    service.reload_from_disk()
    assert _base(service) == base
    assert service.wonders_data == {"raw": "new content\n"}
    assert service.preview_resource_edits({}, base)["diff"] == []


def test_crlf_mechanics_edit_changes_only_edited_source(service):
    sources = {
        "buildings": wonder_localization.WONDER_FINAL_BUILDINGS_FILE,
        "generic_rituals": wonder_localization.WONDER_GENERIC_RITUALS_FILE,
        "base_modifiers": wonder_localization.WONDER_BASE_MODIFIERS_FILE,
        "site_rules": wonder_localization.WONDER_SITE_RULES_FILE,
    }
    for key, path in sources.items():
        service.mechanics_data[key] = {"sample": 1}
        text = wonder_localization.dump_yaml_document({key: {"sample": 1}})
        path.write_bytes(text.replace("\n", "\r\n").encode())
    service._base = snapshot_files(wonder_localization._wonder_source_paths(), repo_root=wonder_localization.REPO_ROOT)
    service.mechanics_data["buildings"]["sample"] = 2
    changed = {"localization": False, "mechanics": True, "wonders": False, "unique": False}
    files = service._candidate_source_bytes(changed)
    assert set(files) == {sources["buildings"]}
    raw = files[sources["buildings"]]
    assert b"\r\n" in raw
    assert b"\n" not in raw.replace(b"\r\n", b"")
    service._candidate_for_drafts = lambda _drafts: (changed, files, [1])
    report = service.preview_resource_edits({}, _base(service), regenerate=False)
    assert [item["path"] for item in report["diff"]] == [sources["buildings"].relative_to(wonder_localization.REPO_ROOT).as_posix()]


def test_localization_bytes_preserve_crlf_header_and_bom(service, monkeypatch):
    path = wonder_localization.WONDER_LOCALIZATION_FILE
    path.write_bytes(b"\xef\xbb\xbf# Canonical localization\r\nwonder_localization: {}\r\n")
    monkeypatch.setattr(wonder_localization, "collapse_wonder_localization_data", lambda data: data)
    raw = service._localization_bytes(path, {"english": {"title": "new"}, "simp_chinese": {}})
    assert raw.startswith(b"\xef\xbb\xbf# Canonical localization\r\n")
    assert b"\n" not in raw.replace(b"\r\n", b"")
    assert yaml.safe_load(raw)["wonder_localization"]["english"]["title"] == "new"


@pytest.mark.parametrize("regenerate", [False, True])
def test_generation_snapshots_only_planned_files(service, tmp_path, monkeypatch, regenerate):
    from towards_victory_editor_web.services import platform

    if regenerate:
        _registry(tmp_path, ("generated/english.yml", "generated/chinese.yml"))
    else:
        (tmp_path / "data/generated_files.yaml").unlink()
    source = wonder_localization.WONDER_LOCALIZATION_FILE
    service._candidate_for_drafts = lambda _drafts: (
        {"localization": True, "mechanics": False, "wonders": False, "unique": False},
        {source: b"new content\n"}, [1],
    )
    snapshots = []
    snapshot = platform.snapshot_file_contents

    def record(paths):
        snapshots.extend(paths)
        return snapshot(paths)

    monkeypatch.setattr(platform, "snapshot_file_contents", record)
    executed = []
    monkeypatch.setattr(wonder_localization, "run_generation", lambda plan, **_kwargs: executed.extend(step.spec.script for step in plan.steps))
    result = service.commit_resource({}, _base(service), regenerate=regenerate)
    assert result["changed_files"] == [source.relative_to(tmp_path).as_posix()]
    expected = [source]
    if regenerate:
        expected.extend([tmp_path / "generated/english.yml", tmp_path / "generated/chinese.yml"])
    assert snapshots == expected
    assert executed == (list(LOCALIZATION_SCRIPTS.values()) if regenerate else [])


def test_generator_outputs_follow_registered_plan():
    root = Path(__file__).resolve().parents[1]
    localization = wonder_generation_plan({"localization": True}, repo_root=root)
    mechanics = wonder_generation_plan({"mechanics": True}, repo_root=root)
    assert set(localization.outputs) == set(wonder_localization.GENERATED_LOC_FILES.values())
    assert len(mechanics.outputs) == 22
    assert len(mechanics.steps) == 23
    assert set(localization.outputs) <= set(mechanics.outputs)


@pytest.mark.parametrize("failure", ["conflict", "validation"])
def test_commit_logs_prewrite_errors_without_mutating_state(service, failure):
    original = RuntimeError("not used")
    base = _base(service)
    before = wonder_localization.WONDER_LOCALIZATION_FILE.read_bytes()
    if failure == "conflict":
        base[next(iter(base))] = "stale"
        expected = ConflictError
    else:
        original = ValueError("modifier table is invalid")
        def invalid_draft(_drafts):
            raise original
        service._candidate_for_drafts = invalid_draft
        expected = ValueError
    with pytest.raises(expected) as error:
        service.commit_resource({}, base, regenerate=False)
    assert f"[error] {error.value}" in service.log_text
    assert wonder_localization.WONDER_LOCALIZATION_FILE.read_bytes() == before
    if failure == "validation":
        assert error.value is original


def test_commit_conflicts_while_wonder_media_job_holds_resource(service):
    source_path = wonder_localization._wonder_source_paths()[0]
    before = source_path.read_bytes()
    service._candidate_for_drafts = lambda _drafts: pytest.fail("busy commit prepared a candidate")
    with resource_operation(("editor.wonder",)):
        with pytest.raises(ConflictError, match="Resource busy: editor.wonder"):
            service.commit_resource({}, _base(service), regenerate=False)
    assert "[error] Resource busy: editor.wonder" in service.log_text
    assert source_path.read_bytes() == before


def test_commit_rejects_unknown_current_wonder_before_writing(service):
    source_path = wonder_localization._wonder_source_paths()[0]
    source_before = source_path.read_bytes()
    service._candidate_for_drafts = lambda _drafts: (
        {"localization": True, "mechanics": False, "wonders": False, "unique": False},
        {source_path: b"new source\n"},
        [1],
    )

    with pytest.raises(KeyError, match="Unknown wonder id"):
        service.commit_resource({}, _base(service), current_wonder_id=999, regenerate=False)

    assert source_path.read_bytes() == source_before


def test_response_failure_restores_committed_files(service, tmp_path, monkeypatch):
    output = tmp_path / "generated.txt"
    output.write_bytes(b"old artifact\n")
    _registry(tmp_path, ("generated.txt",))
    source_path = wonder_localization._wonder_source_paths()[0]
    source_before = source_path.read_bytes()
    service._candidate_for_drafts = lambda _drafts: (
        {"localization": True, "mechanics": False, "wonders": False, "unique": False},
        {source_path: b"new source\n"},
        [1],
    )
    monkeypatch.setattr(wonder_localization, "run_generation", lambda _plan, **_kwargs: output.write_bytes(b"new artifact\n"))

    def fail_response():
        raise RuntimeError("response failed")

    service._resource_payload = fail_response
    with pytest.raises(RuntimeError, match="response failed"):
        service.commit_resource({}, _base(service))

    assert source_path.read_bytes() == source_before
    assert output.read_bytes() == b"old artifact\n"


def test_generator_failure_restores_sources_and_existing_outputs(service, tmp_path, monkeypatch):
    service.wonders = [{"id": 1, "key": "test"}]
    existing_output = tmp_path / "generated" / "existing.txt"
    new_output = tmp_path / "generated" / "created.txt"
    existing_output.parent.mkdir()
    existing_output.write_bytes(b"old artifact\n")
    _registry(tmp_path, ("generated/existing.txt", "generated/created.txt"))

    source_path = wonder_localization._wonder_source_paths()[0]
    source_before = source_path.read_bytes()
    service._candidate_for_drafts = lambda _drafts: (
        {"localization": True, "mechanics": False, "wonders": False, "unique": False},
        {source_path: b"new source\n"},
        [1],
    )

    def fail_after_writing(_plan, **_kwargs):
        wonder_localization.atomic_write_files(
            {existing_output: b"new artifact\n", new_output: b"newly created\n"}
        )
        raise RuntimeError("generator failed")

    monkeypatch.setattr(wonder_localization, "run_generation", fail_after_writing)
    with pytest.raises(RuntimeError, match="generator failed"):
        service.commit_resource({}, _base(service), current_wonder_id=1)

    assert source_path.read_bytes() == source_before
    assert existing_output.read_bytes() == b"old artifact\n"
    assert not new_output.exists()


def test_http_resource_contract_maps_missing_base_and_conflict(monkeypatch):
    from towards_victory_editor_web import server

    descriptor = ResourceDescriptor(
        id="editor.wonder",
        kind="yaml_aggregate",
        label="test",
        source_paths=("data/wonder.yaml",),
    ).payload()
    base = {"data/wonder.yaml": "loaded"}

    class FakeWonderService:
        log_text = ""

        def load_resource(self):
            return {"resource": descriptor, "draft": {}, "change_set": {"base": []}}

        def validate_resource_edits(self, _drafts):
            return {"valid": True, "errors": [], "resource": descriptor}

        def preview_resource_edits(self, _drafts, incoming_base, **_kwargs):
            if not incoming_base:
                raise ValueError("base must include snapshots for all resource files")
            if incoming_base != base:
                raise ConflictError("Resource changed since load: data/wonder.yaml")
            return {"valid": True, "errors": [], "diff": [], "change_set": {"base": []}}

        def commit_resource(self, _drafts, incoming_base, **_kwargs):
            if not incoming_base:
                raise ValueError("base must include snapshots for all resource files")
            return {"status": "ok"}

    monkeypatch.setattr(server, "CostRewardEditorService", lambda: object())
    monkeypatch.setattr(server, "VictoryTreePlannerService", lambda: object())
    monkeypatch.setattr(server, "WonderLocalizationService", FakeWonderService)

    with TestClient(server.create_app()) as client:
        assert client.get("/api/resources/editor.wonder").status_code == 200
        assert client.post("/api/resources/editor.wonder/validate", json={}).status_code == 200
        assert client.post("/api/resources/editor.wonder/preview", json={}).status_code == 400
        assert (
            client.post(
                "/api/resources/editor.wonder/preview",
                json={"base": {"data/wonder.yaml": "stale"}},
            ).status_code
            == 409
        )
        assert (
            client.post(
                "/api/resources/editor.wonder/commit",
                json={"base": base, "wonders": []},
            ).status_code
            == 200
        )


@pytest.mark.parametrize("failure,status", [("validation", 400), ("conflict", 409), ("generator", 500)])
def test_http_commit_errors_include_service_log(service, monkeypatch, failure, status):
    from towards_victory_editor_web import server

    monkeypatch.setattr(server, "CostRewardEditorService", lambda: object())
    monkeypatch.setattr(server, "VictoryTreePlannerService", lambda: object())
    monkeypatch.setattr(server, "WonderLocalizationService", lambda: service)
    base = _base(service)
    if failure == "conflict":
        base[next(iter(base))] = "stale"
    elif failure == "validation":
        def invalid_draft(_drafts):
            raise ValueError("invalid modifier table")
        service._candidate_for_drafts = invalid_draft
    else:
        source = wonder_localization.WONDER_LOCALIZATION_FILE
        service._candidate_for_drafts = lambda _drafts: (
            {"localization": True, "mechanics": False, "wonders": False, "unique": False},
            {source: b"new source\n"}, [1],
        )
        def fail_generator(_plan, **_kwargs):
            raise RuntimeError("generator X exited with 1")
        monkeypatch.setattr(wonder_localization, "run_generation", fail_generator)
    with TestClient(server.create_app()) as client:
        response = client.post("/api/resources/editor.wonder/commit", json={"base": base})
    assert response.status_code == status
    assert response.json()["log_text"] == service.log_text
    assert response.json()["detail"] in service.log_text
    assert "[error]" in service.log_text


def test_preview_plan_matches_committed_generation_and_artifacts(service, tmp_path):
    source = wonder_localization.WONDER_LOCALIZATION_FILE
    _registry(tmp_path, ('generated/english.txt', 'generated/chinese.txt'))
    service._candidate_for_drafts = lambda _drafts: (
        {'localization': True}, {source: b'new source\n'}, [1],
    )
    preview = service.preview_resource_edits({}, _base(service))
    assert len(preview['generation_plan']['steps']) == 2
    assert not (tmp_path / 'generated').exists()
    service.reload_from_disk = lambda: setattr(service, '_base', snapshot_files(
        wonder_localization._wonder_source_paths(), repo_root=tmp_path))
    result = service.commit_resource({}, _base(service))
    assert result['generation']['plan'] == preview['generation_plan']
    assert result['generation']['status'] == 'succeeded'
    assert all(item['changed'] for item in result['generation']['artifacts'])
    assert all(item['valid'] for item in result['generation']['output_validation'])
    assert source.read_bytes() == b'new source\n'


@pytest.mark.parametrize('failure', ['missing', 'invalid', 'exit', 'bom', 'timeout'])
def test_real_runner_failure_rolls_back_and_returns_http_report(service, tmp_path, monkeypatch, failure):
    from towards_victory_editor_web import server

    source = wonder_localization.WONDER_LOCALIZATION_FILE
    source_before = source.read_bytes()
    output_name = ('src_engineering_department/in_game/common/scripted_effects/sample.txt'
                   if failure == 'bom' else 'generated/english.txt')
    _registry(tmp_path, (output_name, 'generated/chinese.txt'))
    output = tmp_path / output_name
    output.parent.mkdir(parents=True)
    output_before = b'\xef\xbb\xbfold = {}\n'
    output.write_bytes(output_before)
    script = tmp_path / LOCALIZATION_SCRIPTS['english']
    action = {
        'missing': f"Path({output_name!r}).unlink()",
        'invalid': f"Path({output_name!r}).write_text('broken = {{')",
        'exit': f"Path({output_name!r}).write_text('partial = {{}}'); raise SystemExit(9)",
        'bom': f"Path({output_name!r}).write_text('old = {{}}\\n', encoding='utf-8')",
        'timeout': (f"Path({output_name!r}).write_text('partial = {{}}'); "
                    "print('partial output before timeout', flush=True); "
                    "import time; time.sleep(60)"),
    }[failure]
    script.write_text('from pathlib import Path\n' + action)
    service._candidate_for_drafts = lambda _drafts: (
        {'localization': True}, {source: b'new source\n'}, [1],
    )
    if failure == 'timeout':
        def short_plan(*args, **kwargs):
            plan = wonder_generation_plan(*args, **kwargs)
            return replace(plan, steps=tuple(
                replace(step, spec=replace(step.spec, timeout_seconds=1)) for step in plan.steps))
        monkeypatch.setattr(wonder_localization, 'wonder_generation_plan', short_plan)
    monkeypatch.setattr(server, 'CostRewardEditorService', lambda: object())
    monkeypatch.setattr(server, 'VictoryTreePlannerService', lambda: object())
    monkeypatch.setattr(server, 'WonderLocalizationService', lambda: service)
    with TestClient(server.create_app()) as client:
        response = client.post('/api/resources/editor.wonder/commit', json={'base': _base(service)})
    assert response.status_code == 500
    report = response.json()['generation']
    assert report['status'] == 'failed'
    assert report['rollback'] == {'status': 'succeeded', 'errors': []}
    assert [step['status'] for step in report['steps']] == ['failed', 'skipped']
    assert report['artifacts'][0]['changed']
    assert source.read_bytes() == source_before
    assert output.read_bytes() == output_before
    assert not (tmp_path / 'generated/chinese.txt').exists()
    if failure == 'bom':
        assert 'UTF-8 BOM' in response.json()['detail']
        assert not report['output_validation'][0]['valid']
    if failure == 'timeout':
        assert report['steps'][0]['timed_out']
        assert report['plan']['steps'][0]['timeout_seconds'] == 1
        assert 'timed out after 1s' in response.json()['detail']
        assert 'partial output before timeout' in response.json()['log_text']
        assert report['artifacts'][0]['sha256'] == hashlib.sha256(b'partial = {}').hexdigest()
    # The request ran on another thread. Both service and resource locks must
    # be reusable after recovery, including after the subprocess is killed.
    assert service._lock.acquire(blocking=False)
    service._lock.release()
    with resource_operation(('editor.wonder',)):
        pass


def test_plan_errors_precede_source_write(service, tmp_path):
    source = wonder_localization.WONDER_LOCALIZATION_FILE
    before = source.read_bytes()
    service._candidate_for_drafts = lambda _drafts: (
        {'localization': True}, {source: b'new source\n'}, [1],
    )
    (tmp_path / LOCALIZATION_SCRIPTS['english']).unlink()
    with pytest.raises(ValueError, match='Missing generator script'):
        service.commit_resource({}, _base(service))
    assert source.read_bytes() == before
    report = service.preview_resource_edits({}, _base(service), regenerate=False)
    assert report['generation_plan'] == {'steps': [], 'outputs': []}


def test_generation_error_keeps_report_when_rollback_is_incomplete(service, tmp_path, monkeypatch):
    from towards_victory_editor_web.services import platform
    from towards_victory_editor_web.services.generation import GenerationError

    source = wonder_localization.WONDER_LOCALIZATION_FILE
    _registry(tmp_path, ('generated/english.txt', 'generated/chinese.txt'))
    (tmp_path / LOCALIZATION_SCRIPTS['english']).write_text('raise SystemExit(8)')
    service._candidate_for_drafts = lambda _drafts: ({'localization': True}, {source: b'new\n'}, [1])
    write = platform.atomic_write_files

    def failed_restore(files):
        if source in files:
            raise PermissionError('restore denied')
        return write(files)

    monkeypatch.setattr(platform, 'atomic_write_files', failed_restore)
    with pytest.raises(platform.RollbackError) as failure:
        service.commit_resource({}, _base(service))
    original = failure.value.original
    assert isinstance(original, GenerationError)
    assert original.report['rollback']['status'] == 'incomplete'
    assert 'restore denied' in original.report['rollback']['errors'][0]
    assert 'exited with 8' in str(failure.value)
