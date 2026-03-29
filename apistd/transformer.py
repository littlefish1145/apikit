from typing import Any, Dict, Callable, Optional
from apistd.core.response import Response, SuccessResponse, ErrorResponse
from apistd.core.constants import ResponseFields


class ResponseTransformer:
    def __init__(self):
        self._converters: Dict[str, Callable] = {}

    def register(self, format_name: str, converter: Callable):
        self._converters[format_name] = converter

    def transform(self, data: Any, source_format: str = None) -> Response:
        if isinstance(data, Response):
            return data

        if source_format and source_format in self._converters:
            return self._converters[source_format](data)

        return self._auto_detect_and_convert(data)

    def _auto_detect_and_convert(self, data: Any) -> Response:
        if isinstance(data, dict):
            return self._convert_dict(data)
        elif isinstance(data, (list, tuple)):
            return SuccessResponse(data=data)
        else:
            return SuccessResponse(data=str(data))

    def _convert_dict(self, data: Dict) -> Response:
        code = data.get(ResponseFields.CODE)
        if code is not None:
            if code >= 400:
                return ErrorResponse(
                    message=data.get(ResponseFields.MESSAGE, "Error"),
                    code=code,
                    error_detail=data.get(ResponseFields.ERROR_DETAIL)
                )
            return SuccessResponse(
                data=data.get(ResponseFields.DATA),
                message=data.get(ResponseFields.MESSAGE, "Success"),
                code=code
            )

        if "status" in data and "msg" in data:
            return self._convert_ali_style(data)
        if "code" in data and "message" in data:
            return self._convert_standard_style(data)
        if "ret" in data and "data" in data:
            return self._convert_ret_data_style(data)

        return SuccessResponse(data=data)

    def _convert_ali_style(self, data: Dict) -> Response:
        code = data.get("status", 200)
        msg = data.get("msg", "success")
        result = data.get("result")

        if code >= 400:
            return ErrorResponse(message=msg, code=code)
        return SuccessResponse(data=result, message=msg, code=code)

    def _convert_standard_style(self, data: Dict) -> Response:
        code = data.get("code", 200)
        message = data.get("message", "Success")
        resp_data = data.get("data")

        if code >= 400:
            return ErrorResponse(message=message, code=code)
        return SuccessResponse(data=resp_data, message=message, code=code)

    def _convert_ret_data_style(self, data: Dict) -> Response:
        ret = data.get("ret", 0)
        msg = data.get("msg", "Success")
        resp_data = data.get("data")

        if ret != 0:
            return ErrorResponse(message=msg, code=ret)
        return SuccessResponse(data=resp_data, message=msg, code=200)


_transformer = ResponseTransformer()


def register_format(name: str, converter: Callable):
    _transformer.register(name, converter)


def transform(data: Any, source_format: str = None) -> Response:
    return _transformer.transform(data, source_format)
