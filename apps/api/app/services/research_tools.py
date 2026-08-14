from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote_plus
from xml.etree import ElementTree

import httpx

from app.config import Settings


@dataclass(frozen=True)
class ToolResult:
    tool: str
    ok: bool
    records: list[dict[str, Any]]
    error: str | None = None


class AcademicTools:  # pragma: no cover - provider integration test
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def search_arxiv(self, query: str, limit: int = 5) -> ToolResult:
        url = (
            "https://export.arxiv.org/api/query?search_query=all:"
            f"{quote_plus(query)}&start=0&max_results={min(limit, 10)}"
        )
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.get(url, headers={"User-Agent": "EvidencePilotAI/1.0"})
            response.raise_for_status()
            root = ElementTree.fromstring(response.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            records = []
            for entry in root.findall("atom:entry", ns):
                link = entry.find("atom:id", ns)
                identifier = (link.text if link is not None else "").rsplit("/", 1)[-1]
                records.append(
                    {
                        "title": " ".join((entry.findtext("atom:title", "", ns)).split()),
                        "url": link.text if link is not None else None,
                        "arxiv_id": identifier,
                        "authors": [
                            author.findtext("atom:name", "", ns)
                            for author in entry.findall("atom:author", ns)
                        ],
                        "year": int(entry.findtext("atom:published", "0000", ns)[:4]),
                        "abstract": " ".join((entry.findtext("atom:summary", "", ns)).split()),
                    }
                )
            return ToolResult(tool="search_arxiv", ok=True, records=records)
        except (httpx.HTTPError, ElementTree.ParseError, ValueError) as exc:
            return ToolResult(tool="search_arxiv", ok=False, records=[], error=type(exc).__name__)

    async def search_crossref(self, query: str, limit: int = 5) -> ToolResult:
        url = f"https://api.crossref.org/works?query={quote_plus(query)}&rows={min(limit, 10)}"
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": "EvidencePilotAI/1.0 (mailto:public-demo@example.invalid)"
                    },
                )
            response.raise_for_status()
            records = []
            for item in response.json()["message"]["items"]:
                date_parts = item.get("published", {}).get("date-parts", [[0]])
                records.append(
                    {
                        "title": (item.get("title") or ["Untitled"])[0],
                        "url": item.get("URL"),
                        "doi": item.get("DOI"),
                        "authors": [
                            " ".join(filter(None, [author.get("given"), author.get("family")]))
                            for author in item.get("author", [])
                        ],
                        "year": date_parts[0][0] if date_parts and date_parts[0] else 0,
                        "publisher": item.get("publisher", "Crossref"),
                    }
                )
            return ToolResult(tool="search_crossref", ok=True, records=records)
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            return ToolResult(
                tool="search_crossref", ok=False, records=[], error=type(exc).__name__
            )


class WebSearchTool:  # pragma: no cover - provider integration test
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def search(self, query: str, limit: int = 5) -> ToolResult:
        if not self.settings.tavily_api_key:
            return ToolResult(
                tool="search_web",
                ok=False,
                records=[],
                error="Tavily is not configured; academic and cached evidence remain available.",
            )
        body = {
            "api_key": self.settings.tavily_api_key,
            "query": re.sub(r"[\x00-\x1f]", " ", query)[:500],
            "max_results": min(limit, 10),
            "search_depth": "basic",
            "include_raw_content": False,
        }
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.post("https://api.tavily.com/search", json=body)
            response.raise_for_status()
            records = [
                {
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "excerpt": result.get("content"),
                    "score": result.get("score"),
                    "accessed_at": datetime.now(UTC).isoformat(),
                }
                for result in response.json().get("results", [])
            ]
            return ToolResult(tool="search_web", ok=True, records=records)
        except (httpx.HTTPError, ValueError) as exc:
            return ToolResult(tool="search_web", ok=False, records=[], error=type(exc).__name__)
