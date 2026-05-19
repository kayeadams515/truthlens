"""Scout Agent (情报官) — Multi-source intelligence gathering."""

from crewai import Agent
from tools.search_tool import TruthLensSearchTool
from agents import create_llm


def create_scout_agent() -> Agent:
    """Create the Scout Agent responsible for gathering multi-source intel."""

    return Agent(
        role="情报官 (Scout)",
        goal=(
            "针对用户输入的事件话题，从多个维度全面搜集信息："
            "1) 官方/权威机构的通报与声明；"
            "2) 自媒体/KOL的观点及爆料；"
            "3) 社交媒体(微博、抖音、知乎)上代表性评论及其情绪色彩；"
            "4) 事件关键时间线与参与方的利益关系网络。"
            "最终输出一份结构化的原始情报汇编，供下游Agent分析使用。"
        ),
        backstory=(
            "你是一位经验丰富的情报分析师，曾在国家级媒体担任调查记者15年。"
            "你精通OSINT(开源情报)技术，能从海量碎片信息中提炼关键事实。"
            "你深知：真相往往藏在细节中，而每一方的说辞都带着各自的立场和动机。"
            "你的职业信条是：不放过任何一条线索，不给任何一方特殊待遇。"
        ),
        tools=[TruthLensSearchTool()],
        llm=create_llm(temperature=0.1),
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )
