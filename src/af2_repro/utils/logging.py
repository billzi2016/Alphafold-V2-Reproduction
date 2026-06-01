"""日志工具模块。"""

from __future__ import annotations

import logging
from pathlib import Path


def get_logger(name: str, log_path: Path | None = None) -> logging.Logger:
    """返回一个基础 logger。

    这里统一控制日志格式，并支持可选的文件日志输出。
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_path is not None:
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger
