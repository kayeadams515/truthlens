"""Report persistence — save and load generated reports."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from utils.logger import logger
from utils.paths import get_data_dir

DATA_DIR = get_data_dir() / "reports"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_report(topic: str, markdown_report: str, truth_prob: float | None = None) -> str:
    """Save a generated report to disk. Returns the report ID."""
    timestamp = datetime.now()
    report_id = timestamp.strftime("%Y%m%d_%H%M%S")
    filename = f"{report_id}.json"

    record = {
        "id": report_id,
        "topic": topic,
        "generated_at": timestamp.isoformat(),
        "markdown_report": markdown_report,
        "summary": markdown_report[:200],
    }
    if truth_prob is not None:
        record["truth_probability"] = truth_prob

    filepath = DATA_DIR / filename
    filepath.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Report saved: {filepath}")
    return report_id


def load_reports(limit: int = 20) -> list[dict]:
    """Load recent reports from disk, newest first."""
    reports = []
    if not DATA_DIR.exists():
        return reports

    for filepath in sorted(DATA_DIR.glob("*.json"), reverse=True):
        try:
            record = json.loads(filepath.read_text(encoding="utf-8"))
            reports.append(record)
            if len(reports) >= limit:
                break
        except Exception as e:
            logger.warning(f"Failed to load report {filepath}: {e}")

    return reports


def get_report(report_id: str) -> Optional[dict]:
    """Load a specific report by ID."""
    filepath = DATA_DIR / f"{report_id}.json"
    if not filepath.exists():
        return None
    try:
        return json.loads(filepath.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"Failed to load report {report_id}: {e}")
        return None


def report_exists(topic: str) -> bool:
    """Check if a report for this topic already exists (fuzzy match)."""
    for report in load_reports(limit=50):
        if topic[:20] in report.get("topic", ""):
            return True
    return False
