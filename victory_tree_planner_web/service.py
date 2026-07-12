from __future__ import annotations

import sys
import threading
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from scripts.wonder_mechanics.io import REPO_ROOT, load_yaml, save_yaml_document

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from dds_image_lib import encode_png_rgba, read_dds  # noqa: E402

TREE_VARIANT_FILE = REPO_ROOT / "data" / "victory_path_tree_variant.yaml"
POSITIONS_FILE = REPO_ROOT / "data" / "victory_tree_node_positions.yaml"
POSITIONS_REL = "data/victory_tree_node_positions.yaml"

TREES_DIR = REPO_ROOT / "src/main_menu/gfx/interface/icons/towards_victory/victory_trees"
GENERATED_PREVIEWS_DIR = REPO_ROOT / "data" / "generated_tree_previews"
TREE_PREVIEW_URL_PREFIX = "/tree-previews"

# Default trunk layout: a gentle rising left-to-right S-curve (5 points),
# evoking a trunk growing upward. Values are normalized fractions of the image.
TRUNK_CURVE = (
    {"x": 0.14, "y": 0.82},
    {"x": 0.30, "y": 0.62},
    {"x": 0.50, "y": 0.50},
    {"x": 0.70, "y": 0.34},
    {"x": 0.86, "y": 0.16},
)


