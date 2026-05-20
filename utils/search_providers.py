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
    # Fallback to env for API keys
    import os
    if not cfg.get("tavily_api_key"):
        cfg["tavily_api_key"] = os.getenv("TAVILY_API_KEY", "")
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
        include_raw_content=False,
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
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS
    results = []
    try:
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


def get_search_provider() -> str:
    """Return the currently configured search provider."""
    return _get_provider_config()["provider"]
