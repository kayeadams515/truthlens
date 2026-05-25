"""Fetch weekly hot news: Chinese + Global, with translated titles and controversy scoring."""

import json
from datetime import datetime
from pathlib import Path

from config import is_any_llm_configured
from utils.logger import logger
from utils.i18n import t
from utils.paths import get_data_dir

CACHE_FILE = get_data_dir() / "weekly_news_cache.json"



def _call_llm(prompt: str) -> str:
    """Quick single-call LLM for translation / classification."""
    if not is_any_llm_configured():
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
    if not news_items or not is_any_llm_configured():
        # Fallback: preserve original region, use title as-is
        for item in news_items:
            item["title_cn"] = item.get("title", "")
            item["region"] = item.get("region", "unknown")
            item["controversy"] = "unknown"
        return news_items

    # Build prompt
    items_text = "\n".join(
        f"{i+1}. {item.get('title', '')} | source: {item.get('source', '')}"
        for i, item in enumerate(news_items[:12])
    )

    prompt = t("prompt.weekly_news.classify", items_text=items_text)

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
            item["region"] = item.get("region", "unknown")
            item["controversy"] = "unknown"
        return news_items

    # Merge classifications back
    class_map = {c["id"]: c for c in classifications}
    for i, item in enumerate(news_items):
        cls = class_map.get(i + 1, {})
        item["title_cn"] = cls.get("title_cn", item.get("title", ""))
        item["region"] = cls.get("region", item.get("region", "unknown"))
        item["controversy"] = cls.get("controversy", "unknown")
        item["reason"] = cls.get("reason", "")

    return news_items


def _domain_aware() -> bool:
    from utils.search import _DOMAIN_AWARE_PROVIDERS
    from utils.search_providers import get_search_provider
    return get_search_provider() in _DOMAIN_AWARE_PROVIDERS


def _search_cn_sources(query: str, max_results: int = 6) -> list[dict]:
    """Search Chinese-language sources, domain-restricted when supported."""
    from utils.search import CN_DOMAINS, _filter_results
    from utils.search_providers import search as provider_search
    domains = CN_DOMAINS if _domain_aware() else None
    try:
        results = provider_search(query=query, max_results=max_results, domains=domains,
                                  search_depth="advanced", topic="news", days=7)
    except Exception as e:
        logger.warning(f"CN source search failed: {e}")
        return []
    return _filter_results(results)


def _search_en_sources(query: str, max_results: int = 6) -> list[dict]:
    """Search English-language / global sources, domain-restricted when supported."""
    from utils.search import EN_DOMAINS, _filter_results
    from utils.search_providers import search as provider_search
    domains = EN_DOMAINS if _domain_aware() else None
    try:
        results = provider_search(query=query, max_results=max_results, domains=domains,
                                  search_depth="advanced", topic="news", days=7)
    except Exception as e:
        logger.warning(f"EN source search failed: {e}")
        return []
    return _filter_results(results)


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
        f"新闻 社会 争议 事件 {date_cn}",
        f"最新 报道 事件 话题 {date_cn}",
        "时事 头条 新闻 争议",
    ]
    for q in cn_queries:
        for r in _search_cn_sources(q, max_results=8):
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

    # ---- Supplement with RSS feeds (quality news baseline) ----
    try:
        from utils.news_sources import fetch_all_feeds
        rss_items = fetch_all_feeds()
        rss_added = 0
        all_urls = cn_seen | gl_seen
        for r in rss_items:
            url = r.get("url", "")
            if url and url not in all_urls:
                all_urls.add(url)
                entry = {
                    "title": r.get("title", ""),
                    "content": r.get("content", "")[:200],
                    "url": url,
                    "source": r.get("source", ""),
                    "region": r.get("region", "global"),
                }
                if r.get("region") == "china":
                    china_items.append(entry)
                else:
                    global_items.append(entry)
                rss_added += 1
        logger.info(f"RSS supplement: {rss_added} new items added")
    except ImportError:
        logger.info("RSS module not available, skipping")
    except Exception as e:
        logger.warning(f"RSS supplement failed: {e}")

    # ---- Filter merged results (RSS items were added directly, need filtering too) ----
    from utils.search import _filter_results
    china_items = _filter_results(china_items)
    global_items = _filter_results(global_items)

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


