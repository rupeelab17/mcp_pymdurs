"""Register MCP tools on a Robyn app (schemas from Pydantic models)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mcp_pymdurs.bbox import get_bbox_area as compute_bbox_area
from mcp_pymdurs.schemas import (
    BBoxAreaRequest,
    BuildingsFetchRequest,
    GeometricFetchRequest,
    LczFetchRequest,
    LczImageRequest,
    mcp_input_schema,
)
from mcp_pymdurs.tools import geometric as geometric

if TYPE_CHECKING:
    from robyn import Robyn


def _parse(model: type, **kwargs: Any):
    return model.model_validate(kwargs)


def register_tools(app: Robyn) -> None:
    """Attach geometric MCP tools to ``app``."""

    @app.mcp.tool(
        name="get_bbox_area",
        description=(
            "Compute a square WGS84 bounding box [min_lon, min_lat, max_lon, max_lat] "
            "of given area (km²) centered on (lat, lon)."
        ),
        input_schema=mcp_input_schema(BBoxAreaRequest),
    )
    def get_bbox_area(lat: float, lon: float, bbox_area: float) -> list:
        req = _parse(BBoxAreaRequest, lat=lat, lon=lon, bbox_area=bbox_area)
        return compute_bbox_area(lat=req.lat, lon=req.lon, bbox_area=req.bbox_area)

    @app.mcp.tool(
        name="fetch_buildings",
        description=(
            "Fetch IGN buildings via pymdurs for a WGS84 bbox. "
            "Returns JSON summary (feature_count + geojson) or Plotly HTML when as_html=true."
        ),
        input_schema=mcp_input_schema(BuildingsFetchRequest),
    )
    def fetch_buildings(
        bbox: list | None = None,
        epsg: int | None = None,
        output_path: str | None = None,
        as_html: bool | None = None,
    ) -> str:
        payload: dict[str, Any] = {}
        if bbox is not None:
            payload["bbox"] = bbox
        if epsg is not None:
            payload["epsg"] = epsg
        if output_path is not None:
            payload["output_path"] = output_path
        if as_html is not None:
            payload["as_html"] = as_html
        req = BuildingsFetchRequest.model_validate(payload)
        return geometric.fetch_buildings(
            bbox=req.bbox,
            epsg=req.epsg,
            output_path=req.output_path,
            as_html=req.as_html,
        )

    @app.mcp.tool(
        name="fetch_dem",
        description="Fetch DEM (MNT) via pymdurs; returns JSON with TIFF/mask paths.",
        input_schema=mcp_input_schema(GeometricFetchRequest),
    )
    def fetch_dem(
        bbox: list | None = None,
        epsg: int | None = None,
        output_path: str | None = None,
    ) -> str:
        payload: dict[str, Any] = {}
        if bbox is not None:
            payload["bbox"] = bbox
        if epsg is not None:
            payload["epsg"] = epsg
        if output_path is not None:
            payload["output_path"] = output_path
        req = GeometricFetchRequest.model_validate(payload)
        return geometric.fetch_dem(
            bbox=req.bbox,
            epsg=req.epsg,
            output_path=req.output_path,
        )

    @app.mcp.tool(
        name="fetch_lcz",
        description=(
            "Fetch Local Climate Zones for a city bbox via data.gouv + pymdurs. "
            "Returns JSON summary or Plotly HTML when as_html=true."
        ),
        input_schema=mcp_input_schema(LczFetchRequest),
    )
    def fetch_lcz(
        bbox: list | None = None,
        city: str | None = None,
        epsg: int | None = None,
        output_path: str | None = None,
        as_html: bool | None = None,
    ) -> str:
        payload: dict[str, Any] = {}
        if bbox is not None:
            payload["bbox"] = bbox
        if city is not None:
            payload["city"] = city
        if epsg is not None:
            payload["epsg"] = epsg
        if output_path is not None:
            payload["output_path"] = output_path
        if as_html is not None:
            payload["as_html"] = as_html
        req = LczFetchRequest.model_validate(payload)
        return geometric.fetch_lcz(
            bbox=req.bbox,
            city=req.city,
            epsg=req.epsg,
            output_path=req.output_path,
            as_html=req.as_html,
        )

    @app.mcp.tool(
        name="fetch_cadastre",
        description="Fetch cadastre parcels via pymdurs; returns JSON summary with geojson.",
        input_schema=mcp_input_schema(GeometricFetchRequest),
    )
    def fetch_cadastre(
        bbox: list | None = None,
        epsg: int | None = None,
        output_path: str | None = None,
    ) -> str:
        payload: dict[str, Any] = {}
        if bbox is not None:
            payload["bbox"] = bbox
        if epsg is not None:
            payload["epsg"] = epsg
        if output_path is not None:
            payload["output_path"] = output_path
        req = GeometricFetchRequest.model_validate(payload)
        return geometric.fetch_cadastre(
            bbox=req.bbox,
            epsg=req.epsg,
            output_path=req.output_path,
        )

    @app.mcp.tool(
        name="fetch_roads",
        description="Fetch IGN roads via pymdurs; returns JSON summary with geojson.",
        input_schema=mcp_input_schema(GeometricFetchRequest),
    )
    def fetch_roads(
        bbox: list | None = None,
        epsg: int | None = None,
        output_path: str | None = None,
    ) -> str:
        payload: dict[str, Any] = {}
        if bbox is not None:
            payload["bbox"] = bbox
        if epsg is not None:
            payload["epsg"] = epsg
        if output_path is not None:
            payload["output_path"] = output_path
        req = GeometricFetchRequest.model_validate(payload)
        return geometric.fetch_roads(
            bbox=req.bbox,
            epsg=req.epsg,
            output_path=req.output_path,
        )

    @app.mcp.tool(
        name="fetch_water",
        description="Fetch IGN water bodies via pymdurs; returns JSON summary with geojson.",
        input_schema=mcp_input_schema(GeometricFetchRequest),
    )
    def fetch_water(
        bbox: list | None = None,
        epsg: int | None = None,
        output_path: str | None = None,
    ) -> str:
        payload: dict[str, Any] = {}
        if bbox is not None:
            payload["bbox"] = bbox
        if epsg is not None:
            payload["epsg"] = epsg
        if output_path is not None:
            payload["output_path"] = output_path
        req = GeometricFetchRequest.model_validate(payload)
        return geometric.fetch_water(
            bbox=req.bbox,
            epsg=req.epsg,
            output_path=req.output_path,
        )

    # mcp_pymdu-compatible aliases (always Plotly HTML)
    @app.mcp.tool(
        name="pymdu_building_to_image",
        description=(
            "Fetch IGN buildings and return an interactive Plotly HTML map "
            "(mcp_pymdu pymdu_building_to_image compatible)."
        ),
        input_schema=mcp_input_schema(GeometricFetchRequest),
    )
    def pymdu_building_to_image(
        bbox: list | None = None,
        epsg: int | None = None,
        output_path: str | None = None,
    ) -> str:
        payload: dict[str, Any] = {}
        if bbox is not None:
            payload["bbox"] = bbox
        if epsg is not None:
            payload["epsg"] = epsg
        if output_path is not None:
            payload["output_path"] = output_path
        req = GeometricFetchRequest.model_validate(payload)
        return geometric.fetch_buildings(
            bbox=req.bbox,
            epsg=req.epsg,
            output_path=req.output_path,
            as_html=True,
        )

    @app.mcp.tool(
        name="pymdu_lcz_to_image",
        description=(
            "Fetch Local Climate Zones and return an interactive Plotly HTML map "
            "(mcp_pymdu pymdu_lcz_to_image compatible)."
        ),
        input_schema=mcp_input_schema(LczImageRequest),
    )
    def pymdu_lcz_to_image(
        bbox: list | None = None,
        city: str | None = None,
        epsg: int | None = None,
        output_path: str | None = None,
    ) -> str:
        payload: dict[str, Any] = {}
        if bbox is not None:
            payload["bbox"] = bbox
        if city is not None:
            payload["city"] = city
        if epsg is not None:
            payload["epsg"] = epsg
        if output_path is not None:
            payload["output_path"] = output_path
        req = LczImageRequest.model_validate(payload)
        return geometric.fetch_lcz(
            bbox=req.bbox,
            city=req.city,
            epsg=req.epsg,
            output_path=req.output_path,
            as_html=True,
        )
