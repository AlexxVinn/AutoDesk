"""Screen zone geometry for custom window layouts."""

from __future__ import annotations

from dataclasses import dataclass

# left, top, width, height as fractions of work area (0.0–1.0)
ZONE_FRACTIONS: dict[str, tuple[float, float, float, float]] = {
    "left": (0.0, 0.0, 0.5, 1.0),
    "right": (0.5, 0.0, 0.5, 1.0),
    "top": (0.0, 0.0, 1.0, 0.5),
    "bottom": (0.0, 0.5, 1.0, 0.5),
    "top_left": (0.0, 0.0, 0.5, 0.5),
    "top_right": (0.5, 0.0, 0.5, 0.5),
    "bottom_left": (0.0, 0.5, 0.5, 0.5),
    "bottom_right": (0.5, 0.5, 0.5, 0.5),
    "left_third": (0.0, 0.0, 0.33, 1.0),
    "center_third": (0.33, 0.0, 0.34, 1.0),
    "right_third": (0.67, 0.0, 0.33, 1.0),
    "fullscreen": (0.0, 0.0, 1.0, 1.0),
}


@dataclass
class PixelRect:
    left: int
    top: int
    width: int
    height: int


def zone_to_rect(
    zone: str,
    work_left: int,
    work_top: int,
    work_width: int,
    work_height: int,
) -> PixelRect | None:
    fractions = ZONE_FRACTIONS.get(zone)
    if not fractions:
        return None
    fx, fy, fw, fh = fractions
    w = int(work_width * fw)
    h = int(work_height * fh)
    return PixelRect(
        left=work_left + int(work_width * fx),
        top=work_top + int(work_height * fy),
        width=max(w, 100),
        height=max(h, 80),
    )


def list_zones() -> list[str]:
    return sorted(ZONE_FRACTIONS.keys())
