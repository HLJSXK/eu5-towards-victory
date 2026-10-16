from __future__ import annotations

import copy
import hashlib
import math
import re
import threading
from pathlib import Path
from typing import Any

from scripts_engineering_department.wonder_mechanics.io import REPO_ROOT, load_yaml

from .generator_runs import GeneratorRunService
from .operation_store import OperationStore
from .platform import (
    OperationLog,
    assert_resource_base,
    atomic_write_files,
    file_transaction,
    load_yaml_snapshots,
    run_operation,
    snapshot_files,
    yaml_bytes,
)


RESOURCE_ID = "editor.court_positions"
SCHEMA_VERSION = 1
SOURCE_REL = "data/court_positions.yaml"
SOURCE_RELS = (SOURCE_REL,)
SOURCE_FILE = REPO_ROOT / SOURCE_REL
POSITION_FIELDS = frozenset({
    "id", "name_en", "name_zh", "ability", "ability_en", "ability_zh",
    "artist_only", "modifier", "effect_at_100", "effect_en", "effect_zh",
})
ABILITIES = frozenset({"adm", "dip", "mil", "artist_skill"})
_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _source_base(base: dict[str, Any]) -> dict[str, str]:
    if not isinstance(base, dict) or not isinstance(base.get("sources"), list):
        raise ValueError("base.sources must be a list")
    sources = base["sources"]
    if len(sources) != 1 or not isinstance(sources[0], dict):
        raise ValueError("base.sources must contain exactly the court positions source")
    path, digest = sources[0].get("path"), sources[0].get("sha256")
    if not isinstance(path, str) or path.replace("\\", "/") != SOURCE_REL:
        raise ValueError(f"path_out_of_bounds: {path!r}")
    if not isinstance(digest, str) or not digest:
        raise ValueError(f"Invalid base sha256 for {path!r}")
    return {SOURCE_REL: digest}


def _source_payload(snapshots: tuple) -> list[dict[str, Any]]:
    return [{"path": item.path, "sha256": item.sha256, "size": item.size} for item in snapshots]


