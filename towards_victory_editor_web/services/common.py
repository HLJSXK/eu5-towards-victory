from __future__ import annotations

from typing import Callable


class RollingLog:
    """Bounded append-only text log shared by all three editor services.

    Replaces each service's previously independent `_log_lines`/`_append_log`
    (cost_reward, victory_tree) or `_log_fragments` (wonder_localization) private
    implementations, which were identical in concept but duplicated three times.
    """

    def __init__(self, max_lines: int = 4000) -> None:
        self._lines: list[str] = []
        self._max_lines = max_lines

    def append(self, text: str) -> None:
        self._lines.append(text)
        overflow = len(self._lines) - self._max_lines
        if overflow > 0:
            del self._lines[:overflow]

    def tail_text(self, count: int | None = None) -> str:
        lines = self._lines if count is None else self._lines[-count:]
        return "".join(lines)

    @property
    def text(self) -> str:
        return self.tail_text()


def safe_check(name: str, check_fn: Callable[[], list[str]]) -> list[str]:
    """Run a tool's build_check_report()-style function, normalizing any raised
    exception into a `[FAIL]` line so the combined --check report stays uniform
    even for tools (wonder_localization) whose check function raises instead of
    collecting [FAIL] strings itself.
    """
    try:
        return list(check_fn())
    except Exception as exc:  # noqa: BLE001
        return [f"[FAIL] {name}: {exc}"]
