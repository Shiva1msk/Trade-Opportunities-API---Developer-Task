import asyncio
import logging
import re
import urllib.parse

import httpx

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


async def search_duckduckgo(query: str, max_results: int = 5) -> list[dict]:
    """Scrape DuckDuckGo HTML search results."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    try:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text

        # Extract result snippets from DDG HTML
        results = []
        # Match result blocks: title and snippet
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        urls = re.findall(r'class="result__url"[^>]*>(.*?)</span>', html, re.DOTALL)

        for i in range(min(len(titles), len(snippets), max_results)):
            title = re.sub(r"<[^>]+>", "", titles[i]).strip()
            snippet = re.sub(r"<[^>]+>", "", snippets[i]).strip()
            link = urls[i].strip() if i < len(urls) else ""
            if title and snippet:
                results.append({"title": title, "snippet": snippet, "url": link})

        logger.info(f"DDG returned {len(results)} results for: {query!r}")
        return results

    except Exception as e:
        logger.warning(f"DuckDuckGo search failed for '{query}': {e}")
        return []


async def collect_sector_data(sector: str) -> dict:
    """Run parallel searches to gather market intelligence for the sector."""
    queries = [
        f"{sector} sector India trade opportunities 2025",
        f"India {sector} exports imports market trends 2025",
        f"{sector} industry India government policy PLI FDI",
        f"{sector} India market growth challenges risks",
    ]

    tasks = [search_duckduckgo(q) for q in queries]
    results_list = await asyncio.gather(*tasks, return_exceptions=True)

    aggregated: list[dict] = []
    for i, results in enumerate(results_list):
        if isinstance(results, Exception):
            logger.warning(f"Query {i} failed: {results}")
            continue
        aggregated.extend(results)

    # Deduplicate by URL
    seen: set[str] = set()
    unique: list[dict] = []
    for item in aggregated:
        key = item.get("url", item.get("snippet", ""))[:80]
        if key not in seen:
            seen.add(key)
            unique.append(item)

    logger.info(f"Collected {len(unique)} unique data points for sector '{sector}'")
    return {"sector": sector, "queries": queries, "results": unique}
