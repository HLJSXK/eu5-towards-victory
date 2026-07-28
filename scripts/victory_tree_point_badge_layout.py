"""Shared placement data for the Victory Path tree-point badge UI.

The baked 2048x1152 background circles and the in-game tree use this 508px
layout. Keep the requested route/corner order in one place so the displayed
number remains centred in its matching artwork.
"""

from __future__ import annotations


TREE_BACKGROUND_WIDTH = 508
TREE_BACKGROUND_HEIGHT = round(TREE_BACKGROUND_WIDTH * 1152 / 2048)

TREE_POINT_BADGE_SIZE = 88
TREE_POINT_BADGE_MARGIN = 8

# Per-route adjustments to the requested corner position, in in-game UI px.
TREE_POINT_BADGE_OFFSETS = {
    "prosperity": (-70, 0),
    "cultural": (150, 0),
}

# Requested order: bottom-right, top-right, top-left, bottom-left,
# bottom-left, bottom-right.
TREE_POINT_BADGE_CORNERS = {
    "conquest": "bottom_right",
    "prosperity": "top_right",
    "trade": "top_left",
    "diplomatic": "bottom_left",
    "cultural": "bottom_left",
    "science": "bottom_right",
}


def badge_position(path_id: str) -> tuple[int, int]:
    """Return the top-left UI position for a route's tree-point badge."""
    corner = TREE_POINT_BADGE_CORNERS[path_id]
    x = TREE_POINT_BADGE_MARGIN if corner.endswith("left") else TREE_BACKGROUND_WIDTH - TREE_POINT_BADGE_SIZE - TREE_POINT_BADGE_MARGIN
    y = TREE_POINT_BADGE_MARGIN if corner.startswith("top") else TREE_BACKGROUND_HEIGHT - TREE_POINT_BADGE_SIZE - TREE_POINT_BADGE_MARGIN
    offset_x, offset_y = TREE_POINT_BADGE_OFFSETS.get(path_id, (0, 0))
    return x + offset_x, y + offset_y
