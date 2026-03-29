from typing import Any, List, Optional
from apistd.core.response import ErrorResponse


class ValidationErrorFormatter:
    @staticmethod
    def format(error: Exception) -> ErrorResponse:
        return ErrorResponse(
            message=str(error) or "Validation failed",
            code=1001,
            error_detail={"type": type(error).__name__}
        )

    @staticmethod
    def format_pydantic(errors: List[dict]) -> ErrorResponse:
        formatted_errors = []
        for error in errors:
            formatted_errors.append({
                "loc": error.get("loc", []),
                "msg": error.get("msg", ""),
                "type": error.get("type", ""),
            })

        return ErrorResponse(
            message="Validation failed",
            code=1001,
            error_detail={"errors": formatted_errors}
        )

    @staticmethod
    def format_custom(validator_name: str, message: str, **kwargs) -> ErrorResponse:
        return ErrorResponse(
            message=message,
            code=1001,
            error_detail={
                "validator": validator_name,
                **kwargs
            }
        )
