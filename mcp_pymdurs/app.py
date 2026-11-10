"""Robyn application exposing pymdurs tools over MCP HTTP JSON-RPC.

HTTP routes use Robyn's Pydantic integration:
https://robyn.tech/documentation/en/api_reference/pydantic

NOTE: do not enable ``from __future__ import annotations`` in this module —
Robyn detects BaseModel via ``inspect.signature`` and needs real classes.
"""

import json

from robyn import Robyn

from mcp_pymdurs.bbox import get_bbox_area as compute_bbox_area
from mcp_pymdurs.schemas import (
    BBoxAreaRequest,
    BBoxAreaResponse,
    BuildingsFetchRequest,
    DefaultsInfo,
    GeometricFetchRequest,
    HealthInfo,
    LczFetchRequest,
)
from mcp_pymdurs.tools import geometric, register_tools

app = Robyn(__file__)


@app.get("/")
def health() -> HealthInfo:
    return HealthInfo()


@app.get("/defaults")
def defaults() -> DefaultsInfo:
    return DefaultsInfo()


@app.post("/api/bbox")
def api_bbox(body: BBoxAreaRequest) -> BBoxAreaResponse:
    """Compute a square WGS84 bbox (Pydantic-validated body)."""
    return BBoxAreaResponse(
        bbox=compute_bbox_area(lat=body.lat, lon=body.lon, bbox_area=body.bbox_area)
    )


@app.post("/api/buildings")
def api_buildings(body: BuildingsFetchRequest) -> dict:
    result = geometric.fetch_buildings(
        bbox=body.bbox,
        epsg=body.epsg,
        output_path=body.output_path,
        as_html=body.as_html,
    )
    if body.as_html:
        return {"html": result}
    return json.loads(result)


@app.post("/api/dem")
def api_dem(body: GeometricFetchRequest) -> dict:
    return json.loads(
        geometric.fetch_dem(
            bbox=body.bbox,
            epsg=body.epsg,
            output_path=body.output_path,
        )
    )


@app.post("/api/lcz")
def api_lcz(body: LczFetchRequest) -> dict:
    result = geometric.fetch_lcz(
        bbox=body.bbox,
        city=body.city,
        epsg=body.epsg,
        output_path=body.output_path,
        as_html=body.as_html,
    )
    if body.as_html:
        return {"html": result}
    return json.loads(result)


@app.post("/api/cadastre")
def api_cadastre(body: GeometricFetchRequest) -> dict:
    return json.loads(
        geometric.fetch_cadastre(
            bbox=body.bbox,
            epsg=body.epsg,
            output_path=body.output_path,
        )
    )


@app.post("/api/roads")
def api_roads(body: GeometricFetchRequest) -> dict:
    return json.loads(
        geometric.fetch_roads(
            bbox=body.bbox,
            epsg=body.epsg,
            output_path=body.output_path,
        )
    )


@app.post("/api/water")
def api_water(body: GeometricFetchRequest) -> dict:
    return json.loads(
        geometric.fetch_water(
            bbox=body.bbox,
            epsg=body.epsg,
            output_path=body.output_path,
        )
    )


@app.mcp.resource(
    "pymdurs://defaults/bbox",
    name="default_bbox",
    description="Default WGS84 bbox (La Rochelle) and CRS used by geometric tools.",
    mime_type="application/json",
)
def default_bbox_resource() -> str:
    return DefaultsInfo().model_dump_json()


@app.mcp.prompt(
    name="urban_explore",
    description="Guide for exploring urban geometric layers with pymdurs MCP tools.",
)
def urban_explore_prompt(place: str = "La Rochelle", area_km2: float = 1.0) -> str:
    return (
        f"Explore urban data around {place} (~{area_km2} km²).\n"
        "1. Call get_bbox_area with the place centroid (lat, lon) and bbox_area.\n"
        "2. Use the returned bbox with fetch_buildings, fetch_dem, fetch_lcz, "
        "fetch_cadastre, fetch_roads, and fetch_water as needed.\n"
        "3. Prefer as_html=true, or pymdu_building_to_image / pymdu_lcz_to_image, "
        "for a map preview.\n"
        "4. Default CRS for outputs is EPSG:2154; bbox inputs remain WGS84."
    )


register_tools(app)
