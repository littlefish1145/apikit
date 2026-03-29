from typing import Any, Dict, Optional
from apistd.core.response import Response, SuccessResponse, ErrorResponse
from apistd.core.constants import ResponseFields


class ResponseAdapter:
    def __init__(
        self,
        old_key_map: Dict[str, str] = None,
        new_key_map: Dict[str, str] = None
    ):
        self.old_key_map = old_key_map or {}
        self.new_key_map = new_key_map or {}

    def convert(self, old_response: Any) -> Response:
        if isinstance(old_response, Response):
            return old_response

        if isinstance(old_response, dict):
            new_data = {}
            for old_key, new_key in self.old_key_map.items():
                if old_key in old_response:
                    new_data[new_key] = old_response[old_key]

            for key, value in old_response.items():
                if key not in self.old_key_map:
                    new_data[key] = value

            if ResponseFields.CODE not in new_data:
                new_data[ResponseFields.CODE] = 0

            return Response.from_dict(new_data)

        return SuccessResponse(data=old_response)

    def adapt(self, new_response: Response, old_format: str = None) -> Any:
        result = new_response.to_dict()

        adapted = {}
        for new_key, old_key in self.new_key_map.items():
            if new_key in result:
                adapted[old_key] = result[new_key]

        for key, value in result.items():
            if key not in self.new_key_map:
                adapted[key] = value

        if old_format:
            adapted["_format"] = old_format

        return adapted


class FormatConverter:
    @staticmethod
    def to_apistd_format(data: Dict, mapping: Dict[str, str] = None) -> Response:
        if mapping:
            mapped = {}
            for old_key, new_key in mapping.items():
                if old_key in data:
                    mapped[new_key] = data[old_key]

            if ResponseFields.CODE not in mapped:
                mapped[ResponseFields.CODE] = 0

            return Response.from_dict(mapped)

        if ResponseFields.CODE not in data:
            data[ResponseFields.CODE] = 0

        return Response.from_dict(data)

    @staticmethod
    def from_apistd_format(response: Response, format_name: str = None) -> Dict:
        result = response.to_dict()

        if format_name == "simple":
            return {
                "code": result.get(ResponseFields.CODE),
                "data": result.get(ResponseFields.DATA),
            }
        elif format_name == "detailed":
            return result

        return result
