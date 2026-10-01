import shutil
from pathlib import Path

import pytest
import yaml

from towards_victory_editor_web.services.artifacts import (
    collect_artifacts, snapshot_artifacts, validate_artifact_contract,
)
from towards_victory_editor_web.services.generation import (
    GenerationError, GeneratorSpec, build_generation_plan, run_generation,
)
from towards_victory_editor_web.services.wonder_generation import wonder_generation_plan


def _workspace(root, scripts, outputs):
    (root / 'data').mkdir(exist_ok=True)
    for name, source in scripts.items():
        (root / name).write_text(source)
    (root / 'data/generated_files.yaml').write_text(yaml.safe_dump({'generated': [
        {'script': script, 'output': output}
        for script, paths in outputs.items() for output in paths
    ]}))


def test_dependency_order_and_shared_output_reports(tmp_path):
    _workspace(tmp_path, {
        'fragment.py': "from pathlib import Path; Path('fragment.gui').write_text('widget = {}')",
        'merge.py': "from pathlib import Path; Path('panel.gui').write_text(Path('fragment.gui').read_text())",
        'finish.py': "from pathlib import Path; p=Path('panel.gui'); p.write_text(p.read_text()+'\\nother = {}')",
    }, {'fragment.py': ['fragment.gui'], 'merge.py': ['panel.gui'], 'finish.py': ['panel.gui']})
    specs = (
        GeneratorSpec('finish.py', ('merge.py',), ('panel.gui',)),
        GeneratorSpec('merge.py', ('fragment.py',), ('fragment.gui',)),
        GeneratorSpec('fragment.py'),
    )
    plan = build_generation_plan(specs, ('finish.py',), repo_root=tmp_path)
    assert [step.spec.script for step in plan.steps] == ['fragment.py', 'merge.py', 'finish.py']
    assert len(plan.outputs) == 2
    logs = []
    report = run_generation(plan, log=logs.append)
    assert report['status'] == 'succeeded'
    assert all(step['status'] == 'succeeded' for step in report['steps'])
    assert len(report['artifacts']) == 2
    assert all(item['changed'] for item in report['artifacts'])
    assert report['plan']['steps'][1]['depends_on'] == ['fragment.py']
    assert all(item['valid'] for item in report['output_validation'])
    assert report['operation_id'] in ''.join(logs)
    again = run_generation(plan, log=lambda _: None)
    assert all(not item['changed'] for item in again['artifacts'])


@pytest.mark.parametrize('specs,roots,message', [
    ((GeneratorSpec('a.py', ('b.py',)), GeneratorSpec('b.py', ('a.py',))), ('a.py',), 'cycle'),
    ((GeneratorSpec('a.py', ('missing.py',)),), ('a.py',), 'Unknown generator'),
    ((GeneratorSpec('a.py'), GeneratorSpec('a.py')), ('a.py',), 'Duplicate generator'),
    ((GeneratorSpec('a.py'), GeneratorSpec('b.py')), ('a.py', 'b.py'), 'Unordered generators'),
])
def test_invalid_graph_rejected_before_execution(tmp_path, specs, roots, message):
    _workspace(tmp_path, {'a.py': 'raise AssertionError()', 'b.py': 'raise AssertionError()'},
               {'a.py': ['same.txt'], 'b.py': ['same.txt']})
    with pytest.raises(ValueError, match=message):
        build_generation_plan(specs, roots, repo_root=tmp_path)
    assert not (tmp_path / 'same.txt').exists()


def test_plan_rejects_undeclared_dependency_and_missing_input(tmp_path):
    _workspace(tmp_path, {'a.py': '', 'b.py': ''}, {'a.py': ['a.txt'], 'b.py': ['b.txt']})
    with pytest.raises(ValueError, match='Missing dependency'):
        build_generation_plan((GeneratorSpec('a.py'), GeneratorSpec('b.py', inputs=('a.txt',))),
                              ('a.py', 'b.py'), repo_root=tmp_path)
    with pytest.raises(ValueError, match='Missing generator input'):
        build_generation_plan((GeneratorSpec('a.py', inputs=('absent.txt',)),), ('a.py',), repo_root=tmp_path)


