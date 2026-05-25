"""RSS news source aggregation — pulls real news from verified feeds."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from html import unescape
from typing import Optional
from urllib.parse import urlparse
from xml.etree import ElementTree

import requests

from utils.logger import logger

FEED_TIMEOUT = 10
MAX_PER_SOURCE = 8
MAX_TOTAL = 50

RSS_FEEDS: list[dict] = [
    # ---- Chinese ----
    {"id": "bbc_zhongwen", "url": "https://feeds.bbci.co.uk/zhongwen/trad/rss.xml",
     "name": "BBC中文", "region": "china"},
    {"id": "people_daily",  "url": "http://www.people.com.cn/rss/politics.xml",
     "name": "人民网", "region": "china"},
    {"id": "chinanews",     "url": "http://www.chinanews.com.cn/rss/china.xml",
     "name": "中国新闻网", "region": "china"},
    {"id": "xinhua_world",  "url": "http://www.xinhuanet.com/world/news_world.xml",
     "name": "新华网国际", "region": "china"},
    {"id": "thepaper",      "url": "https://www.thepaper.cn/rss.xml",
     "name": "澎湃新闻", "region": "china"},
    {"id": "chinadaily",    "url": "https://www.chinadaily.com.cn/rss/china_rss.xml",
     "name": "中国日报", "region": "china"},
    {"id": "36kr",          "url": "https://36kr.com/feed",
     "name": "36氪", "region": "china"},
    {"id": "tmtpost",       "url": "https://www.tmtpost.com/rss.xml",
     "name": "钛媒体", "region": "china"},
    # ---- Global ----
    {"id": "bbc_news",      "url": "https://feeds.bbci.co.uk/news/rss.xml",
     "name": "BBC News", "region": "global"},
    {"id": "npr_news",      "url": "https://feeds.npr.org/1001/rss.xml",
     "name": "NPR", "region": "global"},
    {"id": "nyt_world",     "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
     "name": "New York Times", "region": "global"},
    {"id": "voa_news",      "url": "https://www.voanews.com/api/zcqqeogiqe",
     "name": "VOA News", "region": "global"},
    {"id": "guardian_world", "url": "https://www.theguardian.com/world/rss",
     "name": "The Guardian", "region": "global"},
    {"id": "cnn",           "url": "https://www.cnn.com/services/rss/",
     "name": "CNN", "region": "global"},
    {"id": "al_jazeera",    "url": "https://www.aljazeera.com/xml/rss/all.xml",
     "name": "Al Jazeera", "region": "global"},
    {"id": "france24",      "url": "https://www.france24.com/en/rss",
     "name": "France 24", "region": "global"},
    {"id": "dw",            "url": "https://rss.dw.com/rdf/rss-en-all",
     "name": "DW News", "region": "global"},
    {"id": "scmp",          "url": "https://www.scmp.com/rss/91/feed",
     "name": "SCMP", "region": "global"},
]


def _strip_html(text: str) -> str:
    """Remove HTML tags and decode entities from text."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _parse_rss(root: ElementTree.Element) -> list[dict]:
    """Parse RSS 2.0 feed."""
    entries = []
    for item in root.iter("item"):
        title = _strip_html(_text(item, "title"))
        link = _text(item, "link") or _text(item, "guid")
        desc = _strip_html(_text(item, "description") or "")
        pub = _text(item, "pubDate") or _text(item, "dc:date") or ""
        if not title or not link:
            continue
        entries.append({"title": title, "link": link, "desc": desc, "pub": pub})
    return entries


def _parse_atom(root: ElementTree.Element) -> list[dict]:
    """Parse Atom feed."""
    ns = "{http://www.w3.org/2005/Atom}"
    entries = []
    for entry in root.iter(f"{ns}entry"):
        title = _strip_html(_text(entry, f"{ns}title"))
        link_el = entry.find(f"{ns}link")
        link = link_el.get("href", "") if link_el is not None else ""
        if not link:
            for el in entry.findall(f"{ns}link"):
                href = el.get("href", "")
                if href:
                    link = href
                    break
        desc = _strip_html(
            _text(entry, f"{ns}summary") or _text(entry, f"{ns}content") or ""
        )
        pub = _text(entry, f"{ns}published") or _text(entry, f"{ns}updated") or ""
        if not title or not link:
            continue
        entries.append({"title": title, "link": link, "desc": desc, "pub": pub})
    return entries


