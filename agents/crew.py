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
    intent: str,
    scout,
    challenger,
    judge,
    editor,
    available_images_text: str = "",
) -> list[Task]:
    """Build the debate pipeline tasks. 3 tasks for debate_understanding, 4 for truth_seeking."""

    has_angle = bool(controversy_angle.strip()) if controversy_angle else False
    is_truth_seeking = (intent == "truth_seeking")

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

    # Build Editor description, appending image context if available
    if is_truth_seeking:
        # ---- Task 3: Judge scores evidence and calculates truth probability ----
        task_judge = Task(
            description=t("task.crew.judge"),
            expected_output=t("task.crew.judge.expected"),
            agent=judge,
            context=[task_scout, task_challenger],
        )

        # ---- Task 4: Editor produces the final structured report with truth probability ----
        editor_desc = t("task.crew.editor")
        if available_images_text:
            editor_desc += "\n\n" + available_images_text
        task_editor = Task(
            description=editor_desc,
            expected_output=t("task.crew.editor.expected"),
            agent=editor,
            context=[task_scout, task_challenger, task_judge],
        )

        return [task_scout, task_challenger, task_judge, task_editor]
    else:
        # ---- Task 3: Editor produces debate landscape report (no Judge) ----
        editor_desc = t("task.crew.editor.debate_map")
        if available_images_text:
            editor_desc += "\n\n" + available_images_text
        task_editor = Task(
            description=editor_desc,
            expected_output=t("task.crew.editor.debate_map.expected"),
            agent=editor,
            context=[task_scout, task_challenger],
        )

        return [task_scout, task_challenger, task_editor]


def run_analysis(topic: str, controversy_angle: str = "", existing_info: str = "",
                  intent: str = "debate_understanding", available_images_text: str = "") -> str:
    """Run the adaptive debate pipeline on a given topic.

    Args:
        topic: The news event or topic to analyze.
        controversy_angle: Optional user-specified controversy angle to focus on.
        existing_info: Optional existing search results from info mode.
        intent: "debate_understanding" (3 agents, no truth probability) or
                "truth_seeking" (4 agents, full Bayesian pipeline).
        available_images_text: Optional formatted image list for the Editor agent.

    Returns:
        The final structured Markdown report from the Editor agent.
    """
    logger.info(f"Starting analysis pipeline: topic={topic[:40]}, intent={intent}, "
                f"has_angle={bool(controversy_angle)}, has_existing_info={bool(existing_info)}, "
                f"has_images={bool(available_images_text)}")

    # Create agents
    scout = create_scout_agent()
    challenger = create_challenger_agent()
    judge = create_judge_agent() if intent == "truth_seeking" else None
    editor = create_editor_agent()

    # Build tasks with proper context chaining
    tasks = _build_tasks(topic, controversy_angle, existing_info, intent,
                         scout, challenger, judge, editor, available_images_text)

    # Assemble crew in sequential mode
    agents = [scout, challenger, editor]
    if judge is not None:
        agents.insert(2, judge)  # Judge before Editor

    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    logger.info(f"Crew assembled ({len(agents)} agents, {len(tasks)} tasks), kicking off...")
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
