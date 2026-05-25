"""Unified search provider abstraction — Tavily, DuckDuckGo, Brave, SerpAPI, SearXNG."""

from __future__ import annotations

from typing import Optional

from utils.logger import logger

PROVIDERS = {
    "tavily":       "Tavily",
    "duckduckgo":   "DuckDuckGo",
    "brave":        "Brave Search",
    "serpapi":      "SerpAPI",
    "searxng":      "SearXNG",
}


def _get_provider_config() -> dict:
    """Read current search provider config from session state / env."""
    cfg: dict = {"provider": "tavily"}
    try:
        import streamlit as st
        cfg["provider"] = st.session_state.get("search_provider", "tavily")
        for key in ("tavily_api_key", "brave_api_key", "serpapi_api_key",
                     "searxng_base_url"):
            cfg[key] = st.session_state.get(key, "")
    except Exception:
        pass
    return cfg


def _search_tavily(query: str, cfg: dict, max_results: int = 10,
                   domains: Optional[list[str]] = None, **kwargs) -> list[dict]:
    from tavily import TavilyClient
    client = TavilyClient(api_key=cfg["tavily_api_key"])
    params = dict(
        query=query,
        search_depth=kwargs.get("search_depth", "advanced"),
        max_results=max_results,
        include_answer=kwargs.get("include_answer", False),
        include_raw_content=True,
        topic=kwargs.get("topic", "news"),
        days=kwargs.get("days", 7),
    )
    if domains:
        params["include_domains"] = domains
    resp = client.search(**params)
    return resp.get("results", [])


def _search_duckduckgo(query: str, cfg: dict, max_results: int = 10,
                        domains: Optional[list[str]] = None, **kwargs) -> list[dict]:
    # DuckDuckGo does not support domain filtering via site: syntax — it causes timeouts.
    # Domains are ignored for this provider.
    results = []
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "content": r.get("body", ""),
                    "source": "",
                })
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")
        raise RuntimeError(f"DuckDuckGo: {e}") from e
    return results


def _search_brave(query: str, cfg: dict, max_results: int = 10,
                  domains: Optional[list[str]] = None, **kwargs) -> list[dict]:
    import requests
    api_key = cfg.get("brave_api_key", "")
    if not api_key:
        logger.warning("Brave Search API key not configured")
        return []
    # Brave supports site: operator in query for domain filtering
    if domains:
        site_filter = " OR ".join(f"site:{d}" for d in domains)
        query = f"{query} ({site_filter})"
    headers = {"Accept": "application/json", "Accept-Encoding": "gzip",
               "X-Subscription-Token": api_key}
    params = {"q": query, "count": min(max_results, 20)}
    try:
        resp = requests.get("https://api.search.brave.com/res/v1/web/search",
                           headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for r in data.get("web", {}).get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("description", ""),
                "source": "",
            })
        return results
    except Exception as e:
        logger.warning(f"Brave search failed: {e}")
        return []


def _search_serpapi(query: str, cfg: dict, max_results: int = 10,
                    domains: Optional[list[str]] = None, **kwargs) -> list[dict]:
    import requests
    api_key = cfg.get("serpapi_api_key", "")
    if not api_key:
        logger.warning("SerpAPI key not configured")
        return []
    # SerpAPI passes query through to Google, which supports site: operator
    if domains:
        site_filter = " OR ".join(f"site:{d}" for d in domains)
        query = f"{query} ({site_filter})"
    params = {"q": query, "api_key": api_key, "engine": "google", "num": max_results}
    try:
        resp = requests.get("https://serpapi.com/search", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for r in data.get("organic_results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("link", ""),
                "content": r.get("snippet", ""),
                "source": r.get("source", ""),
            })
        return results
    except Exception as e:
        logger.warning(f"SerpAPI search failed: {e}")
        return []


def _search_searxng(query: str, cfg: dict, max_results: int = 10,
                    domains: Optional[list[str]] = None, **kwargs) -> list[dict]:
    import requests
    base_url = cfg.get("searxng_base_url", "").rstrip("/")
    if not base_url:
        logger.warning("SearXNG base URL not configured")
        return []
    params = {"q": query, "format": "json", "categories": "news,general"}
    try:
        resp = requests.get(f"{base_url}/search", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for r in data.get("results", [])[:max_results]:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
                "source": r.get("engine", ""),
            })
        return results
    except Exception as e:
        logger.warning(f"SearXNG search failed: {e}")
        return []


def _search_reddit(query: str, max_results: int = 10, **kwargs) -> list[dict]:
    """Search Reddit for discussions. Public JSON API, no auth needed."""
    import requests
    url = "https://www.reddit.com/search.json"
    headers = {"User-Agent": "TruthLens/1.0 (news analysis tool)"}
    params = {"q": query, "limit": min(max_results, 25), "sort": "relevance", "t": "month"}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            selftext = (post.get("selftext", "") or "")[:800]
            results.append({
                "title": post.get("title", ""),
                "url": f"https://reddit.com{post.get('permalink', '')}",
                "content": selftext,
                "source": f"Reddit r/{post.get('subreddit', 'unknown')}",
                "score": post.get("score", 0),
                "comments": post.get("num_comments", 0),
                "upvote_ratio": post.get("upvote_ratio", 0),
            })
        logger.info(f"Reddit search: {len(results)} results for '{query[:40]}...'")
        results.sort(key=lambda r: r["score"] * r["comments"], reverse=True)
        return results
    except Exception:
        # Reddit may be blocked in some regions; fail silently
        return []


_SEARCH_IMPLS = {
    "tavily": _search_tavily,
    "duckduckgo": _search_duckduckgo,
    "brave": _search_brave,
    "serpapi": _search_serpapi,
    "searxng": _search_searxng,
}


def search(query: str, max_results: int = 10, domains: Optional[list[str]] = None,
           **kwargs) -> list[dict]:
    """Unified search entry point. Routes to the configured provider."""
    cfg = _get_provider_config()
    provider = cfg["provider"]
    impl = _SEARCH_IMPLS.get(provider, _search_tavily)
    logger.info(f"Search [{provider}]: {query[:50]}...")
    return impl(query, cfg, max_results=max_results, domains=domains, **kwargs)


def search_reddit(query: str, max_results: int = 10) -> list[dict]:
    """Search Reddit for discussions about a topic."""
    return _search_reddit(query, max_results=max_results)


def get_search_provider() -> str:
    """Return the currently configured search provider."""
    return _get_provider_config()["provider"]
