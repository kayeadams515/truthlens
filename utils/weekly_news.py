"""Fetch weekly hot news: Chinese + Global, with translated titles and controversy scoring."""

import json
from datetime import datetime
from pathlib import Path

from config import IS_LLM_CONFIGURED
from utils.logger import logger

CACHE_FILE = Path(__file__).parent.parent / "data" / "weekly_news_cache.json"



def _call_llm(prompt: str) -> str:
    """Quick single-call LLM for translation / classification."""
    if not IS_LLM_CONFIGURED:
        return ""
    try:
        from config import create_integration_llm
        llm = create_integration_llm(temperature=0.0)
        return llm.call(messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        logger.warning(f"LLM call failed: {e}")
        return ""


def _translate_and_classify(news_items: list[dict]) -> list[dict]:
    """Use LLM to translate titles to Chinese and classify as CN/Global + controversy level."""
    if not news_items or not IS_LLM_CONFIGURED:
        # Fallback: mark all as global
        for item in news_items:
            item["title_cn"] = item.get("title", "")
            item["region"] = "global"
            item["controversy"] = "medium"
        return news_items

    # Build prompt
    items_text = "\n".join(
        f"{i+1}. {item.get('title', '')} | source: {item.get('source', '')}"
        for i, item in enumerate(news_items[:12])
    )

    prompt = f"""请对以下新闻逐条处理，返回 JSON 数组。每个元素格式：
{{"id": 序号, "title_cn": "中文标题(简洁)", "region": "china/global", "controversy": "high/medium/low", "reason": "一句话说明为什么是这个争议等级"}}

判断标准：
- region: 与中国直接相关(政治/经济/社会/科技)→china，否则→global
- controversy: 存在明显对立的观点/利益冲突/舆论反转→high，有一定讨论度→medium，纯资讯→low

新闻列表：
{items_text}

只返回 JSON 数组，不要其他内容。"""

    result = _call_llm(prompt)
    if not result:
        return news_items

    # Parse LLM response
    try:
        # Clean potential markdown fences
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[1]
            if result.endswith("```"):
                result = result[:-3]
        classifications = json.loads(result)
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM classification, using fallback")
        for item in news_items:
            item["title_cn"] = item.get("title", "")
            item["region"] = "global"
            item["controversy"] = "medium"
        return news_items

    # Merge classifications back
    class_map = {c["id"]: c for c in classifications}
    for i, item in enumerate(news_items):
        cls = class_map.get(i + 1, {})
        item["title_cn"] = cls.get("title_cn", item.get("title", ""))
        item["region"] = cls.get("region", "global")
        item["controversy"] = cls.get("controversy", "medium")
        item["reason"] = cls.get("reason", "")

    return news_items


def _domain_aware() -> bool:
    from utils.search import _DOMAIN_AWARE_PROVIDERS
    from utils.search_providers import get_search_provider
    return get_search_provider() in _DOMAIN_AWARE_PROVIDERS


def _search_cn_sources(query: str, max_results: int = 6) -> list[dict]:
    """Search Chinese-language sources, domain-restricted when supported."""
    from utils.search import CN_DOMAINS
    from utils.search_providers import search as provider_search
    domains = CN_DOMAINS if _domain_aware() else None
    return provider_search(query=query, max_results=max_results, domains=domains,
                           search_depth="advanced", topic="news", days=7)


def _search_en_sources(query: str, max_results: int = 6) -> list[dict]:
    """Search English-language / global sources, domain-restricted when supported."""
    from utils.search import EN_DOMAINS
    from utils.search_providers import search as provider_search
    domains = EN_DOMAINS if _domain_aware() else None
    return provider_search(query=query, max_results=max_results, domains=domains,
                           search_depth="advanced", topic="news", days=7)


def fetch_weekly_hot_news() -> dict:
    """Fetch this week's hot news, balanced CN/EN. Cached for 2 hours.

    Returns: {"china": [...], "global": [...]}
    """
    # Return cached if fresh
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            cached_at = datetime.fromisoformat(cache.get("cached_at", "2000-01-01"))
            if (datetime.now() - cached_at).total_seconds() < 7200:
                logger.info("Using cached weekly news")
                return {"china": cache.get("china", []), "global": cache.get("global", [])}
        except Exception:
            pass

    today = datetime.now()
    date_cn = f"{today.year}年{today.month}月"
    date_en = today.strftime("%B %Y")

    china_items = []
    cn_seen = set()

    cn_queries = [
        f"中国 本周 热点新闻 争议 {date_cn}",
        f"今日 热搜 社会事件 {date_cn}",
        "国内 头条 新闻 舆论 争议",
    ]
    for q in cn_queries:
        for r in _search_cn_sources(q, max_results=6):
            url = r.get("url", "")
            if url and url not in cn_seen:
                cn_seen.add(url)
                china_items.append({
                    "title": r.get("title", ""),
                    "content": r.get("content", "")[:200],
                    "url": url,
                    "source": r.get("source", ""),
                    "region": "china",
                })

    logger.info(f"Weekly CN search: {len(china_items)} results from CN domains")

    global_items = []
    gl_seen = set()
    # Don't reuse URLs already captured in CN search
    gl_seen.update(cn_seen)

    global_queries = [
        f"world news controversy debate this week {date_en}",
        f"global hot topics trending controversy {today.year}",
    ]
    for q in global_queries:
        for r in _search_en_sources(q, max_results=6):
            url = r.get("url", "")
            if url and url not in gl_seen:
                gl_seen.add(url)
                global_items.append({
                    "title": r.get("title", ""),
                    "content": r.get("content", "")[:200],
                    "url": url,
                    "source": r.get("source", ""),
                    "region": "global",
                })

    logger.info(f"Weekly EN search: {len(global_items)} results from EN domains")

    # ---- Translate & Classify (CN titles to Chinese, EN titles to Chinese) ----
    china_items = _translate_and_classify(china_items)
    global_items = _translate_and_classify(global_items)

    # Sort by controversy level
    controversy_order = {"high": 0, "medium": 1, "low": 2}
    china_items.sort(key=lambda x: (controversy_order.get(x.get("controversy", "medium"), 1), -len(x.get("content", ""))))
    global_items.sort(key=lambda x: (controversy_order.get(x.get("controversy", "medium"), 1), -len(x.get("content", ""))))

    # Top 6 each
    china_items = china_items[:6]
    global_items = global_items[:6]

    # If one side has fewer than 3, pad from the other side's overflow
    # (but only if the other side has results to spare)

    logger.info(f"Weekly news final: {len(china_items)} CN, {len(global_items)} global")

    # Cache
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({
        "cached_at": datetime.now().isoformat(),
        "china": china_items,
        "global": global_items,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"china": china_items, "global": global_items}


def get_fallback_weekly_news() -> dict:
    """Fallback when Tavily unavailable."""
    return {
        "china": [
            {"title_cn": "本周中国社会热点聚焦", "title": "", "content": "多个社会民生话题引发广泛讨论", "source": "", "region": "china", "controversy": "high"},
            {"title_cn": "科技行业最新动态与争议", "title": "", "content": "AI技术应用边界再次成为讨论焦点", "source": "", "region": "china", "controversy": "high"},
            {"title_cn": "经济政策调整引发市场关注", "title": "", "content": "新一轮房地产调控政策出台", "source": "", "region": "china", "controversy": "medium"},
        ],
        "global": [
            {"title_cn": "国际地缘政治新动向", "title": "", "content": "全球主要国家外交关系出现新变化", "source": "", "region": "global", "controversy": "high"},
            {"title_cn": "全球科技竞争加剧", "title": "", "content": "各国在人工智能领域竞相出台新政策", "source": "", "region": "global", "controversy": "medium"},
            {"title_cn": "气候变化国际谈判进展", "title": "", "content": "新一轮全球气候峰会达成部分共识", "source": "", "region": "global", "controversy": "medium"},
        ],
    }
