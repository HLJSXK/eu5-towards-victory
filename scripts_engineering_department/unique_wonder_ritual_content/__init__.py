"""Content modules for the fully-implemented Unique Wonder Rituals.

Each module exposes a uniform contract consumed by scripts/gen_unique_wonder_rituals.py
(dedicated events/effects/triggers files) and by
scripts/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py
(the shared organization-panel GUI fragment):

- WONDER_ID, WONDER_KEY, NAME_SLUG, RUNTIME_PREFIX, IMAGE
- build_events_body() -> list[str]
- append_effects(lines), append_triggers(lines)
- append_gui(lines, indent, helpers)

Only Pharos Lighthouse and Hagia Sophia are implemented this way; every other unique
wonder (including the four formerly-bespoke Alhambra, Dome of the Rock, Bank of Saint
George, and St. Peter's Basilica) uses the generic immediate-mode ritual driven directly
by data/unique_wonders.yaml.
"""
from . import hagia, pharos

RITUAL_MODULES = (pharos, hagia)


def iter_ritual_modules():
    return iter(RITUAL_MODULES)


def append_unique_ritual_gui(lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    for module in iter_ritual_modules():
        module.append_gui(lines, indent, helpers)
