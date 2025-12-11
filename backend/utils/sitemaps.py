"""Helpers for building simple XML sitemaps."""

from __future__ import annotations

from typing import Iterable, Mapping, Optional


def build_sitemap_xml(urls: Iterable[Mapping[str, Optional[str]]]) -> str:
    """
    Build a minimal XML sitemap string.

    Each mapping should at least define ``loc`` and can optionally include
    ``lastmod`` (ISO 8601 string).
    """
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for url in urls:
        loc = url.get("loc")
        if not loc:
            continue
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lastmod = url.get("lastmod")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")

    lines.append("</urlset>")
    return "\n".join(lines)

