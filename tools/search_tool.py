"""Web search tool for CrewAI agents — uses Tavily API with mock data fallback."""

from __future__ import annotations

import json
from typing import Any, Optional

from crewai.tools import BaseTool
from pydantic import Field

from config import TAVILY_API_KEY
from tools.mock_data import get_mock_news, search_mock_news, list_scenarios
from utils.logger import logger


class TruthLensSearchTool(BaseTool):
    """Search tool that gathers multi-source intelligence on a given topic.

    When Tavily API key is available, performs live web search.
    Otherwise, falls back to realistic mock data for demonstration.
    """

    name: str = "truth_lens_search"
    description: str = (
        "搜索指定话题的全网信息，返回官方通报、自媒体观点、社交媒体评论等多源数据。"
        "输入为话题关键词或URL链接。输出为结构化的JSON格式情报数据。"
    )

    def _run(self, query: str) -> str:
        """Execute search and return structured results as JSON string."""
        logger.info(f"Search tool called with query: {query}")

        # Try real search first if API key is available
        if TAVILY_API_KEY:
            try:
                result = self._tavily_search(query)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Tavily search failed, falling back to mock: {e}")

        # Fall back to mock data
        return self._mock_search(query)

    def _tavily_search(self, query: str) -> Optional[str]:
        """Perform live web search using Tavily API across CN + EN sources."""
        try:
            from tavily import TavilyClient
            from config import get_active_domains
            client = TavilyClient(api_key=TAVILY_API_KEY)
            domains = get_active_domains()

            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=10,
                include_answer=True,
                include_raw_content=False,
                include_domains=domains,
            )

            social_response = client.search(
                query=f"{query} 网友评论 舆论",
                search_depth="basic",
                max_results=5,
                include_domains=domains,
            )

            result = {
                "topic": query,
                "source": "tavily_live_search",
                "official_news": [],
                "we_media": [],
                "social_sentiment": [],
                "search_summary": response.get("answer", ""),
                "raw_results": response.get("results", []),
                "social_results": social_response.get("results", []),
            }

            return json.dumps(result, ensure_ascii=False, indent=2)

        except ImportError:
            logger.warning("tavily-python not installed")
            return None
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return None

    def _mock_search(self, query: str) -> str:
        """Use mock data as fallback."""
        logger.info(f"Using mock data for query: {query}")

        # Try to find matching scenario
        scenario = search_mock_news(query)

        if not scenario:
            # If no match, return the first scenario with a note
            scenario = get_mock_news("ev_crash")
            note = f'未找到与"{query}"完全匹配的模拟数据，以下是示例数据以供演示。'
        else:
            note = f'以下为关于"{scenario["topic"]}"的模拟情报数据。'

        result = {
            "topic": scenario["topic"],
            "source": "mock_data",
            "note": note,
            "summary_5w1h": scenario["summary_5w1h"],
            "official": scenario["official"],
            "we_media": scenario["we_media"],
            "social_media": scenario["social_media"],
        }

        return json.dumps(result, ensure_ascii=False, indent=2)


class ScenarioListTool(BaseTool):
    """Tool to list all available pre-built analysis scenarios."""

    name: str = "list_scenarios"
    description: str = "列出系统内预置的所有热点新闻事件，供用户浏览和选择。"

    def _run(self, _: str = "") -> str:
        scenarios = list_scenarios()
        return json.dumps(scenarios, ensure_ascii=False, indent=2)
