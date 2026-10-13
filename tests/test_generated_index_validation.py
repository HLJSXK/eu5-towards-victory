"""Generated index provenance and CLI/AI validation must agree."""
import json
import sys

import pytest
import yaml

from scripts import gen_index, validate


@pytest.fixture
def isolated_validator(tmp_path, monkeypatch):
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(validate, "issues", [])
    monkeypatch.setattr(validate, "warnings", [])
    (tmp_path / "data").mkdir()
    return tmp_path


def register_outputs(root, *outputs):
    (root / "data/generated_files.yaml").write_text(
        yaml.safe_dump({"generated": [
            {"script": gen_index.GENERATOR_SCRIPT, "output": output}
            for output in outputs
        ]}),
        encoding="utf-8",
    )


def test_index_writers_produce_valid_provenance_without_changing_records(isolated_validator):
    root = isolated_validator
    text_path = root / "data/index/icons.txt"
    json_path = root / "data/index/modifier_localization.json"
    gen_index._write_index(text_path, ["@b!", "@a!", "@b!"], False, "icons")
    payload = {"version": 1, "modifiers": {"monthly_political_influence": {"value_kind": "number"}}}
    gen_index._write_json_index(json_path, payload, False, "modifiers", 1)
    records = [line for line in text_path.read_text(encoding="utf-8").splitlines()
               if line and not line.startswith("#")]
    assert records == ["@a!", "@b!"]
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["modifiers"] == payload["modifiers"]
    assert payload == {key: value for key, value in loaded.items() if key != "_generated_by"}
    register_outputs(root, "data/index/icons.txt", "data/index/modifier_localization.json")
    validate.check_generated_headers()
    assert validate.issues == []


@pytest.mark.parametrize("content,suffix", [
    ("@a!\n", "txt"),
    ('{"version": 1}', "json"),
    ('{"_generated_by": "scripts/wrong.py"}', "json"),
    ('{invalid json}', "json"),
])
def test_missing_or_invalid_index_provenance_fails(isolated_validator, content, suffix):
    root = isolated_validator
    output = f"data/index.{suffix}"
    (root / output).write_text(content, encoding="utf-8")
    register_outputs(root, output)
    validate.check_generated_headers()
    assert len(validate.issues) == 1
    assert validate.issues[0].startswith("[AUTOGEN_HEADER]")


@pytest.mark.parametrize("ai_report", [False, True])
@pytest.mark.parametrize("rule", ["AUTOGEN_HEADER", "AUTOGEN"])
def test_output_modes_both_reject_generated_errors(isolated_validator, monkeypatch, capsys, ai_report, rule):
    monkeypatch.setattr(validate, "load_yaml", lambda _path: None)
    monkeypatch.setattr(validate, "load_modifier_whitelist", lambda: set())
    monkeypatch.setattr(validate, "load_hardcoded_on_actions", lambda: set())
    monkeypatch.setattr(validate, "load_warning_baseline", lambda: [])
    monkeypatch.setattr(validate, "collect_files", lambda _path: [])
    monkeypatch.setattr(sys, "argv", ["scripts/validate.py", *(["--ai-report"] if ai_report else [])])
    validate.issues.append(f"[{rule}] data/index/icons.txt missing generated provenance")
    with pytest.raises(SystemExit) as exited:
        validate.main()
    assert exited.value.code == 1
    output = capsys.readouterr().out
    if ai_report:
        report = json.loads(output)
        assert report["pass"] is False
        assert report["errors"][0]["rule"] == rule.lower()
        assert report["warnings"] == []
    else:
        assert "[FAIL]" in output
