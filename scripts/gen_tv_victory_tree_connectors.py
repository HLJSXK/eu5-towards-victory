"""
Generate victory-tree connector-line DDS overlays (one per path) from
data/victory_path_tree_variant.yaml + data/victory_tree_node_positions.yaml.

The engine's .gui widgets have no rotation/line-drawing primitive, so
prerequisite-to-node connector lines are pre-rendered here as a transparent
full-canvas overlay instead of being built from GUI widgets. The curve math
(Catmull-Rom through each chain, one smooth spline per trunk/branch — see
victory_tree_planner_web/static/app.js's catmullRomPath/drawChain/renderLinks)
and per-path line colors (PATH_LINE_COLORS in the same file) are mirrored here
so the in-game connectors match what was authored in the planner tool.

Output: src/main_menu/gfx/interface/icons/towards_victory/victory_trees/
        tv_victory_{path}_tree_connectors.dds (2048x1152, one per path)

One-off asset helper (like scripts/generate_dds_icon.py) — not registered in
data/generated_files.yaml, which only tracks script-managed src/ text files.
"""

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.dds_image_lib import RgbaImage, write_dds
from scripts.victory_tree_node_codegen import flatten_nodes, load_data
from scripts.wonder_mechanics.io import load_yaml

POSITIONS_FILE = REPO_ROOT / "data" / "victory_tree_node_positions.yaml"
OUT_DIR = REPO_ROOT / "src/main_menu/gfx/interface/icons/towards_victory/victory_trees"

IMAGE_WIDTH = 2048
IMAGE_HEIGHT = 1152
LINE_WIDTH_PX = 12
LINE_RADIUS_PX = LINE_WIDTH_PX / 2
STEP_PX = 4
LINE_ALPHA = 235

# Mirrors PATH_LINE_COLORS in victory_tree_planner_web/static/app.js.
PATH_LINE_COLORS = {
    "conquest": (0xFC, 0xA5, 0xA5),
    "prosperity": (0x86, 0xEF, 0xAC),
    "trade": (0xFC, 0xD3, 0x4D),
    "diplomatic": (0xD1, 0xD5, 0xDB),
    "cultural": (0xD8, 0xB4, 0xFE),
    "science": (0x93, 0xC5, 0xFD),
}


def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def _bezier_point(p0, p1, p2, p3, t: float) -> tuple[float, float]:
    mt = 1 - t
    x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
    y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
    return (x, y)


def catmull_rom_polyline(points: list[tuple[float, float]], step_px: float) -> list[tuple[float, float]]:
    """Port of catmullRomPath()/drawChain() in victory_tree_planner_web/static/app.js,
    expanded into a dense polyline (instead of an SVG path string) for rasterization."""
    if len(points) < 2:
        return list(points)
    if len(points) == 2:
        rough_len = _dist(points[0], points[1])
        steps = max(2, int(rough_len / step_px))
        return [
            (points[0][0] + (points[1][0] - points[0][0]) * t / steps, points[0][1] + (points[1][1] - points[0][1]) * t / steps)
            for t in range(steps + 1)
        ]

    result = [points[0]]
    n = len(points)
    for i in range(n - 1):
        p0 = points[i - 1] if i - 1 >= 0 else points[i]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[i + 2] if i + 2 < n else p2
        cp1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        cp2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        rough_len = _dist(p1, cp1) + _dist(cp1, cp2) + _dist(cp2, p2)
        steps = max(4, int(rough_len / step_px))
        for s in range(1, steps + 1):
            result.append(_bezier_point(p1, cp1, cp2, p2, s / steps))
    return result


def _stamp_circle(buf: bytearray, width: int, height: int, cx: float, cy: float, radius: float, color: tuple[int, int, int], alpha: int) -> None:
    r2 = radius * radius
    x0 = max(0, int(cx - radius))
    x1 = min(width - 1, int(cx + radius))
    y0 = max(0, int(cy - radius))
    y1 = min(height - 1, int(cy + radius))
    for y in range(y0, y1 + 1):
        dy = y - cy
        for x in range(x0, x1 + 1):
            dx = x - cx
            if dx * dx + dy * dy <= r2:
                idx = (y * width + x) * 4
                buf[idx] = color[0]
                buf[idx + 1] = color[1]
                buf[idx + 2] = color[2]
                buf[idx + 3] = alpha


def draw_chain(buf: bytearray, width: int, height: int, node_positions: dict, chain_ids: list[str], color: tuple[int, int, int]) -> None:
    points_norm = [node_positions[node_id] for node_id in chain_ids]
    points_px = [(p["x"] * width, p["y"] * height) for p in points_norm]
    if len(points_px) < 2:
        return
    polyline = catmull_rom_polyline(points_px, STEP_PX)
    for x, y in polyline:
        _stamp_circle(buf, width, height, x, y, LINE_RADIUS_PX, color, LINE_ALPHA)


def render_path_connectors(path: dict, node_positions: dict) -> RgbaImage:
    buf = bytearray(IMAGE_WIDTH * IMAGE_HEIGHT * 4)
    color = PATH_LINE_COLORS[path["id"]]

    nodes = flatten_nodes(path)
    nodes_by_id = {n["id"]: n for n in nodes}

    trunk_ids = [n["id"] for n in nodes if n["kind"] == "trunk"]
    draw_chain(buf, IMAGE_WIDTH, IMAGE_HEIGHT, node_positions, trunk_ids, color)

    for branch in path["branches"]:
        branch_node_ids = [n["id"] for n in branch["nodes"]]
        attach = branch["attach_after"]
        chain = [attach] + branch_node_ids
        draw_chain(buf, IMAGE_WIDTH, IMAGE_HEIGHT, node_positions, chain, color)

    return RgbaImage(width=IMAGE_WIDTH, height=IMAGE_HEIGHT, rgba=bytes(buf))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate positions only, do not write DDS files")
    args = parser.parse_args()

    data = load_data()
    positions = load_yaml(POSITIONS_FILE)

    for path in data["paths"]:
        pid = path["id"]
        expected_ids = {n["id"] for n in flatten_nodes(path)}
        stored = positions.get(pid, {})
        if set(stored.keys()) != expected_ids:
            missing = sorted(expected_ids - set(stored.keys()))
            extra = sorted(set(stored.keys()) - expected_ids)
            raise ValueError(f"{pid}: node id mismatch in {POSITIONS_FILE.name} (missing={missing}, extra={extra})")

    if args.check:
        print(f"[OK] {len(data['paths'])} paths validated against {POSITIONS_FILE.relative_to(REPO_ROOT)}")
        return

    for path in data["paths"]:
        pid = path["id"]
        image = render_path_connectors(path, positions[pid])
        out_path = OUT_DIR / f"tv_victory_{pid}_tree_connectors.dds"
        write_dds(image, out_path, dds_format="DXT5", overwrite=True)
        print(f"Written: {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
