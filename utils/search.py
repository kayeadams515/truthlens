"""Bilingual search utility — splits CN/EN domains, interleaves results."""

from utils.logger import logger

CN_DOMAINS = [
    "zhihu.com", "weibo.com", "sohu.com", "sina.com.cn",
    "163.com", "qq.com", "thepaper.cn", "ifeng.com",
    "guancha.cn", "cls.cn", "caixin.com", "bjd.com.cn",
]

EN_DOMAINS = [
    "bbc.com", "cnn.com", "reuters.com", "apnews.com",
    "nytimes.com", "theguardian.com", "washingtonpost.com",
]

# Providers whose API supports domain filtering natively
_DOMAIN_AWARE_PROVIDERS = {"tavily", "brave"}


def _provider_supports_domains() -> bool:
    from utils.search_providers import get_search_provider
    return get_search_provider() in _DOMAIN_AWARE_PROVIDERS


def bilingual_search(query: str, max_results: int = 10,
                     search_depth: str = "advanced", topic: str = "news",
                     days: int = 30, include_answer: bool = False,
                     include_raw_content: bool = False) -> list[dict]:
    """Search Chinese and English sources separately, then interleave results.

    Returns combined list with CN/EN results alternating, up to max_results.
    For providers that don't support domain filtering (DuckDuckGo, SerpAPI,
    SearXNG), a single undomain-restricted search is performed instead.
    """
    from utils.search_providers import search

    if not _provider_supports_domains():
        results = search(
            query=query, max_results=max_results, domains=None,
            search_depth=search_depth, topic=topic, days=days,
            include_answer=include_answer, include_raw_content=include_raw_content,
        )
        logger.info(f"Bilingual search (single): {len(results)} results")
        return results

    halved = max(max_results // 2, 3)

    cn_results = search(
        query=query, max_results=halved, domains=CN_DOMAINS,
        search_depth=search_depth, topic=topic, days=days,
        include_answer=include_answer, include_raw_content=include_raw_content,
    )

    en_results = search(
        query=query, max_results=halved, domains=EN_DOMAINS,
        search_depth=search_depth, topic=topic, days=days,
        include_answer=include_answer, include_raw_content=include_raw_content,
    )

    # Interleave: CN1, EN1, CN2, EN2, ...
    combined = []
    max_len = max(len(cn_results), len(en_results))
    for i in range(max_len):
        if i < len(cn_results):
            combined.append(cn_results[i])
        if i < len(en_results):
            combined.append(en_results[i])

    result = combined[:max_results]
    logger.info(f"Bilingual search: {len(cn_results)} CN + {len(en_results)} EN -> {len(result)} combined")
    return result


def bilingual_simple_search(query: str, max_results: int = 5) -> list[dict]:
    """Simplified version for quick searches (disambiguation, Q&A)."""
    return bilingual_search(
        query=query, max_results=max_results,
        search_depth="basic", topic="news", days=7,
    )