def _parse_rdf(root: ElementTree.Element) -> list[dict]:
    """Parse RDF/RSS 1.0 feed."""
    ns_rdf = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
    ns_rss = "{http://purl.org/rss/1.0/}"
    ns_dc = "{http://purl.org/dc/elements/1.1/}"
    entries = []
    for item in root.iter(f"{ns_rss}item") if root.find(f".//{ns_rss}item") is not None \
               else root.iter("item"):
        title = _strip_html(_text(item, f"{ns_rss}title") or _text(item, "title"))
        link = _text(item, f"{ns_rss}link") or _text(item, "link")
        desc = _strip_html(
            _text(item, f"{ns_rss}description") or
            _text(item, f"{ns_dc}description") or ""
        )
        pub = (_text(item, f"{ns_dc}date") or _text(item, "pubDate") or "")
        if not title or not link:
            continue
        entries.append({"title": title, "link": link, "desc": desc, "pub": pub})
    return entries


def _text(element: ElementTree.Element, tag: str) -> str:
    """Extract text from a tag or namespaced tag, handling both cases."""
    el = element.find(tag)
    if el is None and "}" not in tag:
        ns = tag.split(":")[0] if ":" in tag else None
        if ns:
            for child in element:
                suffix = "}" + tag.split(":")[1]
                if child.tag.endswith(suffix):
                    el = child
                    break
    return (el.text or "") if el is not None else ""


def _try_parse_date(date_str: str) -> Optional[str]:
    """Try to parse a date string and return ISO format. Returns None on failure."""
    if not date_str:
        return None
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S+00:00",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).isoformat()
        except ValueError:
            continue
    return None


def _fetch_one_feed(feed_def: dict) -> list[dict]:
    """Fetch and parse a single RSS/Atom/RDF feed. Returns list of item dicts."""
    try:
        resp = requests.get(
            feed_def["url"],
            headers={"User-Agent": "TruthLens/1.0"},
            timeout=FEED_TIMEOUT,
            allow_redirects=True,
        )
        resp.raise_for_status()

        content_bytes = resp.content
        if not content_bytes.strip():
            return []

        root = ElementTree.fromstring(content_bytes)

        # Detect feed type
        tag = root.tag.lower()
        entries = []
        if "rss" in tag:
            # Try channel > item
            channel = root.find("channel")
            if channel is not None:
                entries = _parse_rss(channel)
            else:
                entries = _parse_rss(root)
        elif "feed" in tag or "atom" in tag:
            entries = _parse_atom(root)
        elif "rdf" in tag:
            entries = _parse_rdf(root)
        else:
            # Fallback: try all parsers
            entries = _parse_rss(root) or _parse_atom(root) or _parse_rdf(root)

        results = []
        for e in entries[:MAX_PER_SOURCE]:
            pub_iso = _try_parse_date(e["pub"])
            results.append({
                "title": e["title"],
                "url": e["link"],
                "content": e["desc"][:300],
                "source": feed_def["name"],
                "region": feed_def["region"],
                "published": pub_iso or "",
                "feed_id": feed_def["id"],
            })

        if results:
            logger.info(f"RSS {feed_def['id']}: {len(results)} items")
        return results

    except requests.RequestException as e:
        logger.warning(f"RSS {feed_def['id']} HTTP error: {e}")
        return []
    except ElementTree.ParseError as e:
        logger.warning(f"RSS {feed_def['id']} XML parse error: {e}")
        return []
    except Exception as e:
        logger.warning(f"RSS {feed_def['id']} failed: {e}")
        return []


def fetch_all_feeds() -> list[dict]:
    """Fetch all RSS feeds concurrently. Returns deduped, sorted list."""
    all_items = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(_fetch_one_feed, f): f for f in RSS_FEEDS}
        for fut in as_completed(futures):
            try:
                items = fut.result()
                all_items.extend(items)
            except Exception as e:
                logger.warning(f"RSS worker failed: {e}")

    # Deduplicate by URL
    seen = set()
    deduped = []
    for item in all_items:
        url = item["url"]
        if url and url not in seen:
            seen.add(url)
            deduped.append(item)

    # Sort by published date, newest first; items without dates go last
    def sort_key(item):
        pub = item.get("published", "")
        return (0, pub) if pub else (1, "")

    deduped.sort(key=sort_key)

    if len(deduped) > MAX_TOTAL:
        deduped = deduped[:MAX_TOTAL]

    logger.info(f"RSS total: {len(deduped)} items from {len(all_items)} raw (dedup)")
    return deduped


def partition_by_region(items: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split results into (china, global) by region tag."""
    china = [i for i in items if i.get("region") == "china"]
    global_ = [i for i in items if i.get("region") == "global"]
    return china, global_
