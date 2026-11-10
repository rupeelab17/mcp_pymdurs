"""Plotly HTML helpers for GeoDataFrames."""

from __future__ import annotations

from typing import Any

from geopandas import GeoDataFrame


def gdf_to_plotly_html(
    gdf: GeoDataFrame,
    column: str | None = None,
    color_map: dict[str, str] | None = None,
    labels: dict[str, str] | None = None,
    zoom: int = 13,
) -> str:
    """Convert a GeoDataFrame to an interactive Plotly Mapbox choropleth HTML snippet."""
    import plotly.express as px

    plot_gdf = gdf
    if plot_gdf.crs is not None and plot_gdf.crs.to_epsg() != 4326:
        plot_gdf = plot_gdf.to_crs(epsg=4326)

    minx, miny, maxx, maxy = plot_gdf.total_bounds
    center_lon = float((minx + maxx) / 2)
    center_lat = float((miny + maxy) / 2)

    kwargs: dict[str, Any] = {
        "geojson": plot_gdf.geometry,
        "locations": plot_gdf.index,
        "center": {"lat": center_lat, "lon": center_lon},
        "map_style": "carto-positron",
        "zoom": zoom,
        "opacity": 0.7,
    }
    if column is not None:
        kwargs["color"] = column
    if color_map is not None:
        kwargs["color_discrete_map"] = color_map
    if labels is not None:
        kwargs["labels"] = labels

    fig = px.choropleth_map(plot_gdf, **kwargs)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig.to_html(full_html=False, include_plotlyjs="cdn")
