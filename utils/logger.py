"""Structured logging for Vision Lens."""

import sys
from loguru import logger
from utils.paths import get_data_dir

logger.remove()
logger.add(
    sys.stderr,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
)

_log_dir = get_data_dir() / "logs"
_log_dir.mkdir(parents=True, exist_ok=True)
logger.add(
    str(_log_dir / "vision_lens_{time:YYYY-MM-DD}.log"),
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
)

__all__ = ["logger"]
