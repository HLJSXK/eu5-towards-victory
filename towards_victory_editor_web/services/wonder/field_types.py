"""Wonder field specifications and API serialization."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import sources
from .localization import LANGUAGES, LANGUAGE_LABELS


@dataclass(slots=True)
class FieldSpec:
    key: str
    label: str
    group: str
    language: str
    file_path: Path
    original_value: str
    height: int = 3
    source_kind: str = "canonical"

    def to_api_dict(self) -> dict[str, Any]:
        origin_label = {
            "canonical": "Canonical source",
        }.get(self.source_kind, self.source_kind)
        return {
            "key": self.key,
            "label": self.label,
            "group": self.group,
            "language": self.language,
            "source_kind": self.source_kind,
            "origin_label": origin_label,
            "original_value": self.original_value,
            "value": self.original_value,
            "field_type": "text",
            "height": self.height,
            "options": [],
            "help_text": "",
        }


@dataclass(slots=True)
class MechanicsFieldSpec:
    key: str
    label: str
    group: str
    source_kind: str
    file_path: Path
    original_value: str
    field_type: str
    target_kind: str
    target_key: str
    target_parent_key: str = ""
    height: int = 3
    options: list[dict[str, Any]] = field(default_factory=list)
    help_text: str = ""
    source_path: str = ""
    target_path: str = ""
    structured_value: Any | None = None
    editable: bool = True
    prototype_key: str = ""

    def to_api_dict(self) -> dict[str, Any]:
        origin_label = {
            "shared": "Shared mechanics source",
            "generic": "Generic wonder source",
            "unique": "Unique wonder source",
        }.get(self.source_kind, self.source_kind)
        if not self.editable and self.prototype_key:
            origin_label = "Inherited from prototype"
        return {
            "key": self.key,
            "label": self.label,
            "group": self.group,
            "source_kind": self.source_kind,
            "origin_label": origin_label,
            "original_value": self.original_value,
            "value": self.original_value,
            "field_type": self.field_type,
            "target_kind": self.target_kind,
            "target_key": self.target_key,
            "target_parent_key": self.target_parent_key,
            "height": self.height,
            "options": list(self.options),
            "help_text": self.help_text,
            "source_path": self.source_path or str(self.file_path.relative_to(sources.REPO_ROOT)),
            "target_path": self.target_path,
            "structured_value": deepcopy(self.structured_value),
            "editable": self.editable,
            "prototype_key": self.prototype_key,
        }


def serialize_specs(specs: dict[str, list[FieldSpec]]) -> dict[str, dict[str, Any]]:
    payload: dict[str, dict[str, Any]] = {}
    for language in LANGUAGES:
        sections: list[dict[str, Any]] = []
        current_group: str | None = None
        current_fields: list[dict[str, Any]] = []
        for spec in specs.get(language, []):
            if spec.group != current_group:
                if current_group is not None:
                    sections.append({"group": current_group, "fields": current_fields})
                current_group = spec.group
                current_fields = []
            current_fields.append(spec.to_api_dict())
        if current_group is not None:
            sections.append({"group": current_group, "fields": current_fields})
        payload[language] = {
            "label": LANGUAGE_LABELS[language],
            "sections": sections,
        }
    return payload


def serialize_mechanics_specs(specs: list[MechanicsFieldSpec]) -> dict[str, Any]:
    sections: list[dict[str, Any]] = []
    current_group: str | None = None
    current_fields: list[dict[str, Any]] = []
    for spec in specs:
        if spec.group != current_group:
            if current_group is not None:
                sections.append({"group": current_group, "fields": current_fields})
            current_group = spec.group
            current_fields = []
        current_fields.append(spec.to_api_dict())
    if current_group is not None:
        sections.append({"group": current_group, "fields": current_fields})
    return {
        "label": "Mechanics",
        "sections": sections,
    }
