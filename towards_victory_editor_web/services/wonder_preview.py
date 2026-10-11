from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from . import wonder_localization as domain
from .platform import ChangeSet, repo_relative_path, source_text_bytes, yaml_bytes
from .wonder_generation import wonder_generation_plan


def source_fields(path, data):
    """Yield semantic source fields, keeping each structured editor value whole."""
    if path == domain.WONDER_LOCALIZATION_FILE:
        for language, values in data['wonder_localization'].items():
            for key, value in values.items():
                yield ('localization', language, '', key), value
    elif path in (domain.WONDERS_FILE, domain.UNIQUE_WONDERS_FILE, domain.UNIQUE_RITUAL_PROMPTS_FILE):
        root = 'wonders' if path == domain.WONDERS_FILE else 'unique_wonders'
        scope = 'ritual_prompt' if path == domain.UNIQUE_RITUAL_PROMPTS_FILE else 'mechanics'
        for entry in data[root]:
            for field, value in entry.items():
                yield (scope, '', entry['key'], field), value
    else:
        for group, entries in data.items():
            for key, value in entries.items():
                if group == 'base_modifiers':
                    yield ('mechanics', '', key, group), value
                else:
                    for field, item in value.items():
                        yield ('mechanics', '', key, f'{group}.{field}'), item


def field_diff(service, files, drafts):
    owners = {}
    for wonder_id, draft in drafts.items():
        if draft.get('values'):
            wonder = service._get_wonder(wonder_id)
            for language, specs in service._build_specs_for_wonder(wonder).items():
                for spec in specs:
                    owners[(language, spec.key)] = wonder
    wonders = {wonder['key']: wonder for wonder in service.wonders}
    result = []
    for path, content in files.items():
        before = dict(source_fields(path, yaml.safe_load(path.read_bytes()))) if path.exists() else {}
        after = dict(source_fields(path, yaml.safe_load(content)))
        for identity in sorted(before.keys() | after.keys()):
            old, new = before.get(identity), after.get(identity)
            if identity in before and identity in after and json.dumps(old, sort_keys=True) == json.dumps(new, sort_keys=True):
                continue
            scope, language, key, field = identity
            wonder = owners.get((language, field), wonders.get(key, {}))
            value = new if identity in after else old
            result.append({
                'kind': 'field', 'path': repo_relative_path(path, domain.REPO_ROOT),
                'wonder_id': wonder.get('id'), 'wonder_key': wonder.get('key', key),
                'scope': scope, 'language': language or None, 'field': field,
                'value_kind': 'structure' if isinstance(value, (dict, list)) else
                              'script' if field.endswith('_script') else
                              'text' if isinstance(value, str) else 'scalar',
                'before': old, 'after': new,
                'before_present': identity in before, 'after_present': identity in after,
            })
    return result