@pytest.mark.parametrize('timeout', [0, -1, float('inf'), float('nan')])
def test_plan_rejects_unbounded_or_nonpositive_timeout(tmp_path, timeout):
    _workspace(tmp_path, {'a.py': ''}, {'a.py': ['a.txt']})
    with pytest.raises(ValueError, match='timeout must be finite and positive'):
        build_generation_plan((GeneratorSpec('a.py', timeout_seconds=timeout),), ('a.py',), repo_root=tmp_path)


@pytest.mark.parametrize('source,error', [
    ('pass', 'Missing declared outputs'),
    ("from pathlib import Path; Path('a.txt').write_text('broken = {')", 'Output validation failed'),
    ("from pathlib import Path; Path('a.txt').write_text('partial = {}'); raise SystemExit(7)", 'exited with 7'),
])
def test_failure_keeps_attempted_artifacts_and_skips_dependents(tmp_path, source, error):
    _workspace(tmp_path, {'a.py': source, 'b.py': "raise AssertionError('must be skipped')"},
               {'a.py': ['a.txt'], 'b.py': ['b.txt']})
    plan = build_generation_plan((GeneratorSpec('a.py'), GeneratorSpec('b.py', ('a.py',))),
                                 ('b.py',), repo_root=tmp_path)
    with pytest.raises(GenerationError, match=error) as failure:
        run_generation(plan, log=lambda _: None)
    report = failure.value.report
    assert report['status'] == 'failed'
    assert [item['status'] for item in report['steps']] == ['failed', 'skipped']
    assert 'b.txt' in report['missing_outputs']
    assert bool(report['artifacts']) == (source != 'pass')


@pytest.mark.parametrize('name,content,valid', [
    ('a.gui', b'widget = { text = "} # {" # ignored }\n }', True),
    ('a.txt', b'a = { value = "escaped \\" quote" }', True),
    ('a.txt', b'a = {', False),
    ('a.txt', b'a = "unfinished', False),
    ('a.txt', b'}', False),
    ('a.txt', b'', False),
    ('a.txt', b'\xff', False),
    ('a_l_english.yml', '\ufeffl_english:\n key:0 "Text\\nvalue"\n'.encode(), True),
    # Literal interior quotes occur in vanilla government_l_english.yml.
    ('a_l_english.yml', '\ufeffl_english:\n key: ""L’État, c’est moi!""\n'.encode(), True),
    ('a_l_english.yml', '\ufeffl_english:\n key: "Text" # comment\n'.encode(), True),
    ('a_l_english.yml', b'l_english:\n key: "Text"\n', False),
    ('a_l_english.yml', '\ufeffl_simp_chinese:\n key: "Text"\n'.encode(), False),
    ('a.yml', '\ufeffl_english:\n key: "one"\n key: "two"\n'.encode(), False),
    ('a.yml', '\ufeffl_english:\n key: "multi\nline"\n'.encode(), False),
    ('a.yml', '\ufeffl_english:\n key: “curly”\n'.encode(), False),
    ('a.yml', '\ufeffl_english:\n key: "unfinished\n'.encode(), False),
])
def test_generated_text_contract(tmp_path, name, content, valid):
    path = tmp_path / name
    path.write_bytes(content)
    artifacts = collect_artifacts(tmp_path, {}, snapshot_artifacts((path,)))
    reports = validate_artifact_contract(tmp_path, artifacts, ('txt', 'gui', 'yml'))
    assert reports[0]['valid'] is valid


@pytest.mark.parametrize('relative', [
    'src/in_game/common/building_types/sample.txt',
    'src_engineering_department/main_menu/common/game_concepts/sample.txt',
    'src_engineering_department/in_game/events/sample.txt',
    'src_engineering_department/in_game/gui/panels/sample.gui',
])
@pytest.mark.parametrize('bom', [b'', b'\xef\xbb\xbf'])
def test_game_script_outputs_require_bom(tmp_path, relative, bom):
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_bytes(bom + b'sample = {}\n')
    artifacts = collect_artifacts(tmp_path, {}, snapshot_artifacts((path,)))
    report, = validate_artifact_contract(tmp_path, artifacts)
    assert report['valid'] is bool(bom)
    if not bom:
        assert 'UTF-8 BOM' in report['error']


def test_intermediate_gui_fragment_does_not_require_bom(tmp_path):
    # The repository's parent directory must not affect the relative-path rule.
    root = tmp_path / 'gui' / 'workspace'
    path = root / 'data/generated_fragments/sample.gui'
    path.parent.mkdir(parents=True)
    path.write_bytes(b'widget = {}\n')
    artifacts = collect_artifacts(root, {}, snapshot_artifacts((path,)))
    report, = validate_artifact_contract(root, artifacts)
    assert report['valid']


def test_real_wonder_plan_dependencies_and_current_artifacts():
    root = Path(__file__).resolve().parents[1]
    plan = wonder_generation_plan({'mechanics': True}, repo_root=root)
    by_name = {Path(step.spec.script).name: step for step in plan.steps}
    merge = by_name['merge_tv_wonder_ceremony_cards_gui.py']
    assert {Path(script).name for script in merge.spec.depends_on} == {
        'gen_tv_wonder_ceremony_cards_gui.py', 'merge_tv_engineering_department_wonder_mechanics_gui.py',
    }
    encyclopedia_merge = by_name['merge_tv_encyclopedia_wonders_cards_gui.py']
    prosper_or_perish = by_name['gen_tv_prosper_or_perish_encyclopedia_lateralview.py']
    assert prosper_or_perish.spec.depends_on == (encyclopedia_merge.spec.script,)
    assert prosper_or_perish.outputs == (
        root / 'submods/tv_prosper_or_perish_compat/in_game/gui/encyclopedia_lateralview.gui',
    )
    artifacts = collect_artifacts(root, {}, snapshot_artifacts(plan.outputs))
    assert len(artifacts) == 40
    assert all(item['valid'] for item in validate_artifact_contract(root, artifacts, ('txt', 'gui', 'yml', 'yaml')))
    assert not wonder_generation_plan({'mechanics': True}, repo_root=root, regenerate=False).steps


def test_plan_adds_downstream_consumers_of_planned_outputs(tmp_path):
    _workspace(tmp_path, {name: '' for name in ('fragment.py', 'merge.py', 'reader.py', 'other.py')}, {
        'fragment.py': ['fragment.gui'], 'merge.py': ['panel.gui'],
        'reader.py': ['report.txt'], 'other.py': ['other.txt'],
    })
    (tmp_path / 'fragment.gui').write_text('widget = {}')
    (tmp_path / 'panel.gui').write_text('widget = {}')
    specs = (
        GeneratorSpec('fragment.py'),
        GeneratorSpec('merge.py', ('fragment.py',), ('fragment.gui',)),
        GeneratorSpec('reader.py', ('merge.py',), ('panel.gui',)),
        GeneratorSpec('other.py'),
    )
    plan = build_generation_plan(specs, ('fragment.py',), repo_root=tmp_path)
    assert [step.spec.script for step in plan.steps] == ['fragment.py', 'merge.py', 'reader.py']
    # A consumer that reads a planned output without declaring the edge is
    # pulled in and then rejected instead of being silently left stale.
    with pytest.raises(ValueError, match='Missing dependency for reader.py'):
        build_generation_plan((GeneratorSpec('fragment.py'), GeneratorSpec('reader.py', inputs=('fragment.gui',))),
                              ('fragment.py',), repo_root=tmp_path)


def test_real_wonder_cost_reward_plan_selects_only_catalog_consumers():
    root = Path(__file__).resolve().parents[1]
    plan = wonder_generation_plan({'cost_reward': True}, repo_root=root)
    names = {Path(step.spec.script).name for step in plan.steps}
    assert names == {
        'gen_tv_wonder_ceremony_cost_country_modifiers.py',
        'gen_tv_wonder_ceremony_cost_local_modifiers.py',
        'gen_tv_wonder_ceremony_effects.py',
        'gen_tv_wonder_ceremony_l_english.py',
        'gen_tv_wonder_ceremony_l_simp_chinese.py',
        'gen_wonder_editor_catalog.py',
    }
    assert len(plan.outputs) == 6
    assert all('cost_reward' in step.spec.input_groups for step in plan.steps)


