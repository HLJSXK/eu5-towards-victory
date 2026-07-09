"""Content modules for the 6 fully-implemented Unique Wonder Rituals.

Each module exposes a uniform contract consumed by scripts/gen_unique_wonder_rituals.py
(dedicated events/effects/triggers/localization files) and by
scripts/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py
(the shared organization-panel GUI fragment):

- WONDER_ID, WONDER_KEY, NAME_SLUG, RUNTIME_PREFIX, IMAGE
- build_events_body() -> list[str]
- append_effects(lines), append_triggers(lines)
- append_gui(lines, indent, helpers)

This replaces the retired scripts/wonder_unique_rituals/ package (hardcoded
Pharos/Hagia plugins merged into shared engineering-department files),
scripts/gen_repeated_row_pilot_wonders.py (Dome of the Rock / Bank of Saint
George / St. Peter's Basilica generic row-set skeleton), and the Alhambra-only
`gen_unique_wonder_ritual_code.py --write-alhambra-source` Harness vertical
slice with one consistent pipeline.
"""
from . import alhambra, bank_of_saint_george, dome_of_the_rock, hagia, pharos, st_peters_basilica

RITUAL_MODULES = (pharos, hagia, alhambra, dome_of_the_rock, bank_of_saint_george, st_peters_basilica)


def iter_ritual_modules():
    return iter(RITUAL_MODULES)


def append_unique_ritual_gui(lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    for module in iter_ritual_modules():
        module.append_gui(lines, indent, helpers)
