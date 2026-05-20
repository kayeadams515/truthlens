"""Bilingual search utility — splits CN/EN domains, interleaves results."""

import re

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

# Providers whose API supports domain filtering (Tavily natively, Brave/SerpAPI via site:)
_DOMAIN_AWARE_PROVIDERS = {"tavily", "brave", "serpapi"}

# ---- Content filter ----
_SPAM_PATTERNS = [
    # Adult / escort / dating spam
    r"约炮", r"上门服务", r"威信[：:\s]*\d", r"美女qq", r"援交",
    r"一夜情", r"同城约", r"嫖", r"小姐", r"按摩.*服务",
    r"escort", r"hookup", r"adult.*dating", r"sex.*chat",
    # Gambling / casino spam
    r"赌场", r"博彩", r"菠菜", r"下注", r"赔率", r"老虎机",
    r"casino", r"gambling", r"betting", r"slot",
    # Typical spam patterns
    r"兼职.*日结", r"日入[过超]", r"躺[赚挣]", r"暴富",
    r"贷款.*秒", r"套[现花]", r"代[办开].*[证卡]",
    r"NOT AN OFFICIAL MINECRAFT SERVICE",
    r"NOT APPROVED BY OR ASSOCIATED WITH MOJANG",
]
_SPAM_PATTERNS_C = [re.compile(p, re.IGNORECASE) for p in _SPAM_PATTERNS]

_SPAM_DOMAINS = {
    "seductivexk.com", "fa88cai.com", "bet365.com",
}

_SPAM_TITLE_STOPS = {
    "minecraft", "sex", "porn", "xxx", "成人", "色情",
    "彩票", "六合彩",
}


def _filter_results(results: list[dict]) -> list[dict]:
    """Remove spam / adult / gambling results."""
    filtered = []
    for r in results:
        title = r.get("title", "") or ""
        content = r.get("content", "") or ""
        url = r.get("url", "") or ""
        text = f"{title} {content}"

        # Domain block
        from urllib.parse import urlparse
        try:
            domain = urlparse(url).netloc.lower()
            if domain in _SPAM_DOMAINS:
                continue
        except Exception:
            pass

        # Title stop words
        title_lower = title.lower()
        if any(w in title_lower for w in _SPAM_TITLE_STOPS):
            continue

        # Regex patterns
        if any(p.search(text) for p in _SPAM_PATTERNS_C):
            continue

        filtered.append(r)

    removed = len(results) - len(filtered)
    if removed:
        logger.info(f"Content filter: removed {removed} spam results")
    return filtered


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
        results = _filter_results(results)
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
    cn_results = _filter_results(cn_results)
    en_results = _filter_results(en_results)
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
