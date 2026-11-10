"""Pydantic v2 models for Robyn HTTP validation and MCP tool schemas.

See https://robyn.tech/documentation/en/api_reference/pydantic
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from mcp_pymdurs import DEFAULT_BBOX, DEFAULT_EPSG, DEFAULT_OUTPUT_PATH, __version__

BBox = Annotated[
    list[float],
    Field(
        min_length=4,
        max_length=4,
        description="WGS84 bbox [min_lon, min_lat, max_lon, max_lat]",
    ),
]


class HealthInfo(BaseModel):
    name: str = "mcp-pymdurs"
    version: str = __version__
    mcp: str = "/mcp"
    docs: str = "https://robyn.tech/documentation/en/api_reference/mcps"
    openapi: str = "/openapi.json"
    pydantic_docs: str = "https://robyn.tech/documentation/en/api_reference/pydantic"


class DefaultsInfo(BaseModel):
    bbox: BBox = Field(default_factory=lambda: list(DEFAULT_BBOX))
    epsg: int = DEFAULT_EPSG
    output_path: str = DEFAULT_OUTPUT_PATH
    crs_note: str = (
        "bbox is WGS84 (EPSG:4326); collectors reproject to epsg (default 2154)."
    )


class BBoxAreaRequest(BaseModel):
    lat: float = Field(description="Latitude (degrees)")
    lon: float = Field(description="Longitude (degrees)")
    bbox_area: float = Field(
        gt=0,
        description="Square side length in km (mcp_pymdurs convention)",
    )


class BBoxAreaResponse(BaseModel):
    bbox: BBox


class GeometricFetchRequest(BaseModel):
    bbox: BBox = Field(default_factory=lambda: list(DEFAULT_BBOX))
    epsg: int = Field(default=DEFAULT_EPSG, description="Target CRS EPSG code")
    output_path: str = Field(
        default=DEFAULT_OUTPUT_PATH,
        description="Directory for downloaded artifacts",
    )

    @field_validator("bbox", mode="before")
    @classmethod
    def _empty_bbox_to_default(cls, value: object) -> object:
        if value is None or value == [] or value == "":
            return list(DEFAULT_BBOX)
        return value


class BuildingsFetchRequest(GeometricFetchRequest):
    as_html: bool = Field(
        default=False,
        description="If true, return Plotly HTML map instead of JSON",
    )


class LczFetchRequest(GeometricFetchRequest):
    city: str = Field(
        default="la-rochelle",
        description="City name for data.gouv LCZ zip lookup",
    )
    as_html: bool = Field(
        default=False,
        description="If true, return Plotly HTML map instead of JSON",
    )


class LczImageRequest(GeometricFetchRequest):
    """``pymdurs_lcz_to_image`` — always returns Plotly HTML."""

    city: str = Field(
        default="la-rochelle",
        description="City name for data.gouv LCZ zip lookup",
    )


class JsonResult(BaseModel):
    """Wrapper when a geometric tool returns a JSON string payload."""

    result: str


def mcp_input_schema(model: type[BaseModel]) -> dict:
    """JSON Schema for MCP ``input_schema`` (no $defs wrappers)."""
    schema = model.model_json_schema()
    # MCP tools expect a flat object schema
    schema.pop("title", None)
    return schema
