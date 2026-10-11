from __future__ import annotations

import hashlib
import json
import threading
from copy import copy
from typing import Any

import scripts_engineering_department.wonder_localization_lib as localization_lib
import scripts_engineering_department.wonder_mechanics.io as wonder_io

from .common import RollingLog
from .operation_store import OperationStore
from .platform import ChangeSet, ResourceDescriptor, assert_resource_base, snapshot_files
from .wonder import localization, model, options, sources
from .wonder_commit import WonderCommit
from .wonder_preview import WonderPreview


class WonderResourceService(WonderPreview, WonderCommit, model.WonderModel):
    def __init__(self, operation_store: OperationStore | None = None) -> None:
        self.operation_store = operation_store
        self._lock = threading.RLock()
        self._log = RollingLog(max_lines=400)
        self.wonders: list[dict[str, Any]] = []
        self.mechanics: dict[str, Any] = {}
        self.wonders_data: dict[str, Any] = {}
        self.mechanics_data: dict[str, Any] = {}
        self.unique_wonders_data: dict[str, Any] = {}
        self.event_suffixes: dict[int, str] = {}
        self.localization_data: dict[str, dict[str, str]] = {}
        self.unique_ritual_designs_data: dict[str, Any] = {}
        self.unique_ritual_design_translations_data: dict[str, Any] = {}
        self.unique_ritual_prompts_data: dict[str, Any] = {}
        self.country_modifier_options: list[dict[str, Any]] = []
        self.local_modifier_options: list[dict[str, Any]] = []
        self.reward_type_options: list[dict[str, Any]] = []
        self.ceremony_cost_type_options: list[dict[str, str]] = []
        self._option_catalogs: dict[str, list[dict[str, Any]]] = {}
        self._option_catalog_version = ""
        self.reload_from_disk()
        self._log.append("[server] Wonder Localization Editor ready\n")

    @property
    def log_text(self) -> str:
        return self._log.text

    def _append_log(self, text: str) -> None:
        self._log.append(text)

    def reload_from_disk(self) -> None:
        with self._lock:
            base = snapshot_files(sources.wonder_source_paths(), repo_root=sources.REPO_ROOT)
            loaded = copy(self)
            loaded._load_from_disk()
            assert_resource_base(
                {item.path: item.sha256 for item in base},
                base,
                snapshot_files(sources.wonder_source_paths(), repo_root=sources.REPO_ROOT),
            )
            loaded._base = base
            self.__dict__.update(loaded.__dict__)

    def _load_from_disk(self) -> None:
        wonder_io.reset_cost_reward_unit_caches()
        self.wonders_data = wonder_io.load_wonders_source_data()
        self.mechanics_data = wonder_io.load_mechanics_source_data()
        self.unique_wonders_data = wonder_io.load_unique_wonders_source_data()
        self.wonders, self.mechanics = wonder_io.load_all_wonder_mechanics_data()
        self.wonders = sorted(self.wonders, key=lambda item: int(item["id"]))
        self.event_suffixes = localization_lib.load_engineering_department_suffix_map()
        self.localization_data = localization_lib.load_wonder_localization_data()
        self.unique_ritual_designs_data = sources.load_unique_ritual_designs_data()
        sources.validate_unique_ritual_designs(self.wonders, self.unique_ritual_designs_data)
        self.unique_ritual_design_translations_data = sources.load_unique_ritual_design_translations_data()
        self.unique_ritual_prompts_data = sources.load_unique_ritual_prompts_data(sources.UNIQUE_RITUAL_PROMPTS_FILE)
        (
            self.country_modifier_options,
            self.local_modifier_options,
            self.reward_type_options,
        ) = options.modifier_option_catalog(self.mechanics_data, self.unique_wonders_data)
        self.ceremony_cost_type_options = options.ceremony_stage_cost_options()
        self._option_catalogs = {
            "country_modifier": self.country_modifier_options,
            "local_modifier": self.local_modifier_options,
            "reward_type": self.reward_type_options,
            "ceremony_cost_type": self.ceremony_cost_type_options,
        }
        catalog_bytes = json.dumps(
            self._option_catalogs, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self._option_catalog_version = hashlib.sha256(catalog_bytes).hexdigest()
        localization.validate_canonical_localization_data(
            self.wonders,
            self.mechanics,
            self.event_suffixes,
            self.localization_data,
        )

    def resource_descriptor(self) -> ResourceDescriptor:
        return ResourceDescriptor(
            id="editor.wonder",
            kind="yaml_aggregate",
            label="Wonder localization and mechanics",
            source_paths=sources.wonder_source_rels(),
            generator_ids=("wonder.localization", "wonder.mechanics"),
        )

    def _resource_payload(self) -> dict[str, Any]:
        descriptor = self.resource_descriptor()
        return {
            "resource": descriptor.payload(),
            "draft": self.bootstrap_payload(),
            "change_set": ChangeSet(descriptor.id, descriptor.source_paths, self._base).payload(),
        }

    def load_resource(self) -> dict[str, Any]:
        with self._lock:
            self.reload_from_disk()
            return self._resource_payload()

    def _assert_base(self, base: dict[str, str] | None) -> None:
        current = snapshot_files(sources.wonder_source_paths(), repo_root=sources.REPO_ROOT)
        assert_resource_base(base, self._base, current)

    def validate_resource_edits(self, drafts_by_wonder_id: dict[int, dict[str, Any]]) -> dict[str, Any]:
        with self._lock:
            try:
                self._candidate_for_drafts(drafts_by_wonder_id)
            except (KeyError, RuntimeError, TypeError, ValueError) as exc:
                return {
                    "valid": False,
                    "errors": [str(exc).strip("'\"")],
                    "resource": self.resource_descriptor().payload(),
                }
            return {"valid": True, "errors": [], "resource": self.resource_descriptor().payload()}

    def bootstrap_payload(self) -> dict[str, Any]:
        with self._lock:
            wonders = self.list_wonders()
            first_wonder_id = wonders[0]["id"] if wonders else None
            return {
                "title": "Towards Victory Wonder Editor",
                "status": "Ready",
                "wonders": wonders,
                "initial_wonder_id": first_wonder_id,
                "log_text": self.log_text,
            }
