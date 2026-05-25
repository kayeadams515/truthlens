"""CrewAI orchestrator — assembles the 4-agent debate pipeline."""

from __future__ import annotations

from crewai import Crew, Process, Task

from agents.scout import create_scout_agent
from agents.challenger import create_challenger_agent
from agents.judge import create_judge_agent
from agents.editor import create_editor_agent
from utils.logger import logger
from utils.i18n import t


def _build_tasks(
    topic: str,
    controversy_angle: str,
    existing_info: str,
    scout,
    challenger,
    judge,
    editor,
) -> list[Task]:
    """Build the 4 sequential tasks for the debate pipeline."""

    has_angle = bool(controversy_angle.strip()) if controversy_angle else False

    # ---- Task 1: Scout gathers raw intelligence ----
    if has_angle:
        scout_desc = t("task.crew.scout.with_angle", topic=topic, controversy_angle=controversy_angle, existing_info=existing_info)
        scout_expected = t("task.crew.scout.with_angle.expected")
    else:
        scout_desc = t("task.crew.scout", topic=topic)
        scout_expected = t("task.crew.scout.expected")

    task_scout = Task(
        description=scout_desc,
        expected_output=scout_expected,
        agent=scout,
    )

    # ---- Task 2: Challenger cross-examines the intel ----
    if has_angle:
        challenger_desc = t("task.crew.challenger.focused", controversy_angle=controversy_angle)
        challenger_expected = t("task.crew.challenger.focused.expected")
    else:
        challenger_desc = t("task.crew.challenger")
        challenger_expected = t("task.crew.challenger.expected")

    task_challenger = Task(
        description=challenger_desc,
        expected_output=challenger_expected,
        agent=challenger,
        context=[task_scout],
    )

    # ---- Task 3: Judge scores evidence and calculates truth probability ----
    task_judge = Task(
        description=t("task.crew.judge"),
        expected_output=t("task.crew.judge.expected"),
        agent=judge,
        context=[task_scout, task_challenger],
    )

    # ---- Task 4: Editor produces the final structured report ----
    task_editor = Task(
        description=t("task.crew.editor"),
        expected_output=t("task.crew.editor.expected"),
        agent=editor,
        context=[task_scout, task_challenger, task_judge],
    )

    return [task_scout, task_challenger, task_judge, task_editor]


def run_analysis(topic: str, controversy_angle: str = "", existing_info: str = "") -> str:
    """Run the full 4-agent debate pipeline on a given topic.

    Args:
        topic: The news event or topic to analyze.
        controversy_angle: Optional user-specified controversy angle to focus on.
        existing_info: Optional existing search results from info mode.

    Returns:
        The final structured Markdown report from the Editor agent.
    """
    logger.info(f"Starting analysis pipeline for topic: {topic}, has_angle: {bool(controversy_angle)}, has_existing_info: {bool(existing_info)}")

    # Create all agents
    scout = create_scout_agent()
    challenger = create_challenger_agent()
    judge = create_judge_agent()
    editor = create_editor_agent()

    # Build tasks with proper context chaining
    tasks = _build_tasks(topic, controversy_angle, existing_info, scout, challenger, judge, editor)

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
