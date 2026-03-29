import time
import logging
from typing import Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("apistd")


@dataclass
class QueryLog:
    query: str
    duration: float
    params: Any = None
    timestamp: float = field(default_factory=time.time)


class SQLLogger:
    def __init__(self, threshold_ms: float = 100):
        self.threshold_ms = threshold_ms
        self.queries: List[QueryLog] = []

    def log_query(self, query: str, duration: float, params: Any = None) -> None:
        query_log = QueryLog(query=query, duration=duration, params=params)
        self.queries.append(query_log)

        if duration > self.threshold_ms:
            logger.warning(
                f"Slow query detected ({duration:.2f}ms): {query[:100]}..."
            )

    def get_slow_queries(self) -> List[QueryLog]:
        return [q for q in self.queries if q.duration > self.threshold_ms]

    def clear(self) -> None:
        self.queries.clear()


class DatabaseExtension:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.sql_logger = SQLLogger(
            threshold_ms=self.config.get("slow_query_threshold", 100)
        )

    def install(self, app: Any) -> None:
        logger.info("DatabaseExtension installed")
