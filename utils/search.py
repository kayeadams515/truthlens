"""Bilingual search utility — splits CN/EN domains, interleaves results."""

import re

from utils.logger import logger

CN_DOMAINS = [
    # 官方媒体
    "xinhuanet.com", "people.com.cn", "cctv.com",
    "huanqiu.com", "chinanews.com.cn", "gmw.cn",
    # 门户与资讯
    "zhihu.com", "weibo.com", "sohu.com", "sina.com.cn",
    "163.com", "qq.com", "thepaper.cn", "ifeng.com",
    "guancha.cn", "cls.cn", "caixin.com", "bjd.com.cn",
    # 社交与社区平台
    "douyin.com", "xiaohongshu.com",
    "bilibili.com", "tieba.baidu.com", "douban.com",
]

EN_DOMAINS = [
    # 传统媒体
    "bbc.com", "cnn.com", "reuters.com", "apnews.com",
    "nytimes.com", "theguardian.com", "washingtonpost.com",
    # 社交平台
    "youtube.com", "x.com", "twitter.com",
    "facebook.com", "instagram.com",
    "reddit.com", "tiktok.com",
]

# Providers whose API supports domain filtering (Tavily natively, Brave/SerpAPI via site:)
_DOMAIN_AWARE_PROVIDERS = {"tavily", "brave", "serpapi"}

# ---- Content filter ----
_SPAM_PATTERNS = [
    # Adult / escort / dating spam
    r"约炮", r"上门服务", r"威信[：:\s]*\d", r"美女qq", r"援交",
    r"一夜情", r"同城约", r"\b嫖\b", r"小姐.*服务", r"按摩.*服务",
    r"裸聊", r"少妇", r"熟女", r"学生妹", r"包夜",
    r"escort", r"hookup", r"adult.*dating", r"sex.*chat",
    r"porn", r"nude", r"onlyfans",
    # Gambling / casino spam
    r"赌场", r"博彩", r"菠菜", r"下注", r"赔率", r"老虎机",
    r"棋牌", r"捕鱼.*游戏", r"百家乐", r"德州扑克",
    r"casino", r"gambling", r"betting", r"slot",
    r"sportsbook", r"bookmaker",
    # Typical spam / scam patterns
    r"兼职.*日结", r"日入[过超]", r"躺[赚挣]", r"暴富",
    r"贷款.*秒", r"套[现花]", r"代[办开].*[证卡]",
    r"刷单", r"网赚", r"返利.*佣金",
    r"NOT AN OFFICIAL MINECRAFT SERVICE",
    r"NOT APPROVED BY OR ASSOCIATED WITH MOJANG",
    # Phishing / malware
    r"免费.*领取.*红包", r"扫码.*领取", r"点击.*领取.*大奖",
    r"中奖.*通知", r"幸运.*用户",
    # SEO spam
    r"外链.*软件", r"软件.*推广", r"TG.*推广", r"telegram.*推广",
    r"谷歌.*推广", r"百度.*推广", r"关键词.*优化", r"SEO.*服务",
    r"外链.*TG", r"外链.*飞机",
    # Fake reviews / nonsense
    r"amenities?\s*review", r"\bB1\s*review\b", r"\bB1\s*设施评价\b",
    r"facilities?\s*review", r"fake\s*review",
    r"[A-Z][a-z]+ [A-Z][a-z]+ B\d",
    # PDF / document viewer pages
    r"pdf\.js", r"viewer\.html.*file=",
    r"/plugins/generic/pdfJsViewer", r"\.pdf\?",
    # Search / aggregator result pages
    r"Live Posts & Updates", r"X.*search\?",
    r"exploding.?topics", r"trends?24",
    # Garbage / nonsense strings
    r"[A-Z]{6,}",  # Random uppercase strings like WKZCCRVC
]
_SPAM_PATTERNS_C = [re.compile(p, re.IGNORECASE) for p in _SPAM_PATTERNS]

_SPAM_DOMAINS = {
    "seductivexk.com", "fa88cai.com", "bet365.com",
    "v88av.com", "bet288.com", "abg888.com",
    "catscale.com", "ojs.library.okstate.edu",
    "practiceguides.chambers.com", "explodingtopics.com",
    "trends24.in", "trends.google.com",
    "behance.net", "vimeo.com", "ln24international.com",
}

_NON_NEWS_URL_PATTERNS_C = [
    re.compile(r"/search\b"), re.compile(r"behance\.net/search"),
    re.compile(r"vimeo\.com/\d+/likes"), re.compile(r"trends\.google\.com"),
]

_SPAM_TITLE_STOPS = {
    "minecraft", "sex", "porn", "xxx", "成人", "色情",
    "彩票", "六合彩", "賭場", "百家乐",
    "buy cheap", "free shipping", "wholesale",
    "viagra", "cialis", "casino online",
    "amenities review", "b1 amenities", "设施评价",
    "not an official", "not approved by",
    "google 外链", "外链软件", "外链推广",
}

_CN_SPAM_TOKENS = ["外链", "推广", "TG:", "@", "软件推广", "谷歌推广", "百度推广"]


def _filter_results(results: list[dict]) -> list[dict]:
    """Remove spam / adult / gambling / SEO / garbage results."""
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

        # URL path patterns
        url_lower = url.lower()
        if any(p.search(url_lower) for p in _NON_NEWS_URL_PATTERNS_C):
            continue

        # Title stop words
        title_lower = title.lower()
        if any(w in title_lower for w in _SPAM_TITLE_STOPS):
            continue

        # Regex patterns
        if any(p.search(text) for p in _SPAM_PATTERNS_C):
            continue

        # Chinese SEO heuristic: >= 2 suspicious tokens
        cn_hits = sum(1 for t in _CN_SPAM_TOKENS if t in text)
        if cn_hits >= 2:
            continue

        # Minimum quality: content must be meaningful
        if len(content.strip()) < 10 and len(title.strip()) < 15:
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
        try:
            results = search(
                query=query, max_results=max_results, domains=None,
                search_depth=search_depth, topic=topic, days=days,
                include_answer=include_answer, include_raw_content=include_raw_content,
            )
        except Exception as e:
            logger.warning(f"Search failed: {e}")
            return []
        results = _filter_results(results)
        logger.info(f"Bilingual search (single): {len(results)} results")
        return results

    halved = max(max_results // 2, 3)

    try:
        cn_results = search(
            query=query, max_results=halved, domains=CN_DOMAINS,
            search_depth=search_depth, topic=topic, days=days,
            include_answer=include_answer, include_raw_content=include_raw_content,
        )
    except Exception as e:
        logger.warning(f"CN search failed: {e}")
        cn_results = []

    try:
        en_results = search(
            query=query, max_results=halved, domains=EN_DOMAINS,
            search_depth=search_depth, topic=topic, days=days,
            include_answer=include_answer, include_raw_content=include_raw_content,
        )
    except Exception as e:
        logger.warning(f"EN search failed: {e}")
        en_results = []

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
