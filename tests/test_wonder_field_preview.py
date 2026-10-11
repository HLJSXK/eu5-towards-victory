"""Preview actual normalized candidate sources, without writing project data."""
from copy import copy, deepcopy
import hashlib
import json
import shutil

import pytest
import yaml

from towards_victory_editor_web.services import wonder_localization as domain
from towards_victory_editor_web.services.platform import snapshot_files
from towards_victory_editor_web.services.wonder_resource import WonderResourceService


@pytest.fixture(scope="module")
def loaded():
    return WonderResourceService()


@pytest.fixture
def service(loaded, tmp_path, monkeypatch):
    service = copy(loaded)
    for name in ('WONDER_LOCALIZATION_FILE', 'WONDER_FINAL_BUILDINGS_FILE', 'WONDER_GENERIC_RITUALS_FILE',
                 'WONDER_BASE_MODIFIERS_FILE', 'WONDER_SITE_RULES_FILE', 'WONDERS_FILE',
                 'UNIQUE_WONDERS_FILE', 'UNIQUE_RITUAL_PROMPTS_FILE'):
        old = getattr(domain, name)
        path = tmp_path / 'data' / old.name
        path.parent.mkdir(exist_ok=True)
        shutil.copyfile(old, path)
        monkeypatch.setattr(domain, name, path)
    monkeypatch.setattr(domain, 'REPO_ROOT', tmp_path)
    service._base = snapshot_files(domain._wonder_source_paths(), repo_root=tmp_path)
    return service


def preview(service, drafts):
    base = {item.path: item.sha256 for item in service._base}
    disk = {path: path.read_bytes() for path in domain._wonder_source_paths()}
    original = deepcopy((service.wonders_data, service.mechanics_data, service.unique_wonders_data,
                         service.localization_data, service.unique_ritual_prompts_data))
    result = service.preview_resource_edits(drafts, base, regenerate=False)
    assert disk == {path: path.read_bytes() for path in disk}
    assert original == (service.wonders_data, service.mechanics_data, service.unique_wonders_data,
                        service.localization_data, service.unique_ritual_prompts_data)
    assert result['generation_plan']['steps'] == []
    return result


def test_localization_diff_has_wonder_language_and_normalized_written_value(service):
    wonder = service.wonders[0]
    key = domain.wonder_name_key(wonder)
    report = preview(service, {wonder['id']: {'values': {
        'english': {key: '  Changed\r\nname  '}, 'simp_chinese': {key: '新名称'},
    }}})
    rows = report['diff']
    assert len(rows) == 2
    for row in rows:
        assert row['wonder_id'] == wonder['id']
        assert row['wonder_key'] == wonder['key']
        assert row['field'] == key
        assert row['scope'] == 'localization'
        assert row['before'] == service.localization_data[row['language']][key]
    assert {r['language']: r['after'] for r in rows} == {'english': 'Changed name', 'simp_chinese': '新名称'}


def test_multiple_wonder_edits_keep_distinct_identity(service):
    wonders = service.wonders[:2]
    report = preview(service, {w['id']: {'values': {'english': {domain.wonder_name_key(w): 'Changed ' + w['key']}}} for w in wonders})
    assert {r['wonder_id'] for r in report['diff']} == {w['id'] for w in wonders}


def test_structure_diff_uses_source_mapping_without_editor_options(service):
    wonder = next(w for w in service.wonders if not w['is_unique'])
    spec = next(s for s in service._build_mechanics_specs_for_wonder(wonder) if s.target_kind == 'base_modifiers')
    editor_value = json.loads(spec.original_value)
    editor_value['rows'][0]['value'] = '0.12345'
    report = preview(service, {wonder['id']: {'mechanics': {spec.key: json.dumps(editor_value)}}})
    row = next(r for r in report['diff'] if r['field'] == 'base_modifiers')
    assert row['value_kind'] == 'structure'
    assert row['before'] == service.mechanics_data['base_modifiers'][spec.target_key]
    assert row['after'] == domain.mapping_from_modifier_rows(json.dumps(editor_value), context=spec.key)
    assert 'options' not in json.dumps(row)


def test_prototype_selection_reports_both_written_source_fields(service):
    wonder = next(w for w in service.wonders if w['is_unique'])
    prototype = next(w for w in service.wonders if not w['is_unique'] and w['key'] != wonder['base_key'])
    spec = next(s for s in service._build_mechanics_specs_for_wonder(wonder) if s.target_kind == 'unique_prototype')
    report = preview(service, {wonder['id']: {'mechanics': {spec.key: prototype['key']}}})
    assert {r['field']: r['after'] for r in report['diff']} == {'base_key': prototype['key'], 'mechanic_key': prototype['key']}


def test_prompt_multiline_and_clear_distinguish_missing_from_empty(service):
    wonder = next(w for w in service.wonders if w['is_unique'])
    report = preview(service, {wonder['id']: {'ritual_prompt': '  First\r\nSecond  '}})
    row = next(r for r in report['diff'] if r['field'] == 'prompt')
    assert row['after'] == 'First\nSecond'
    assert row['value_kind'] == 'text'
    assert row['scope'] == 'ritual_prompt'
    # Install the candidate only in this test's temporary source.
    _, files, _ = service._candidate_for_drafts({wonder['id']: {'ritual_prompt': 'First\nSecond'}})
    for path, content in files.items():
        path.write_bytes(content)
    service.unique_ritual_prompts_data = yaml.safe_load(domain.UNIQUE_RITUAL_PROMPTS_FILE.read_bytes())
    service._base = snapshot_files(domain._wonder_source_paths(), repo_root=domain.REPO_ROOT)
    cleared = preview(service, {wonder['id']: {'ritual_prompt': ''}})
    row = next(r for r in cleared['diff'] if r['field'] == 'prompt')
    assert row['before'] == 'First\nSecond'
    assert row['after_present'] is False


def test_normalized_noop_has_no_field_or_file_diff(service):
    wonder = service.wonders[0]
    key = domain.wonder_name_key(wonder)
    report = preview(service, {wonder['id']: {'values': {'english': {key: '  ' + service.localization_data['english'][key] + '  '}}}})
    assert report['diff'] == report['file_diff'] == []


def test_preview_matches_commit_file_bytes_and_values(service):
    wonder = service.wonders[0]
    key = domain.wonder_name_key(wonder)
    drafts = {wonder['id']: {'values': {'english': {key: '  Committed\nname  '}}}}
    report = preview(service, drafts)
    base = {item.path: item.sha256 for item in service._base}
    # This check isolates source serialization/transaction from detail generation.
    service.reload_from_disk = lambda: setattr(service, '_base', snapshot_files(domain._wonder_source_paths(), repo_root=domain.REPO_ROOT))
    service.get_wonder_payload = lambda _id: None
    service.commit_resource(drafts, base, regenerate=False)
    for row in report['file_diff']:
        path = domain.REPO_ROOT / row['path']
        assert row['kind'] == 'file'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['after']
    saved = yaml.safe_load(domain.WONDER_LOCALIZATION_FILE.read_bytes())
    assert saved['wonder_localization']['english'][key] == report['diff'][0]['after'] == 'Committed name'
