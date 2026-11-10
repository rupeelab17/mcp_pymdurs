"""Locate Climate Zone dataset URL lookup on data.gouv.fr."""

from __future__ import annotations

import httpx

LCZ_DATASET_RESOURCES = (
    "https://www.data.gouv.fr/api/2/datasets/6641c562e5acdb35c0e6051d/resources"
)


def search_url_lcz(city: str) -> str:
    """Return the first LCZ zip resource URL matching ``city`` on data.gouv.fr."""
    params = {
        "type": "main",
        "page_size": 10,
        "page": 1,
        "q": city,
        "lang": "fr",
    }
    headers = {
        "content-type": "application/json",
        "User-Agent": "mcp-pymdurs/0.1 (+https://github.com/rupeelab17/pymdurs)",
    }
    with httpx.Client(follow_redirects=True, timeout=30.0) as client:
        response = client.get(LCZ_DATASET_RESOURCES, params=params, headers=headers)
        response.raise_for_status()
        payload = response.json()

    data = payload.get("data") or []
    if not data:
        raise ValueError(f"No LCZ resource found for city={city!r}")
    url = data[0].get("url")
    if not url:
        raise ValueError(f"LCZ resource for city={city!r} has no url")
    return str(url)
