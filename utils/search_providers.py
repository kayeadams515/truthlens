"""Unified search provider abstraction — Tavily, Brave, SerpAPI, SearXNG."""

from __future__ import annotations

from typing import Optional

from utils.logger import logger

PROVIDERS = {
    "tavily":       "Tavily",
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
        include_images=True,
        topic=kwargs.get("topic", "news"),
        days=kwargs.get("days", 7),
    )
    if domains:
        params["include_domains"] = domains
    resp = client.search(**params)
    # Collect top-level images (query-relevant, may be plain URL strings)
    top_images = resp.get("images", [])
    if not isinstance(top_images, list):
        top_images = []

    def _normalize(img):
        """Normalize image entries: string → {url}, dict → keep as-is."""
        if isinstance(img, str) and img.startswith("http"):
            return {"url": img}
        if isinstance(img, dict) and img.get("url"):
            return {"url": img["url"]}
        return None

    results = []
    # Prepend top-level Tavily images as a virtual high-authority result so they
    # score highest during image selection. These are query-relevant editorial
    # images curated by Tavily, not per-page UI elements.
    top_normalized = [ni for ni in (_normalize(ti) for ti in top_images[:5]) if ni]
    if top_normalized:
        results.append({
            "title": f"Topic Images: {query[:80]}",
            "url": "https://tavily.com",
            "content": "",
            "source": "Tavily Image Search",
            "images": top_normalized,
        })

    for r in resp.get("results", []):
        images = r.get("images", [])
        if not isinstance(images, list):
            images = []
        normalized = [ni for ni in (_normalize(img) for img in images) if ni]
        results.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", ""),
            "source": "",
            "images": normalized,
        })
    return results


def _search_duckduckgo(query: str, cfg: dict, max_results: int = 10,
                        domains: Optional[list[str]] = None, **kwargs) -> list[dict]:
    # DuckDuckGo does not support domain filtering via site: syntax — it causes timeouts.
    # Domains are ignored for this provider.
    import re

    # Import DDGS: prefer ddgs (v9+), fall back to duckduckgo_search (v8)
    DDGS = None
    import_errors = []
    try:
        from ddgs import DDGS
    except ImportError as e:
        import_errors.append(f"ddgs: {e}")
    if DDGS is None:
        try:
            from duckduckgo_search import DDGS
        except ImportError as e:
            import_errors.append(f"duckduckgo_search: {e}")
    if DDGS is None:
        raise RuntimeError(
            "DuckDuckGo: neither ddgs nor duckduckgo_search is installed. "
            "Run: pip install ddgs"
        )

    results = []
    text_kwargs: dict = {"max_results": max_results}
    if re.search(r'[一-鿿]', query):
        text_kwargs["region"] = "cn-zh"

    def _collect(iterator):
        for r in iterator:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "content": r.get("body", ""),
                "source": "",
            })

    try:
        with DDGS() as ddgs:
            _collect(ddgs.text(query, **text_kwargs))
    except TypeError:
        logger.debug("DuckDuckGo text() rejected kwargs, retrying with query only")
        try:
            with DDGS() as ddgs:
                _collect(ddgs.text(query, max_results=max_results))
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
            raise RuntimeError(f"DuckDuckGo: {e}") from e
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")
        raise RuntimeError(f"DuckDuckGo: {e}") from e

    if not results:
        logger.warning(
            f"DuckDuckGo returned 0 results for '{query[:60]}'. "
            "This may indicate network issues or DuckDuckGo being unreachable."
        )

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
            images = []
            thumbnail = r.get("thumbnail")
            if thumbnail and isinstance(thumbnail, dict) and thumbnail.get("src"):
                images.append({"url": thumbnail["src"]})
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("description", ""),
                "source": "",
                "images": images,
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
            images = []
            # Try thumbnail first
            thumb = r.get("thumbnail")
            if thumb and isinstance(thumb, str):
                images.append({"url": thumb})
            # Also check pagemap for article images
            pagemap = r.get("pagemap", {})
            if isinstance(pagemap, dict):
                cse_image = pagemap.get("cse_image")
                if isinstance(cse_image, list):
                    for img in cse_image:
                        if isinstance(img, dict) and img.get("src"):
                            images.append({"url": img["src"]})
                elif isinstance(cse_image, dict) and cse_image.get("src"):
                    images.append({"url": cse_image["src"]})
            results.append({
                "title": r.get("title", ""),
                "url": r.get("link", ""),
                "content": r.get("snippet", ""),
                "source": r.get("source", ""),
                "images": images,
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
            images = []
            img_src = r.get("img_src")
            if img_src and isinstance(img_src, str):
                images.append({"url": img_src})
            thumbnail = r.get("thumbnail")
            if thumbnail and isinstance(thumbnail, str) and thumbnail not in [img_src]:
                images.append({"url": thumbnail})
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
                "source": r.get("engine", ""),
                "images": images,
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
            # Extract best available image
            images = []
            preview = post.get("preview", {})
            if isinstance(preview, dict):
                preview_images = preview.get("images", [])
                if isinstance(preview_images, list) and preview_images:
                    for pi in preview_images:
                        if isinstance(pi, dict):
                            source = pi.get("source", {})
                            if isinstance(source, dict) and source.get("url"):
                                images.append({"url": source["url"].replace("&amp;", "&")})
            # Fallback: use thumbnail if it's a real URL (not "self", "default", "nsfw")
            if not images:
                thumb = post.get("thumbnail", "")
                if thumb and isinstance(thumb, str) and thumb.startswith("http"):
                    images.append({"url": thumb})
            results.append({
                "title": post.get("title", ""),
                "url": f"https://reddit.com{post.get('permalink', '')}",
                "content": selftext,
                "source": f"Reddit r/{post.get('subreddit', 'unknown')}",
                "score": post.get("score", 0),
                "comments": post.get("num_comments", 0),
                "upvote_ratio": post.get("upvote_ratio", 0),
                "images": images,
            })
        logger.info(f"Reddit search: {len(results)} results for '{query[:40]}...'")
        results.sort(key=lambda r: r["score"] * r["comments"], reverse=True)
        return results
    except Exception:
        # Reddit may be blocked in some regions; fail silently
        return []


_SEARCH_IMPLS = {
    "tavily": _search_tavily,
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
