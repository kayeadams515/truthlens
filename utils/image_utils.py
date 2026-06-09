"""Image utility — domain authority scoring, selection, and LLM formatting."""
from __future__ import annotations

from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Domain Authority Database
# ---------------------------------------------------------------------------
# Tiers: 1.0 = top global wire services & broadcasters
#        0.8 = major national papers & respected outlets
#        0.5 = recognized news / tech / commentary
#        0.2 = social media, aggregators, unknown

_DOMAIN_TIERS: dict[str, float] = {
    # ---- Tier 1: global wire services & flagship broadcasters ----
    "tavily.com": 1.0,    # Tavily-curated query-relevant images
    "reuters.com": 1.0,
    "apnews.com": 1.0,
    "bbc.com": 1.0,
    "bbc.co.uk": 1.0,
    "nytimes.com": 1.0,
    "news.cn": 1.0,
    "xinhuanet.com": 1.0,
    "cctv.com": 1.0,
    "cnn.com": 1.0,
    "washingtonpost.com": 1.0,
    "theguardian.com": 1.0,
    # ---- Tier 2: major nationals & respected specialists ----
    "people.com.cn": 0.8,
    "caixin.com": 0.8,
    "thepaper.cn": 0.8,
    "bloomberg.com": 0.8,
    "wsj.com": 0.8,
    "ft.com": 0.8,
    "economist.com": 0.8,
    "npr.org": 0.8,
    "aljazeera.com": 0.8,
    "politico.com": 0.8,
    "thehill.com": 0.8,
    "time.com": 0.8,
    "newsweek.com": 0.8,
    "independent.co.uk": 0.8,
    "telegraph.co.uk": 0.8,
    "dw.com": 0.8,
    "france24.com": 0.8,
    "scmp.com": 0.8,
    "nikkei.com": 0.8,
    "ifeng.com": 0.8,
    "guancha.cn": 0.8,
    # ---- Tier 3: recognized news / tech / regional ----
    "163.com": 0.5,
    "qq.com": 0.5,
    "sina.com.cn": 0.5,
    "sohu.com": 0.5,
    "toutiao.com": 0.5,
    "huanqiu.com": 0.5,
    "chinadaily.com.cn": 0.5,
    "globaltimes.cn": 0.5,
    "yicai.com": 0.5,
    "jiemian.com": 0.5,
    "cls.cn": 0.5,
    "36kr.com": 0.5,
    "tmtpost.com": 0.5,
    "huxiu.com": 0.5,
    "techcrunch.com": 0.5,
    "theverge.com": 0.5,
    "arstechnica.com": 0.5,
    "wired.com": 0.5,
    "vox.com": 0.5,
    "vice.com": 0.5,
    "buzzfeednews.com": 0.5,
    "theatlantic.com": 0.5,
    "newyorker.com": 0.5,
    "usatoday.com": 0.5,
    "latimes.com": 0.5,
    "chicagotribune.com": 0.5,
    "nypost.com": 0.5,
    "dailymail.co.uk": 0.5,
    "mirror.co.uk": 0.5,
    "thesun.co.uk": 0.5,
    "abc.net.au": 0.5,
    "smh.com.au": 0.5,
    "straitstimes.com": 0.5,
    "channelnewsasia.com": 0.5,
    "joins.com": 0.5,
}

# ---- Social / UGC domains always Tier 4 ----
_SOCIAL_DOMAINS: set[str] = {
    "reddit.com", "twitter.com", "x.com", "weibo.com",
    "zhihu.com", "douban.com", "bilibili.com", "douyin.com",
    "tiktok.com", "youtube.com", "facebook.com", "instagram.com",
    "baidu.com", "tieba.baidu.com",
}

_DEFAULT_AUTHORITY = 0.2


def get_domain_authority(url: str) -> float:
    """Return an authority score [0.2 – 1.0] for a news-domain URL.

    Social / UGC domains always score 0.2 regardless of tier list.
    """
    try:
        domain = urlparse(url).netloc.lower()
        # Strip leading "www."
        if domain.startswith("www."):
            domain = domain[4:]
    except Exception:
        return _DEFAULT_AUTHORITY

    if domain in _SOCIAL_DOMAINS:
        return _DEFAULT_AUTHORITY
    return _DOMAIN_TIERS.get(domain, _DEFAULT_AUTHORITY)


# ---------------------------------------------------------------------------
# Image scoring & selection
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Junk-image filter — ad pixels, tracking, logos, icons, SVG, etc.
# ---------------------------------------------------------------------------

# Domains / URL patterns that are definitely NOT editorial images
_JUNK_DOMAINS = {
    "aorta.clickagy.com", "analytics.twitter.com", "t.co",
    "p1.zemanta.com", "ids4.ad.gt", "ids.ad.gt",
    "secure.adnxs.com", "ib.adnxs.com",
    "u.openx.net", "image2.pubmatic.com", "token.rubiconproject.com",
    "sync.go.sonobi.com", "ad.360yield.com",
    "consent.trustarc.com",
    "a.usbrowserspeed.com",
}