def _error(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _diff_values(before: Any, after: Any, field: str, output: list[dict[str, Any]]) -> None:
    if isinstance(before, dict) and isinstance(after, dict):
        for key in dict.fromkeys([*before, *after]):
            child = f"{field}.{key}" if field else str(key)
            _diff_values(before.get(key), after.get(key), child, output)
    elif isinstance(before, list) and isinstance(after, list):
        for index in range(max(len(before), len(after))):
            _diff_values(
                before[index] if index < len(before) else None,
                after[index] if index < len(after) else None,
                f"{field}[{index}]", output,
            )
    elif before != after:
        output.append({"path": SOURCE_REL, "field": field, "before": copy.deepcopy(before), "after": copy.deepcopy(after)})


class CourtPositionsEditorService:
    def __init__(self, operation_store: OperationStore | None = None, *, generator_service: GeneratorRunService | None = None) -> None:
        self.operation_store = operation_store
        self.generator_service = generator_service or GeneratorRunService(operation_store, repo_root=REPO_ROOT)
        self._lock = threading.Lock()
        self.reload_from_disk()

    def reload_from_disk(self) -> None:
        documents, self._base = load_yaml_snapshots((SOURCE_FILE,), repo_root=REPO_ROOT)
        self.data = documents[SOURCE_FILE]

    def _reward_catalog_ids(self) -> set[str]:
        try:
            catalog = load_yaml(REPO_ROOT / "data" / "cost_reward_units.yaml")
        except (OSError, TypeError, ValueError):
            return set()
        return {
            str(item["id"]) for values in catalog.values() if isinstance(values, list)
            for item in values if isinstance(item, dict) and isinstance(item.get("id"), str)
        }

    @staticmethod
    def _modifier_schema_ids() -> set[str]:
        roots = (
            REPO_ROOT / ".eu5-base" / "reference_game_files" / "game" / "main_menu" / "common" / "modifier_type_definitions",
            REPO_ROOT / ".eu5-base" / "reference_mods_variants" / "eu5-towards-victory",
        )
        result: set[str] = set()
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*.txt"):
                try:
                    text = path.read_text(encoding="utf-8-sig", errors="ignore")
                except OSError:
                    continue
                result.update(re.findall(r"(?m)^\s*([a-z][a-z0-9_]*)\s*=\s*\{", text))
        return result

    def _references(self, document: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
        catalog_ids = self._reward_catalog_ids()
        schema_ids = self._modifier_schema_ids()
        positions = document.get("positions", []) if isinstance(document, dict) else []
        keys = sorted({
            position["modifier"] for position in positions if isinstance(position, dict)
            and isinstance(position.get("modifier"), str)
        }) if isinstance(positions, list) else []
        return {"rewards": [{
            "key": key, "resolved": key in catalog_ids or key in schema_ids,
            "source_resource": "editor.cost_reward" if key in catalog_ids else "game_modifier_schema",
            "editable": False, "editable_here": False,
        } for key in keys], "tasks": []}

    def _validate_document(self, document: Any) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []
        if not isinstance(document, dict) or set(document) != {"positions"}:
            return [_error("invalid_document", "document", "Document must contain only positions.")]
        positions = document["positions"]
        if not isinstance(positions, list):
            return [_error("invalid_positions", "positions", "Positions must be a list.")]
        if len(positions) != 6:
            errors.append(_error("invalid_positions", "positions", "Exactly six launch positions are required."))
        seen: set[str] = set()
        for index, position in enumerate(positions):
            path = f"positions[{index}]"
            if not isinstance(position, dict):
                errors.append(_error("invalid_position", path, "Position must be an object."))
                continue
            if set(position) != POSITION_FIELDS:
                errors.append(_error("invalid_position_fields", path, "Position must contain exactly the declared source fields."))
            position_id = position.get("id")
            if not isinstance(position_id, str) or not _ID_RE.fullmatch(position_id):
                errors.append(_error("invalid_position_id", f"{path}.id", "Position ID must be a lowercase script identifier."))
            elif position_id in seen:
                errors.append(_error("duplicate_position_id", f"{path}.id", "Position IDs must be unique."))
            else:
                seen.add(position_id)
            for prefix in ("name", "ability", "effect"):
                if any(not isinstance(position.get(f"{prefix}_{lang}"), str) or not position[f"{prefix}_{lang}"].strip() for lang in ("en", "zh")):
                    errors.append(_error("bilingual_required", f"{path}.{prefix}", "Complete non-empty English and Chinese text is required."))
            ability = position.get("ability")
            if not isinstance(ability, str) or ability not in ABILITIES:
                errors.append(_error("invalid_ability", f"{path}.ability", "Unsupported court position ability."))
            if not isinstance(position.get("artist_only"), bool):
                errors.append(_error("invalid_boolean", f"{path}.artist_only", "Value must be true or false."))
            elif ability == "artist_skill" and not position["artist_only"]:
                errors.append(_error("invalid_artist_position", f"{path}.artist_only", "artist_skill requires artist_only=true."))
            effect = position.get("effect_at_100")
            if not isinstance(effect, (int, float)) or isinstance(effect, bool) or not math.isfinite(effect):
                errors.append(_error("invalid_number", f"{path}.effect_at_100", "Effect must be a finite number."))
            modifier = position.get("modifier")
            if not isinstance(modifier, str) or not _ID_RE.fullmatch(modifier):
                errors.append(_error("invalid_modifier", f"{path}.modifier", "Modifier must be a script identifier."))
        for reference in self._references(document)["rewards"]:
            if not reference["resolved"]:
                errors.append(_error("invalid_reward_reference", "positions.modifier", f"Unknown reward modifier reference: {reference['key']}."))
        return errors

    def _generation_plan(self, *, source_changed: bool) -> dict[str, Any]:
        errors: list[dict[str, str]] = []
        try:
            generators = self.generator_service.generators()
        except Exception as exc:
            errors.append(_error("generation_registry_incomplete", "generation", str(exc)))
            generators = []
        selected = [generator for generator in generators if set(SOURCE_RELS).intersection(
            str(value).replace("\\", "/") for value in generator.get("data_inputs", [])
        )]
        owners: dict[str, str] = {}
        outputs: set[str] = set()
        for generator in selected:
            script, declared = generator.get("script"), generator.get("outputs")
            if not isinstance(script, str) or not script:
                errors.append(_error("generation_registry_incomplete", "generation", "A matched generator is missing script."))
                continue
            if not isinstance(declared, list) or not declared:
                errors.append(_error("generation_registry_incomplete", script, "A matched generator has no outputs."))
                continue
            for output in declared:
                output = str(output).replace("\\", "/")
                if output in owners and owners[output] != script:
                    errors.append(_error("generation_output_conflict", output, f"Output is declared by both {owners[output]} and {script}."))
                owners[output] = script
                outputs.add(output)
        if not selected:
            errors.append(_error("generation_registry_incomplete", "generation", "No registered generator declares the court positions source."))
        return {
            "required": bool(source_changed and selected), "registry_complete": not errors,
            "generators": [generator["script"] for generator in selected if isinstance(generator.get("script"), str)],
            "outputs": sorted(outputs),
            "steps": [{"script": generator["script"], "outputs": sorted(generator.get("outputs", []))}
                      for generator in selected if isinstance(generator.get("script"), str)],
            "errors": errors,
        }

    def _payload(self, *, generation: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "resource_id": RESOURCE_ID, "schema_version": SCHEMA_VERSION,
            "sources": _source_payload(self._base), "document": copy.deepcopy(self.data),
            "references": self._references(self.data),
            "generation": generation or self._generation_plan(source_changed=False),
            "read_only_outputs": True,
            "constraints": {
                "yaml_write_boundary": "Preserves BOM, leading comment block and newline style; body comments are not retained and key order is not guaranteed for untouched keys.",
                "positions": "Exactly six positions; IDs are unique; abilities are adm, dip, mil or artist_skill; artist_skill requires artist_only=true.",
            },
        }

    def load_resource(self) -> dict[str, Any]:
        with self._lock:
            self.reload_from_disk()
            return self._payload()

    def _base_assert(self, base: dict[str, Any]) -> None:
        current = snapshot_files((SOURCE_FILE,), repo_root=REPO_ROOT)
        assert_resource_base(_source_base(base), self._base, current)

    def _candidate_report(self, document: dict[str, Any]) -> dict[str, Any]:
        candidate = copy.deepcopy(document)
        errors = self._validate_document(candidate)
        generation = self._generation_plan(source_changed=candidate != self.data)
        return {"candidate": candidate, "errors": [*errors, *generation["errors"]], "warnings": [], "generation": generation}

    def validate_document(self, document: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            report = self._candidate_report(document)
            return {
                "resource_id": RESOURCE_ID, "valid": not report["errors"],
                "errors": report["errors"], "warnings": report["warnings"],
                "references": self._references(report["candidate"]), "generation": report["generation"],
            }

    def preview_document(self, document: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._base_assert(base)
            report = self._candidate_report(document)
            before = SOURCE_FILE.read_bytes()
            after = yaml_bytes(SOURCE_FILE, report["candidate"])
            diff: list[dict[str, Any]] = []
            _diff_values(self.data, report["candidate"], "", diff)
            return {
                "resource_id": RESOURCE_ID, "ready": not report["errors"],
                "validation": {"errors": report["errors"], "warnings": report["warnings"]},
                "diff": {"sources": [{"path": SOURCE_REL, "changed": before != after,
                                      "before_sha256": hashlib.sha256(before).hexdigest(),
                                      "after_sha256": hashlib.sha256(after).hexdigest()}], "fields": diff},
                "written_paths": [SOURCE_REL] if before != after else [],
                "references": self._references(report["candidate"]), "generation": report["generation"],
            }

    def commit_document(self, document: dict[str, Any], base: dict[str, Any], message: str | None = None) -> dict[str, Any]:
        with self._lock:
            self._base_assert(base)
            report = self._candidate_report(document)
            if report["errors"]:
                raise ValueError("Court positions validation failed: " + "; ".join(item["message"] for item in report["errors"]))
            candidate_bytes = {SOURCE_FILE: yaml_bytes(SOURCE_FILE, report["candidate"])}
            source_files = {path: content for path, content in candidate_bytes.items() if content != path.read_bytes()}
            details: dict[str, Any] = {
                "resource_id": RESOURCE_ID, "written_paths": [],
                "generation": {"status": "not_required", "generators": report["generation"]["generators"],
                               "outputs": report["generation"]["outputs"], "artifacts": []},
                "rollback": {"status": "not_needed", "errors": []},
            }
            operation = OperationLog(
                "resource_commit", (RESOURCE_ID,), store=self.operation_store,
                snapshot_details=lambda: copy.deepcopy(details),
            )

            def execute() -> dict[str, Any]:
                try:
                    outputs = tuple(REPO_ROOT / output for output in report["generation"]["outputs"])
                    with file_transaction((*source_files, *outputs), reload=self.reload_from_disk):
                        atomic_write_files(source_files)
                        if report["generation"]["required"]:
                            generation_result = self.generator_service.run(report["generation"]["generators"])
                            details["generation"] = {
                                "status": "succeeded", "generators": report["generation"]["generators"],
                                "outputs": report["generation"]["outputs"], "artifacts": generation_result.get("artifacts", []),
                            }
                        self.reload_from_disk()
                except Exception as exc:
                    details["rollback"] = {
                        "status": "failed" if getattr(exc, "errors", None) else "completed",
                        "errors": list(getattr(exc, "errors", [])),
                    }
                    raise
                details["written_paths"] = [path.relative_to(REPO_ROOT).as_posix() for path in source_files]
                details["written_paths"].extend(
                    artifact["path"] for artifact in details["generation"]["artifacts"] if artifact["changed"]
                )
                details["written_paths"] = list(dict.fromkeys(details["written_paths"]))
                return self._payload(generation=report["generation"]) | {
                    "operation_id": operation.id, "status": "succeeded", "written_paths": details["written_paths"],
                    "generation": details["generation"], "rollback": details["rollback"],
                    "base": {"sources": _source_payload(self._base)}, "message": message,
                }

            try:
                result = run_operation(operation, execute)
            except Exception as exc:
                if hasattr(exc, "report") and isinstance(exc.report, dict):
                    exc.report["resource_id"] = RESOURCE_ID
                    exc.report["written_paths"] = details["written_paths"]
                    exc.report["rollback"] = details["rollback"]
                raise
            return {**result, "operation": operation.payload()}


def build_check_report() -> list[str]:
    service = CourtPositionsEditorService()
    resource = service.load_resource()
    validation = service.validate_document(resource["document"])
    lines = [f"[FAIL] {item['code']}: {item['message']}" for item in validation["errors"]]
    if not lines:
        lines.append(f"[PASS] court positions: {len(resource['document']['positions'])}; references resolved")
        lines.append(f"[PASS] registry-derived generation: {len(resource['generation']['generators'])} generators, {len(resource['generation']['outputs'])} outputs")
    return lines
