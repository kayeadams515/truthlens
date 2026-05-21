"""CrewAI orchestrator — assembles the 4-agent debate pipeline."""

from __future__ import annotations

from crewai import Crew, Process, Task

from agents.scout import create_scout_agent
from agents.challenger import create_challenger_agent
from agents.judge import create_judge_agent
from agents.editor import create_editor_agent
from utils.logger import logger


def _build_tasks(
    topic: str,
    scout,
    challenger,
    judge,
    editor,
) -> list[Task]:
    """Build the 4 sequential tasks for the debate pipeline."""

    # ---- Task 1: Scout gathers raw intelligence ----
    task_scout = Task(
        description=(
            f"用户关注的事件话题是：「{topic}」\n\n"
            "请使用你的搜索工具，从以下维度全面搜集信息：\n"
            "1. 使用搜索工具搜索该话题，获取官方通报、媒体报道、社交媒体讨论\n"
            "2. 提取事件关键时间线上的每一个节点\n"
            "3. 识别事件中的各利益相关方及其公开立场\n"
            "4. 选取社交媒体上最具代表性的评论(包括不同情绪倾向的)\n\n"
            "输出要求：用中文输出结构化的情报汇编，包含：\n"
            "- 事件5W1H基本信息\n"
            "- 官方/权威方声明(逐条列出，注明出处)\n"
            "- 自媒体/KOL观点(逐条列出，注明发布者、粉丝量、可能的利益关联)\n"
            "- 社交媒体代表性评论(至少5条，注明情绪倾向和点赞量)\n"
            "- 情绪分布统计(给出各情绪的大致占比)\n\n"
            "如果有URL链接注明原始链接。所有信息必须标注来源。"
        ),
        expected_output=(
            "一份结构化的原始情报汇编，包含5W1H信息、官方声明列表、自媒体观点列表、"
            "社交媒体代表性评论、情绪分布统计。所有条目必须标注来源。"
        ),
        agent=scout,
    )

    # ---- Task 2: Challenger cross-examines the intel ----
    task_challenger = Task(
        description=(
            "情报官已经搜集了关于该事件的原始情报。现在请你发挥'杠精'本色，"
            "对每一条信息进行无情的交叉审查：\n\n"
            "**审查维度：**\n"
            "1. **信息一致性交叉验证**：将不同来源对同一事实的描述进行比对，标记一致/不一致/无法验证。\n"
            "2. **利益关联图绘制**：分析每一个发言方背后可能的经济、政治或流量利益。谁是受益者？谁是受害者？\n"
            "3. **逻辑谬误诊断**：逐一检查各方论证中的逻辑漏洞(稻草人、假两难、滑坡、诉诸情感、以偏概全等)。\n"
            "4. **水军/异常行为检测**：是否存在短时间内大量相似话术？是否存在与正常讨论模式不符的情绪极端化？\n"
            "5. **反讽与潜台词解读**：识别阴阳怪气、高级黑、反串等隐性表达的真实含义。\n\n"
            "**输出格式：**\n"
            "对每一方(官方、每个自媒体、评论区整体)给出：\n"
            "- 可信度评估(高/中/低 + 理由)\n"
            "- 利益相关度分析\n"
            "- 逻辑漏洞清单\n"
            "- 与其他来源的信息交叉验证结果"
        ),
        expected_output=(
            "一份详细的交叉审查报告，包含各方可信度评估、利益相关度分析、"
            "逻辑漏洞清单、以及信息交叉验证矩阵。"
        ),
        agent=challenger,
        context=[task_scout],
    )

    # ---- Task 3: Judge scores evidence and calculates truth probability ----
    task_judge = Task(
        description=(
            "审核员已经对情报进行了交叉审查。现在请你以法官的身份，"
            "基于贝叶斯推断框架，对事件核心争议点进行裁决：\n\n"
            "**评分维度：**\n"
            "1. **明确核心争议主张**：首先用一句话写出要评估的具体命题(如'XX品牌汽车存在设计缺陷导致车门无法打开')\n"
            "2. **证据链完整性评分** (0-100)：\n"
            "   - 该核心主张有几条独立的直接证据？\n"
            "   - 证据之间的因果链是否闭合？有无缺失环节？\n"
            "   - 证据来源的多样性如何？(单一来源 vs 多方印证)\n"
            "3. **贝叶斯真相概率计算**：\n"
            "   - 给出先验概率P(H)：基于常识和统计，类似事件中该主张为真的基础概率\n"
            "   - 给出似然比LR：每条证据对主张的支持/削弱程度\n"
            "   - 计算出后验概率P(H|E)：综合所有证据后，核心主张为真的概率\n"
            "4. **缺失证据清单**：\n"
            "   - 列出要确证或证伪该主张还需要的关键证据\n"
            "   - 说明这些证据应该从何处获取\n\n"
            "**重要：**\n"
            "- 必须在报告开头明确写出你正在评估的核心争议主张\n"
            "- 必须给出具体的百分比数字，不能含糊其辞\n"
            "- 必须说明计算逻辑，不能只给结论\n"
            "- 对无法验证的主张明确标注'待证实'"
        ),
        expected_output=(
            "一份包含以下内容的裁决报告：\n"
            "1. **核心争议主张**（明确写出要评估的命题，如'XX品牌汽车存在设计缺陷'）\n"
            "2. 该主张的证据链完整度评分(具体数字+理由)\n"
            "3. 贝叶斯推理过程(先验概率→似然比→后验概率)\n"
            "4. **综合真相可能概率**：该核心主张为真的后验概率(一个具体的百分比数字)\n"
            "5. 缺失的关键证据清单(至少3项)"
        ),
        agent=judge,
        context=[task_scout, task_challenger],
    )

    # ---- Task 4: Editor produces the final structured report ----
    task_editor = Task(
        description=(
            "情报官、审核员、法官已经完成了全部分析。现在轮到你——首席撰稿人——"
            "将所有分析整合为一份可供公众阅读的结构化透视报告。\n\n"
            "**你必须严格按以下格式输出(使用纯Markdown)：**\n\n"
            "```markdown\n"
            "# 🔍 AI资讯透视报告\n\n"
            "## 📌 事件概述\n"
            "[5W1H纯事实总结，每条事实标注来源。不使用任何主观修饰词]\n\n"
            "## 📊 真相透视表\n"
            "> 本表评估的核心主张是：「[从法官报告中提取核心争议主张]」。以下概率值表示该主张为真的可能性。\n\n"
            "| 指标 | 数值 |\n"
            "|------|------|\n"
            "| 真相可能概率 | XX% |\n"
            "| 证据链完整度 | XX/100 |\n"
            "| 信息交叉验证率 | XX% |\n\n"
            "**概率计算依据**：[法官的贝叶斯推理简述]\n"
            "**缺失的关键证据**：\n"
            "1. [证据1 — 说明从何处获取]\n"
            "2. [证据2]\n"
            "3. [证据3]\n\n"
            "## ⚖️ 各方观点对垒\n"
            "### 🏛️ 官方/权威方\n"
            "[核心说辞 + 支撑证据 + 置信度评分]\n\n"
            "### 📢 自媒体/KOL方\n"
            "[逐一列出：核心说辞 + 利益相关度分析 + 逻辑漏洞]\n\n"
            "### 💬 评论区舆情\n"
            "**情绪占比**：[angry/fearful/neutral/supportive/sarcastic等，给出百分比]\n"
            "**代表性神评**：[选取2-3条，分析其洞察价值]\n"
            "**反转信号**：[是否存在舆论反转的迹象]\n\n"
            "## 🔍 事实链条对齐\n"
            "### ✅ 已确认事实\n"
            "[多方交叉验证通过的事实，逐条标注来源]\n"
            "### ⚠️ 存疑点\n"
            "[证据不足或来源单一的说法]\n"
            "### ❌ 矛盾点\n"
            "[各方说法存在直接冲突的地方，列出冲突双方及其说辞]\n"
            "```\n\n"
            "**关键约束：**\n"
            "1. 任何数字、事实、百分比必须来自上游Agent的输出，严禁自行编造\n"
            "2. 每条事实性陈述必须带来源标记 [来源: xxx]\n"
            "3. 明确区分'事实'和'观点/推断'\n"
            "4. 不确定的地方标注'待证实'，不要强行得出结论"
        ),
        expected_output=(
            "一份完整的、格式规范的Markdown透视报告，包含事件概述、真相透视表、"
            "各方观点对垒、事实链条对齐四个核心板块。所有事实带来源标记。"
        ),
        agent=editor,
        context=[task_scout, task_challenger, task_judge],
    )

    return [task_scout, task_challenger, task_judge, task_editor]


def run_analysis(topic: str) -> str:
    """Run the full 4-agent debate pipeline on a given topic.

    Args:
        topic: The news event or topic to analyze.

    Returns:
        The final structured Markdown report from the Editor agent.
    """
    logger.info(f"Starting analysis pipeline for topic: {topic}")

    # Create all agents
    scout = create_scout_agent()
    challenger = create_challenger_agent()
    judge = create_judge_agent()
    editor = create_editor_agent()

    # Build tasks with proper context chaining
    tasks = _build_tasks(topic, scout, challenger, judge, editor)

    # Assemble crew in sequential mode
    crew = Crew(
        agents=[scout, challenger, judge, editor],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    logger.info("Crew assembled, kicking off execution...")
    result = crew.kickoff()

    logger.info("Analysis pipeline completed")
    return str(result)


# ---- Standalone test entry point ----
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "某品牌新能源车高速碰撞起火，车门无法打开致1死2伤"

    print(f"\n{'='*60}")
    print(f"运行分析流水线...")
    print(f"话题: {topic}")
    print(f"{'='*60}\n")

    report = run_analysis(topic)
    print("\n" + "=" * 60)
    print("最终报告:")
    print("=" * 60)
    print(report)