class WonderPreview:
    @staticmethod
    def _localization_bytes(path: Path, localization: dict[str, dict[str, str]]) -> bytes:
        canonical = domain.collapse_wonder_localization_data(deepcopy(localization))
        payload = {"wonder_localization": {language: dict(canonical[language]) for language in domain.LANGUAGES}}
        text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, default_flow_style=False)
        return source_text_bytes(path, text)

    def _candidate_source_bytes(self, changed: dict[str, bool]) -> dict[Path, bytes]:
        files: dict[Path, bytes] = {}
        if changed["localization"]:
            files[domain.WONDER_LOCALIZATION_FILE] = self._localization_bytes(
                domain.WONDER_LOCALIZATION_FILE, self.localization_data
            )
        if changed["mechanics"]:
            files.update(
                {
                    domain.WONDER_FINAL_BUILDINGS_FILE: yaml_bytes(
                        domain.WONDER_FINAL_BUILDINGS_FILE, {"buildings": self.mechanics_data.get("buildings", {})}
                    ),
                    domain.WONDER_GENERIC_RITUALS_FILE: yaml_bytes(
                        domain.WONDER_GENERIC_RITUALS_FILE, {"generic_rituals": self.mechanics_data.get("generic_rituals", {})}
                    ),
                    domain.WONDER_BASE_MODIFIERS_FILE: yaml_bytes(
                        domain.WONDER_BASE_MODIFIERS_FILE, {"base_modifiers": self.mechanics_data.get("base_modifiers", {})}
                    ),
                    domain.WONDER_SITE_RULES_FILE: yaml_bytes(
                        domain.WONDER_SITE_RULES_FILE, {"site_rules": self.mechanics_data.get("site_rules", {})}
                    ),
                }
            )
        if changed["wonders"]:
            files[domain.WONDERS_FILE] = yaml_bytes(domain.WONDERS_FILE, self.wonders_data)
        if changed["unique"]:
            files[domain.UNIQUE_WONDERS_FILE] = yaml_bytes(domain.UNIQUE_WONDERS_FILE, self.unique_wonders_data)
        if changed["prompts"]:
            files[domain.UNIQUE_RITUAL_PROMPTS_FILE] = yaml_bytes(
                domain.UNIQUE_RITUAL_PROMPTS_FILE, self.unique_ritual_prompts_data
            )
        return {
            path: content
            for path, content in files.items()
            if not path.exists() or path.read_bytes() != content
        }

    def _candidate_for_drafts(self, drafts_by_wonder_id: dict[int, dict[str, Any]]) -> tuple[dict, dict[Path, bytes], list[int]]:
        changed = {
            "localization": False,
            "mechanics": False,
            "wonders": False,
            "unique": False,
            "prompts": False,
        }
        changed_wonder_ids: list[int] = []
        state_attrs = (
            "wonders_data",
            "mechanics_data",
            "unique_wonders_data",
            "localization_data",
            "unique_ritual_prompts_data",
        )
        original = {name: getattr(self, name) for name in state_attrs}
        for name, value in original.items():
            setattr(self, name, deepcopy(value))
        try:
            for wonder_id, draft in sorted(drafts_by_wonder_id.items(), key=lambda item: int(item[0])):
                page_changes = self._apply_wonder_edits(
                    int(wonder_id), draft.get("values", {}), draft.get("mechanics", {})
                )
                prompt_changed = (
                    self._apply_ritual_prompt_edit(int(wonder_id), draft["ritual_prompt"])
                    if "ritual_prompt" in draft
                    else False
                )
                if any(page_changes.values()) or prompt_changed:
                    changed_wonder_ids.append(int(wonder_id))
                for key, value in page_changes.items():
                    changed[key] = changed[key] or value
                changed["prompts"] = changed["prompts"] or prompt_changed
            if changed["localization"]:
                domain.validate_canonical_localization_data(
                    self.wonders, self.mechanics, self.event_suffixes, self.localization_data
                )
            files = self._candidate_source_bytes(changed)
            return changed, files, changed_wonder_ids
        finally:
            for name, value in original.items():
                setattr(self, name, value)

    def preview_resource_edits(
        self, drafts_by_wonder_id: dict[int, dict[str, Any]], base: dict[str, str] | None = None,
        *, regenerate: bool = True,
    ) -> dict[str, Any]:
        with self._lock:
            self._assert_base(base)
            changed, files, _ = self._candidate_for_drafts(drafts_by_wonder_id)
            groups = domain._wonder_input_groups(files)
            plan = wonder_generation_plan(
                changed if files else {}, repo_root=domain.REPO_ROOT, regenerate=regenerate,
                input_groups=groups,
            )
            before = {item.path: item.sha256 for item in self._base}
            file_diff = [
                {
                    "kind": "file",
                    "path": repo_relative_path(path, domain.REPO_ROOT),
                    "before": before.get(repo_relative_path(path, domain.REPO_ROOT), "missing"),
                    "after": hashlib.sha256(content).hexdigest(),
                }
                for path, content in files.items()
                if before.get(repo_relative_path(path, domain.REPO_ROOT), "missing")
                != hashlib.sha256(content).hexdigest()
            ]
            diff = field_diff(self, files, drafts_by_wonder_id)
            self._assert_base(base)
            return {
                "valid": True,
                "errors": [],
                "diff": diff,
                "file_diff": file_diff,
                "generation_plan": plan.payload(),
                "change_set": ChangeSet(
                    self.resource_descriptor().id, self.resource_descriptor().source_paths, self._base
                ).payload(),
            }
