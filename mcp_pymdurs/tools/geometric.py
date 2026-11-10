"""Core geometric fetch helpers wrapping pymdurs collectors."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp_pymdurs import DEFAULT_BBOX, DEFAULT_EPSG, DEFAULT_OUTPUT_PATH
from mcp_pymdurs.bbox import normalize_bbox
from mcp_pymdurs.plot import gdf_to_plotly_html
from mcp_pymdurs.tools.lcz_search import search_url_lcz

# Robyn MCP schemas use List/Dict; keep JSON payloads as str for large GeoJSON.


def _ensure_output(output_path: str) -> str:
    path = Path(output_path)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def _bbox_tuple(bbox: list[float]) -> tuple[float, float, float, float]:
    min_lon, min_lat, max_lon, max_lat = bbox
    return min_lon, min_lat, max_lon, max_lat


def _geojson_summary(geojson_text: str, max_chars: int = 50_000) -> dict[str, Any]:
    try:
        payload = json.loads(geojson_text)
    except json.JSONDecodeError:
        truncated = geojson_text[:max_chars]
        return {
            "feature_count": None,
            "geojson": truncated,
            "truncated": len(geojson_text) > max_chars,
        }

    features = payload.get("features") if isinstance(payload, dict) else None
    feature_count = len(features) if isinstance(features, list) else None
    text = json.dumps(payload, ensure_ascii=False)
    truncated = len(text) > max_chars
    return {
        "feature_count": feature_count,
        "geojson": text[:max_chars] if truncated else text,
        "truncated": truncated,
    }


def _pandas_to_geojson_text(df: Any) -> str:
    if hasattr(df, "to_json"):
        # GeoDataFrame
        try:
            return df.to_crs(epsg=4326).to_json()
        except Exception:
            return df.to_json()
    if isinstance(df, str):
        return df
    return json.dumps(df, default=str)


def _height_column(gdf: Any) -> str | None:
    for name in ("hauteur", "height", "H_MEDIANE", "HAUTEUR"):
        if name in gdf.columns:
            return name
    return None


def _geojson_to_gdf(geojson_data: Any, epsg: int) -> Any:
    """Build a GeoDataFrame from pymdurs get_geojson()/geojson() output."""
    import geopandas as gpd

    if isinstance(geojson_data, str):
        geojson_data = json.loads(geojson_data)
    return gpd.GeoDataFrame.from_features(geojson_data, crs=f"EPSG:{epsg}")


async def fetch_buildings(
    bbox: list[float] | None = None,
    epsg: int = DEFAULT_EPSG,
    output_path: str = DEFAULT_OUTPUT_PATH,
    as_html: bool = False,
) -> str:
    """Fetch IGN buildings for a WGS84 bbox; return JSON summary or Plotly HTML."""
    import pymdurs

    resolved = normalize_bbox(bbox, DEFAULT_BBOX)
    out = _ensure_output(output_path)
    buildings = pymdurs.geometric.Building(output_path=out)
    buildings.set_bbox(*_bbox_tuple(resolved))
    buildings.set_crs(epsg)
    buildings = buildings.run()

    # to_pandas() is attribute-only (no geometry/crs); plot via get_geojson()
    geojson = buildings.get_geojson() if hasattr(buildings, "get_geojson") else None
    if not geojson:
        geojson = _pandas_to_geojson_text(buildings.to_pandas())

    if as_html:
        gdf = _geojson_to_gdf(geojson, epsg)
        column = _height_column(gdf)
        return gdf_to_plotly_html(
            gdf, column=column, labels={column: "Hauteur"} if column else None
        )

    summary = _geojson_summary(geojson if isinstance(geojson, str) else json.dumps(geojson))
    summary.update({"bbox": resolved, "epsg": epsg, "output_path": out, "layer": "buildings"})
    return json.dumps(summary, ensure_ascii=False)


async def fetch_dem(
    bbox: list[float] | None = None,
    epsg: int = DEFAULT_EPSG,
    output_path: str = DEFAULT_OUTPUT_PATH,
) -> str:
    """Fetch DEM (MNT) for a WGS84 bbox; return TIFF / mask paths as JSON."""
    import pymdurs

    resolved = normalize_bbox(bbox, DEFAULT_BBOX)
    out = _ensure_output(output_path)
    dem = pymdurs.geometric.Dem(output_path=out)
    dem.set_bbox(*_bbox_tuple(resolved))
    dem.set_crs(epsg)
    dem = dem.run()

    tiff = dem.get_path_save_tiff() if hasattr(dem, "get_path_save_tiff") else None
    mask = dem.get_path_save_mask() if hasattr(dem, "get_path_save_mask") else None
    return json.dumps(
        {
            "bbox": resolved,
            "epsg": epsg,
            "output_path": out,
            "tiff_path": tiff,
            "mask_path": mask,
            "layer": "dem",
        },
        ensure_ascii=False,
    )


async def fetch_lcz(
    bbox: list[float] | None = None,
    city: str = "la-rochelle",
    epsg: int = DEFAULT_EPSG,
    output_path: str = DEFAULT_OUTPUT_PATH,
    as_html: bool = False,
) -> str:
    """Fetch Local Climate Zones for a city bbox; return JSON or Plotly HTML."""
    import pymdurs

    resolved = normalize_bbox(bbox, DEFAULT_BBOX)
    out = _ensure_output(output_path)
    zipfile_url = await search_url_lcz(city=city)

    lcz = pymdurs.geometric.Lcz(output_path=out)
    lcz.set_bbox(*_bbox_tuple(resolved))
    lcz.set_crs(epsg)
    lcz = lcz.run(zipfile_url=zipfile_url)

    # to_geojson() writes file / returns None; geojson() returns the FeatureCollection
    geojson_data = lcz.geojson()
    lcz_path = Path(out) / "lcz.geojson"

    if as_html:
        import geopandas as gpd

        gdf = (
            _geojson_to_gdf(geojson_data, epsg)
            if geojson_data
            else gpd.read_file(lcz_path)
        )
        table_color = lcz.get_table_color() if hasattr(lcz, "get_table_color") else None
        column = None
        color_map = None
        if table_color and "color" in gdf.columns:
            # pymdurs: {id: {"name": ..., "color": ...}}
            color_to_label = {info["color"]: info["name"] for info in table_color.values()}
            gdf = gdf.copy()
            gdf["categorie"] = gdf["color"].map(color_to_label)
            column = "categorie"
            color_map = {info["name"]: info["color"] for info in table_color.values()}
        return gdf_to_plotly_html(
            gdf,
            column=column,
            color_map=color_map,
            labels={"categorie": "Zone Climatique Locale (LCZ)"} if column else None,
        )

    if isinstance(geojson_data, str):
        geojson = geojson_data
    elif geojson_data:
        geojson = json.dumps(geojson_data)
    else:
        geojson = lcz_path.read_text(encoding="utf-8")

    summary = _geojson_summary(geojson)
    summary.update(
        {
            "bbox": resolved,
            "epsg": epsg,
            "output_path": out,
            "city": city,
            "zipfile_url": zipfile_url,
            "layer": "lcz",
        }
    )
    return json.dumps(summary, ensure_ascii=False)


async def _fetch_vector_layer(
    layer_name: str,
    collector_factory: Any,
    bbox: list[float] | None,
    epsg: int,
    output_path: str,
) -> str:
    resolved = normalize_bbox(bbox, DEFAULT_BBOX)
    out = _ensure_output(output_path)
    collector = collector_factory(output_path=out)
    collector.set_bbox(*_bbox_tuple(resolved))
    collector.set_crs(epsg)
    collector = collector.run()

    geojson = None
    if hasattr(collector, "get_geojson"):
        geojson = collector.get_geojson()
    elif hasattr(collector, "to_geojson"):
        geojson = collector.to_geojson()
    elif hasattr(collector, "to_pandas"):
        geojson = _pandas_to_geojson_text(collector.to_pandas())
    else:
        geojson = "{}"

    if not isinstance(geojson, str):
        geojson = json.dumps(geojson)

    summary = _geojson_summary(geojson)
    summary.update(
        {
            "bbox": resolved,
            "epsg": epsg,
            "output_path": out,
            "layer": layer_name,
        }
    )
    return json.dumps(summary, ensure_ascii=False)


async def fetch_cadastre(
    bbox: list[float] | None = None,
    epsg: int = DEFAULT_EPSG,
    output_path: str = DEFAULT_OUTPUT_PATH,
) -> str:
    """Fetch cadastre parcels for a WGS84 bbox."""
    import pymdurs

    return await _fetch_vector_layer(
        "cadastre",
        pymdurs.geometric.Cadastre,
        bbox,
        epsg,
        output_path,
    )


async def fetch_roads(
    bbox: list[float] | None = None,
    epsg: int = DEFAULT_EPSG,
    output_path: str = DEFAULT_OUTPUT_PATH,
) -> str:
    """Fetch IGN roads for a WGS84 bbox."""
    import pymdurs

    return await _fetch_vector_layer(
        "roads",
        pymdurs.geometric.Road,
        bbox,
        epsg,
        output_path,
    )


async def fetch_water(
    bbox: list[float] | None = None,
    epsg: int = DEFAULT_EPSG,
    output_path: str = DEFAULT_OUTPUT_PATH,
) -> str:
    """Fetch IGN water bodies for a WGS84 bbox."""
    import pymdurs

    return await _fetch_vector_layer(
        "water",
        pymdurs.geometric.Water,
        bbox,
        epsg,
        output_path,
    )
