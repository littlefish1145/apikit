from abc import ABC, abstractmethod
from typing import Any


class FrameworkAdapter(ABC):
    @abstractmethod
    def install(self, app: Any, config: dict = None) -> None:
        pass

    @abstractmethod
    def response_handler(self, response: Any) -> Any:
        pass

    @abstractmethod
    def error_handler(self, exception: Exception) -> Any:
        pass
