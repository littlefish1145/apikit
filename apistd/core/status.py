from enum import IntEnum


class StatusCode(IntEnum):
    SUCCESS = 0
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503


class HTTPStatusMapper:
    @staticmethod
    def to_http_status(code: int) -> int:
        mapping = {
            0: 200,
            201: 201,
            202: 202,
            204: 204,
            400: 400,
            401: 401,
            403: 403,
            404: 404,
            405: 405,
            409: 409,
            422: 422,
            429: 429,
            500: 500,
            501: 501,
            503: 503,
        }
        return mapping.get(code, 500)

    @staticmethod
    def from_http_status(http_status: int) -> int:
        mapping = {
            200: 0,
            201: 201,
            202: 202,
            204: 204,
            400: 400,
            401: 401,
            403: 403,
            404: 404,
            405: 405,
            409: 409,
            422: 422,
            429: 429,
            500: 500,
            501: 501,
            503: 503,
        }
        return mapping.get(http_status, -1)