def test_real_wonder_source_groups_keep_shared_gui_order():
    root = Path(__file__).resolve().parents[1]
    plan = wonder_generation_plan({'unique': True}, repo_root=root)
    names = [Path(step.spec.script).name for step in plan.steps]
    assert 'gen_location_window.py' not in names
    assert names.index('gen_tv_engineering_department_wonder_mechanics_gui.py') < names.index(
        'merge_tv_engineering_department_wonder_mechanics_gui.py'
    ) < names.index('merge_tv_wonder_ceremony_cards_gui.py')
    assert names.index('gen_tv_wonder_ceremony_cards_gui.py') < names.index(
        'merge_tv_wonder_ceremony_cards_gui.py'
    )
    assert 'gen_tv_wonder_ceremony_events.py' in names

    buildings = wonder_generation_plan({}, input_groups={'mechanics.buildings'}, repo_root=root)
    building_names = {Path(step.spec.script).name for step in buildings.steps}
    assert 'gen_tv_wonder_module_buildings.py' in building_names
    assert 'gen_tv_wonder_ceremony_cost_country_modifiers.py' not in building_names
    assert 'gen_location_window.py' not in building_names
    assert any('mechanics.buildings' in step['input_groups'] for step in buildings.payload()['steps'])


def test_real_wonder_regeneration_matches_current_outputs(tmp_path):
    """Execute current generators in isolation; compare bytes with current outputs."""
    root = Path(__file__).resolve().parents[1]
    original_plan = wonder_generation_plan({'mechanics': True}, repo_root=root)
    for directory in ('data', 'scripts', 'scripts_engineering_department'):
        shutil.copytree(root / directory, tmp_path / directory,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    # Keep game text inputs without copying the large image/texture trees.
    for directory in ('src', 'src_engineering_department'):
        for source in (root / directory).rglob('*'):
            if source.is_file() and source.suffix in {'.txt', '.gui', '.yml', '.yaml', '.json'}:
                destination = tmp_path / source.relative_to(root)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
    references = {'reference_game_files/game/main_menu/gui/shared/font_icons.gui'}
    references.update(source for step in original_plan.steps for source in step.spec.inputs
                      if source.startswith('reference_'))
    for relative in references:
        destination = tmp_path / relative
        if (root / relative).is_dir():
            shutil.copytree(root / relative, destination)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / relative, destination)

    # Compare with the working tree, not HEAD: uncommitted data edits with their
    # regenerated outputs are consistent, and checkout newline conversion is not drift.
    current = {}
    for output in original_plan.outputs:
        relative = output.relative_to(root).as_posix()
        current[relative] = output.read_bytes()
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        # In-place GUI mergers need the current panel as their starting input.
        destination.write_bytes(current[relative])

    logs = []
    plan = wonder_generation_plan({'mechanics': True}, repo_root=tmp_path)
    try:
        report = run_generation(plan, log=logs.append)
    except GenerationError as exc:
        pytest.fail(f'{exc}\n' + ''.join(logs))
    assert len(report['steps']) == 41
    assert len(report['artifacts']) == len(current) == 40
    mismatches = [relative for relative, content in current.items()
                  if (tmp_path / relative).read_bytes() != content]
    assert not mismatches, f'Generated bytes differ from working tree outputs: {mismatches}'
    assert all(not artifact['changed'] for artifact in report['artifacts'])


def test_final_validation_catches_later_damage_to_declared_output(tmp_path):
    _workspace(tmp_path, {
        'a.py': "from pathlib import Path; Path('a.txt').write_text('ok = {}')",
        'b.py': "from pathlib import Path; Path('b.txt').write_text('ok = {}'); Path('a.txt').unlink()",
    }, {'a.py': ['a.txt'], 'b.py': ['b.txt']})
    plan = build_generation_plan((GeneratorSpec('a.py'), GeneratorSpec('b.py', ('a.py',))),
                                 ('b.py',), repo_root=tmp_path)
    with pytest.raises(GenerationError, match='Final output validation failed') as failure:
        run_generation(plan, log=lambda _: None)
    assert failure.value.report['missing_outputs'] == ['a.txt']
