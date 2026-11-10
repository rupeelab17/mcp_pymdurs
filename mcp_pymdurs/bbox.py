"""Bounding-box helpers (WGS84)."""

from __future__ import annotations

import math


def get_bbox_area(lat: float, lon: float, bbox_area: float) -> list[float]:
    """Return a square bbox `[min_lon, min_lat, max_lon, max_lat]` of given area (km²).

    Centered on ``(lat, lon)`` in decimal degrees. ``bbox_area`` is interpreted as
    the side length in km of a square (same convention as mcp_pymdu).
    """
    earth_radius_km = 6371.0
    half_side = bbox_area / 2.0

    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    delta_lat = half_side / earth_radius_km
    delta_lon = half_side / (earth_radius_km * math.cos(lat_rad))

    min_lat = math.degrees(lat_rad - delta_lat)
    max_lat = math.degrees(lat_rad + delta_lat)
    min_lon = math.degrees(lon_rad - delta_lon)
    max_lon = math.degrees(lon_rad + delta_lon)

    return [min_lon, min_lat, max_lon, max_lat]


def normalize_bbox(bbox: list[float] | None, default: list[float]) -> list[float]:
    """Validate and return a 4-float bbox, or ``default`` when ``bbox`` is None/empty."""
    if not bbox:
        return list(default)
    if len(bbox) != 4:
        raise ValueError("bbox must be [min_lon, min_lat, max_lon, max_lat]")
    return [float(v) for v in bbox]
