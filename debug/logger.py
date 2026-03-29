import logging
from typing import Any, Optional


class DebugLogger:
    def __init__(self, name: str = "apistd"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)

    def debug(self, message: str, **kwargs) -> None:
        extra = {"extra": kwargs} if kwargs else {}
        self.logger.debug(message, **extra)

    def info(self, message: str, **kwargs) -> None:
        extra = {"extra": kwargs} if kwargs else {}
        self.logger.info(message, **extra)

    def warning(self, message: str, **kwargs) -> None:
        extra = {"extra": kwargs} if kwargs else {}
        self.logger.warning(message, **extra)

    def error(self, message: str, **kwargs) -> None:
        extra = {"extra": kwargs} if kwargs else {}
        self.logger.error(message, **extra)


class SQLDebugLogger(DebugLogger):
    def log_query(self, query: str, duration: float, params: Any = None) -> None:
        self.debug(f"SQL Query ({duration:.2f}ms): {query}", params=params)

    def log_slow_query(self, query: str, duration: float, params: Any = None) -> None:
        self.warning(f"Slow SQL Query ({duration:.2f}ms): {query}", params=params)