def _build_path_nodes(path: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten a path's trunk + branches into an ordered node list, each
    carrying id/label/kind/branch_index/parent_id. Order: trunk first, then
    branches in declared order, nodes within a branch in declared order."""
    nodes: list[dict[str, Any]] = []
    trunk_ids = [t["id"] for t in path["trunk"]]

    prev_id = None
    for t in path["trunk"]:
        nodes.append(
            {
                "id": t["id"],
                "label": f"{t['effect']} {t['value']}".strip(),
                "kind": "trunk",
                "branch_index": None,
                "parent_id": prev_id,
            }
        )
        prev_id = t["id"]

    for branch_index, branch in enumerate(path["branches"]):
        if branch["attach_after"] not in trunk_ids:
            raise ValueError(f"{path['id']}.{branch['id']}: attach_after {branch['attach_after']!r} is not a trunk node")
        prev_id = branch["attach_after"]
        for node in branch["nodes"]:
            nodes.append(
                {
                    "id": node["id"],
                    "label": f"{node['effect']} {node['value']}".strip(),
                    "kind": "branch",
                    "branch_index": branch_index,
                    "parent_id": prev_id,
                }
            )
            prev_id = node["id"]

    return nodes


def _default_positions(path: dict[str, Any]) -> dict[str, dict[str, float]]:
    positions: dict[str, dict[str, float]] = {}
    trunk_point_by_id: dict[str, dict[str, float]] = {}

    for i, t in enumerate(path["trunk"]):
        point = TRUNK_CURVE[min(i, len(TRUNK_CURVE) - 1)]
        positions[t["id"]] = {"x": point["x"], "y": point["y"]}
        trunk_point_by_id[t["id"]] = point

    # Group branches by attach point so branches sharing a trunk node fan out
    # to alternating sides instead of stacking on top of each other.
    group_index: dict[str, int] = {}
    for branch in path["branches"]:
        attach = branch["attach_after"]
        group_index[attach] = group_index.get(attach, -1) + 1
        index_in_group = group_index[attach]
        direction = 1 if index_in_group % 2 == 0 else -1
        side_spread = 1 + 0.5 * (index_in_group // 2)

        anchor = trunk_point_by_id[attach]
        node_count = len(branch["nodes"])
        for i, node in enumerate(branch["nodes"]):
            frac = (i + 1) / (node_count + 1)
            x = anchor["x"] + frac * (0.95 - anchor["x"]) * 0.75
            y = anchor["y"] + direction * side_spread * (0.09 + 0.05 * i)
            x = max(0.02, min(0.98, x))
            y = max(0.02, min(0.98, y))
            positions[node["id"]] = {"x": x, "y": y}

    return positions


class VictoryTreePlannerService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._log_lines: list[str] = []
        self.tree_variant: dict = load_yaml(TREE_VARIANT_FILE)
        self.positions: dict[str, dict[str, dict[str, float]]] = self._load_positions()
        self._ensure_tree_previews()

    def _load_positions(self) -> dict[str, dict[str, dict[str, float]]]:
        try:
            raw = load_yaml(POSITIONS_FILE)
        except FileNotFoundError:
            raw = {}
        positions: dict[str, dict[str, dict[str, float]]] = {}
        for path in self.tree_variant["paths"]:
            path_id = path["id"]
            node_ids = {n["id"] for n in _build_path_nodes(path)}
            stored = raw.get(path_id) if isinstance(raw, dict) else None
            if stored and set(stored.keys()) == node_ids:
                positions[path_id] = {
                    node_id: {"x": float(coord["x"]), "y": float(coord["y"])} for node_id, coord in stored.items()
                }
            else:
                positions[path_id] = _default_positions(path)
        return positions

    def _ensure_tree_previews(self) -> None:
        GENERATED_PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
        for dds_path in TREES_DIR.glob("*.dds"):
            png_path = GENERATED_PREVIEWS_DIR / (dds_path.stem + ".png")
            if png_path.exists() and png_path.stat().st_mtime >= dds_path.stat().st_mtime:
                continue
            image = read_dds(dds_path)
            png_path.write_bytes(encode_png_rgba(image))
            self._append_log(f"[preview] Decoded {dds_path.relative_to(REPO_ROOT)} -> {png_path.relative_to(REPO_ROOT)}\n")

    def _append_log(self, text: str) -> None:
        self._log_lines.append(text)
        del self._log_lines[:-4000]

    def bootstrap_payload(self) -> dict:
        paths = []
        for path in self.tree_variant["paths"]:
            path_id = path["id"]
            nodes = _build_path_nodes(path)
            defaults = _default_positions(path)
            for node in nodes:
                node["x"] = self.positions[path_id][node["id"]]["x"]
                node["y"] = self.positions[path_id][node["id"]]["y"]
                node["default_x"] = defaults[node["id"]]["x"]
                node["default_y"] = defaults[node["id"]]["y"]
            paths.append(
                {
                    "id": path_id,
                    "preview_url": f"{TREE_PREVIEW_URL_PREFIX}/tv_victory_{path_id}_tree.png",
                    "nodes": nodes,
                }
            )
        return {
            "paths": paths,
            "log": "".join(self._log_lines[-200:]),
        }

    def save_positions(self, edits: dict[str, dict[str, dict[str, Any]]]) -> dict:
        with self._lock:
            paths_by_id = {path["id"]: path for path in self.tree_variant["paths"]}

            for path_id, coords in edits.items():
                if path_id not in paths_by_id:
                    raise KeyError(f"Unknown victory path id: {path_id}")
                expected_ids = {n["id"] for n in _build_path_nodes(paths_by_id[path_id])}
                seen_ids = set(coords.keys())
                if seen_ids != expected_ids:
                    missing = sorted(expected_ids - seen_ids)
                    extra = sorted(seen_ids - expected_ids)
                    raise ValueError(f"{path_id}: node id mismatch (missing={missing}, extra={extra})")
                normalized = {}
                for node_id, coord in coords.items():
                    x = float(coord["x"])
                    y = float(coord["y"])
                    if not (0.0 <= x <= 1.0) or not (0.0 <= y <= 1.0):
                        raise ValueError(f"{path_id}.{node_id}: x/y must be within 0..1, got x={x}, y={y}")
                    normalized[node_id] = {"x": round(x, 4), "y": round(y, 4)}
                self.positions[path_id] = normalized

            save_yaml_document(POSITIONS_FILE, self.positions, preserve_leading_comments=True)
            self._append_log(f"[save] Wrote {POSITIONS_REL}\n")
            return self.bootstrap_payload()


def build_check_report() -> list[str]:
    lines: list[str] = []
    try:
        tree_variant = load_yaml(TREE_VARIANT_FILE)
    except Exception as exc:  # noqa: BLE001
        return [f"[FAIL] Could not load data/victory_path_tree_variant.yaml: {exc}"]

    node_ids_by_path: dict[str, set[str]] = {}
    total_nodes = 0
    for path in tree_variant["paths"]:
        try:
            nodes = _build_path_nodes(path)
        except ValueError as exc:
            lines.append(f"[FAIL] {exc}")
            continue
        node_ids_by_path[path["id"]] = {n["id"] for n in nodes}
        total_nodes += len(nodes)

    if lines:
        return lines
    lines.append(
        f"[OK] data/victory_path_tree_variant.yaml: {len(node_ids_by_path)} paths, {total_nodes} nodes total "
        f"({', '.join(f'{pid}={len(ids)}' for pid, ids in node_ids_by_path.items())})."
    )

    try:
        raw = load_yaml(POSITIONS_FILE)
    except FileNotFoundError:
        lines.append(f"[OK] {POSITIONS_REL} does not exist yet; the planner will use default layouts until first save.")
        return lines
    except Exception as exc:  # noqa: BLE001
        lines.append(f"[FAIL] Could not load {POSITIONS_REL}: {exc}")
        return lines

    total = 0
    for path_id, expected_ids in node_ids_by_path.items():
        coords = raw.get(path_id)
        if coords is None:
            lines.append(f"[FAIL] {POSITIONS_REL}: missing entry for path {path_id!r}")
            continue
        seen_ids = set(coords.keys())
        if seen_ids != expected_ids:
            missing = sorted(expected_ids - seen_ids)
            extra = sorted(seen_ids - expected_ids)
            lines.append(f"[FAIL] {path_id}: node id mismatch (missing={missing}, extra={extra})")
            continue
        for node_id, coord in coords.items():
            total += 1
            x, y = coord.get("x"), coord.get("y")
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)) or not (0 <= x <= 1) or not (0 <= y <= 1):
                lines.append(f"[FAIL] {path_id}.{node_id}: x/y must be numbers within 0..1, got x={x!r}, y={y!r}")

    if len(lines) == 1:
        lines.append(f"[OK] {POSITIONS_REL}: {total} node positions validated across {len(node_ids_by_path)} victory paths.")
    return lines
