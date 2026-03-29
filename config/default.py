from typing import Callable, List, Any, Optional
from dataclasses import dataclass, field


DEFAULT_CONFIG = {
    "debug": False,
    "request_id_header": "X-Request-ID",
    "enable_timing": True,
    "enable_sql_log": False,
    "slow_query_threshold": 100,
    "response_format": "default",
    "before_hooks": [],
    "after_hooks": [],
    "timestamp_format": "iso",
    "timezone": "UTC",
}


@dataclass
class ConfigSchema:
    debug: bool = False
    request_id_header: str = "X-Request-ID"
    enable_timing: bool = True
    enable_sql_log: bool = False
    slow_query_threshold: float = 100
    response_format: str = "default"
    before_hooks: List[Callable] = field(default_factory=list)
    after_hooks: List[Callable] = field(default_factory=list)
    timestamp_format: str = "iso"
    timezone: str = "UTC"

    def to_dict(self) -> dict:
        return {
            "debug": self.debug,
            "request_id_header": self.request_id_header,
            "enable_timing": self.enable_timing,
            "enable_sql_log": self.enable_sql_log,
            "slow_query_threshold": self.slow_query_threshold,
            "response_format": self.response_format,
            "before_hooks": self.before_hooks,
            "after_hooks": self.after_hooks,
            "timestamp_format": self.timestamp_format,
            "timezone": self.timezone,
        }


def validate_config(config: dict) -> ConfigSchema:
    schema = ConfigSchema()
    for key, value in config.items():
        if hasattr(schema, key):
            setattr(schema, key, value)
    return schema


_config: ConfigSchema = ConfigSchema()


def configure(**kwargs) -> None:
    global _config
    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)


def get_config() -> ConfigSchema:
    return _config
