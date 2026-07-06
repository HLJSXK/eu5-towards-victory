from . import alhambra, hagia, pharos

UNIQUE_RITUAL_PLUGINS = (pharos, hagia, alhambra)


def iter_unique_ritual_plugins():
    return iter(UNIQUE_RITUAL_PLUGINS)


def append_unique_ritual_effects(lines: list[str]) -> None:
    for plugin in iter_unique_ritual_plugins():
        plugin.append_effects(lines)


def append_unique_ritual_triggers(lines: list[str]) -> None:
    for plugin in iter_unique_ritual_plugins():
        plugin.append_triggers(lines)


def append_unique_ritual_gui(lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    for plugin in iter_unique_ritual_plugins():
        plugin.append_gui(lines, indent, helpers)
