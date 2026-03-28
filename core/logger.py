"""
FetchRouter Logging - 日志系统
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    配置日志系统

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，为 None 则只输出到控制台
        format_string: 自定义格式字符串

    Returns:
        配置好的 logger
    """
    logger = logging.getLogger("fetchrouter")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 清除现有处理器
    logger.handlers.clear()

    # 默认格式
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "fetchrouter") -> logging.Logger:
    """获取已配置的 logger"""
    return logging.getLogger(name)


class EmojiFormatter(logging.Formatter):
    """带 emoji 的日志格式器"""

    EMOJI_MAP = {
        "DEBUG": "🔍",
        "INFO": "ℹ️ ",
        "WARNING": "⚠️ ",
        "ERROR": "❌",
        "CRITICAL": "🚨",
    }

    def format(self, record: logging.LogRecord) -> str:
        emoji = self.EMOJI_MAP.get(record.levelname, "")
        record.emoji = emoji
        return super().format(record)


# 便捷的日志函数
def debug(msg: str, *args, **kwargs):
    """调试日志"""
    logging.getLogger("fetchrouter").debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """信息日志"""
    logging.getLogger("fetchrouter").info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """警告日志"""
    logging.getLogger("fetchrouter").warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """错误日志"""
    logging.getLogger("fetchrouter").error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """严重错误日志"""
    logging.getLogger("fetchrouter").critical(msg, *args, **kwargs)