_JUNK_PATH_TOKENS = (
    "favicon", "icon-", "logo-", "avatar", "/icon/", "/logo/",
    "cookiepref", "bars-regular", "xmark-solid",
    "/pf/resources/images/logos/",  # site logo directories
    "channel-sync",  # tracking pixels disguised as images
    "/i/adsct",       # Twitter ads tracking
)

def _is_junk_image(url: str) -> bool:
    """Return True if the image URL looks like a tracking pixel, logo, icon, etc."""
    url_lower = url.lower()

    # SVG files are almost always logos/icons (not news photos)
    if url_lower.endswith(".svg"):
        return True

    # Check junk domains
    try:
        domain = urlparse(url).netloc.lower()
        # Strip leading "www."
        domain = domain[4:] if domain.startswith("www.") else domain
        if domain in _JUNK_DOMAINS:
            return True
    except Exception:
        pass

    # Check junk path tokens
    for token in _JUNK_PATH_TOKENS:
        if token in url_lower:
            return True

    # Real editorial images usually have .jpg/.jpeg/.png/.webp extensions
    # or come from known image CDNs
    is_image_ext = url_lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))
    is_image_cdn = any(cdn in url_lower for cdn in (
        "image", "photo", "img", "picture", "media",
        "resizer", "cdn", "q_70", "/images/", "/pictures/",
        "itc.cn", "imgur.com", "cloudinary.com",
    ))
    if not is_image_ext and not is_image_cdn:
        return True  # likely a tracking pixel or data URL

    return False


# ---------------------------------------------------------------------------
# Image scoring & selection
# ---------------------------------------------------------------------------

def score_images(search_results: list[dict]) -> list[dict]:
    """Score and rank images from search results.

    Each image is scored by:
      - domain_authority (60 % weight) — how reputable the source is
      - search_rank       (40 % weight) — position in the result list

    Returns a flat list sorted by combined score descending.
    Items: {url, description, source_title, source_url, score}
    """
    total = len(search_results)
    if total == 0:
        return []

    scored: list[dict] = []

    for idx, result in enumerate(search_results):
        images = result.get("images") or []
        if not images:
            continue

        domain_score = get_domain_authority(result.get("url", ""))
        rank_score = 1.0 - (idx / total)

        for img in images:
            if not isinstance(img, dict):
                continue
            img_url = img.get("url", "")
            if not img_url:
                continue
            if _is_junk_image(img_url):
                continue

            scored.append({
                "url": img_url,
                "description": img.get("description", ""),
                "source_title": result.get("title", ""),
                "source_url": result.get("url", ""),
                "score": round(0.6 * domain_score + 0.4 * rank_score, 3),
            })

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Deduplicate — first by exact URL, then by image host domain (1 per domain
    # ensures visual variety instead of 5 shots of the same wire photo).
    seen_urls: set[str] = set()
    seen_domains: set[str] = set()
    deduped: list[dict] = []

    def _img_domain(url: str) -> str:
        try:
            d = urlparse(url).netloc.lower()
            return d[4:] if d.startswith("www.") else d
        except Exception:
            return url

    for img in scored:
        url = img["url"]
        if url in seen_urls:
            continue
        domain = _img_domain(url)
        if domain in seen_domains:
            continue
        seen_urls.add(url)
        seen_domains.add(domain)
        deduped.append(img)

    return deduped


def select_cover_image(scored_images: list[dict]) -> dict | None:
    """Return the highest-scoring image suitable for use as a cover image."""
    if not scored_images:
        return None
    # The scoring already filters junk, so the highest-score image is the best
    return scored_images[0]


def format_images_for_llm(scored_images: list[dict], max_images: int = 8) -> str:
    """Format scored images as a text block for LLM prompt injection.

    Uses Markdown reference-style syntax so the LLM can insert images inline.
    """
    if not scored_images:
        return ""

    top = scored_images[:max_images]

    # Influence label
    def _label(score: float) -> str:
        if score >= 0.8:
            return "high"
        if score >= 0.5:
            return "medium"
        return "standard"

    lines = [
        "## 📷 Available Images (sorted by source influence)",
        "",
        "You may embed these images in the report using `![description](url)` syntax.",
        "ONLY use images that clearly relate to the adjacent content.",
        "DO NOT fabricate image URLs — only use the ones listed below.",
        "Prefer higher-influence (★) images for key sections.",
        "",
    ]

    for i, img in enumerate(top, 1):
        stars = "★★★" if img["score"] >= 0.8 else ("★★" if img["score"] >= 0.5 else "★")
        desc = img["description"] or img["source_title"]
        lines.append(
            f"{i}. **{desc}** — from *{img['source_title']}*  "
            f"[influence: {_label(img['score'])}, score: {img['score']:.2f}]\n"
            f"   `{img['url']}`\n"
            f"   ↳ insert as: `![{desc}]({img['url']})`\n"
        )

    return "\n".join(lines)
