"""Web search tool for CrewAI agents — live web search via configured provider."""

from __future__ import annotations

import json
from typing import Optional

from crewai.tools import BaseTool

from utils.logger import logger
from utils.i18n import t


class TruthLensSearchTool(BaseTool):
    """Search tool that gathers multi-source intelligence on a given topic."""

    name: str = "truth_lens_search"
    description: str = t("tool.search.description")

    def _run(self, query: str) -> str:
        """Execute search and return structured results as JSON string."""
        logger.info(f"Search tool called with query: {query}")

        try:
            result = self._live_search(query)
            if result:
                return result
        except Exception as e:
            logger.error(f"Live search failed: {e}")

        return json.dumps({
            "topic": query,
            "source": "error",
            "error": t("tool.search.error"),
            "official_news": [],
            "we_media": [],
            "social_sentiment": [],
            "search_summary": "",
            "raw_results": [],
            "social_results": [],
        }, ensure_ascii=False, indent=2)

    def _live_search(self, query: str) -> Optional[str]:
        """Perform live web search via the configured search provider."""
        try:
            from utils.search import bilingual_search
            from utils.search_providers import get_search_provider, search_reddit

            provider = get_search_provider()

            news_results = bilingual_search(
                query=query, max_results=10, search_depth="advanced",
                topic="news", days=30,
            )

            social_results = bilingual_search(
                query=f"{query} 网友评论 舆论",
                max_results=5, search_depth="basic",
                topic="news", days=30,
            )

            reddit_results = search_reddit(query, max_results=8)

            result = {
                "topic": query,
                "source": f"{provider}_live_search",
                "official_news": [],
                "we_media": [],
                "social_sentiment": [],
                "search_summary": "",
                "raw_results": news_results,
                "social_results": social_results,
                "reddit_results": reddit_results,
            }

            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Live search error: {e}")
            return None
