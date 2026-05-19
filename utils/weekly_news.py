"""Fetch weekly hot news: Chinese + Global, with translated titles and controversy scoring."""

import json
from datetime import datetime, timedelta
from pathlib import Path

from config import TAVILY_API_KEY, IS_LLM_CONFIGURED
from utils.logger import logger

CACHE_FILE = Path(__file__).parent.parent / "data" / "weekly_news_cache.json"


def _tavily_search(query: str, max_results: int = 6, topic: str = "news") -> list[dict]:
    """Search using Tavily API across both Chinese and Western sources."""
    if not TAVILY_API_KEY:
        return []
    try:
        from tavily import TavilyClient
        from config import get_active_domains
        client = TavilyClient(api_key=TAVILY_API_KEY)

        response = client.search(
            query=query, search_depth="advanced", max_results=max_results,
            include_answer=False, include_raw_content=False,
            topic=topic, days=7,
            include_domains=get_active_domains(),
        )
        return response.get("results", [])
    except Exception as e:
        logger.warning(f"Tavily search failed for '{query}': {e}")
        return []


def _call_llm(prompt: str) -> str:
    """Quick single-call LLM for translation / classification."""
    if not IS_LLM_CONFIGURED:
        return ""
    try:
        from config import create_llm
        llm = create_llm(temperature=0.0)
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


def fetch_weekly_hot_news() -> dict:
    """Fetch this week's hot news, categorized. Cached for 2 hours.

    Returns: {"china": [...], "global": [...]}
    """
    # Return cached if fresh
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            cached_at = datetime.fromisoformat(cache.get("cached_at", "2000-01-01"))
            if (datetime.now() - cached_at).total_seconds() < 7200:
                logger.info(f"Using cached weekly news")
                return {"china": cache.get("china", []), "global": cache.get("global", [])}
        except Exception:
            pass

    seen = set()
    all_items = []

    # ---- Search Chinese News (Chinese + English queries for broader coverage) ----
    cn_queries = [
        "中国 本周 热点新闻 争议 事件",
        "今日 热搜 社会 争议 中国",
        "China hot news controversy this week May 2026",
    ]
    for q in cn_queries:
        for r in _tavily_search(q, max_results=6, topic="news"):
            url = r.get("url", "")
            if url and url not in seen:
                seen.add(url)
                all_items.append({
                    "title": r.get("title", ""),
                    "content": r.get("content", "")[:200],
                    "url": url,
                    "source": r.get("source", ""),
                })

    # ---- Search Global News ----
    global_queries = [
        "world news controversy debate this week May 2026",
        "global hot topics trending controversy 2026",
    ]
    for q in global_queries:
        for r in _tavily_search(q, max_results=6, topic="news"):
            url = r.get("url", "")
            if url and url not in seen:
                seen.add(url)
                all_items.append({
                    "title": r.get("title", ""),
                    "content": r.get("content", "")[:200],
                    "url": url,
                    "source": r.get("source", ""),
                })

    # ---- Translate & Classify ----
    classified = _translate_and_classify(all_items)

    china_news = [item for item in classified if item.get("region") == "china"]
    global_news = [item for item in classified if item.get("region") != "china"]

    # Sort by controversy level
    controversy_order = {"high": 0, "medium": 1, "low": 2}
    china_news.sort(key=lambda x: (controversy_order.get(x.get("controversy", "medium"), 1), -len(x.get("content", ""))))
    global_news.sort(key=lambda x: (controversy_order.get(x.get("controversy", "medium"), 1), -len(x.get("content", ""))))

    # Top 6 each
    china_news = china_news[:6]
    global_news = global_news[:6]

    logger.info(f"Weekly news: {len(china_news)} CN, {len(global_news)} global")

    # Cache
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({
        "cached_at": datetime.now().isoformat(),
        "china": china_news,
        "global": global_news,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"china": china_news, "global": global_news}


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
