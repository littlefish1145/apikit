class ResponseFields:
    CODE = "code"
    MESSAGE = "message"
    DATA = "data"
    TIMESTAMP = "timestamp"
    ERROR_DETAIL = "error_detail"
    REQUEST_ID = "request_id"
    EXECUTION_TIME = "execution_time"


class ErrorCodes:
    SUCCESS = 0
    UNKNOWN_ERROR = -1
    VALIDATION_ERROR = 1001
    AUTH_ERROR = 1002
    NOT_FOUND = 1004
    INTERNAL_ERROR = 5000


class ConfigKeys:
    DEBUG = "debug"
    REQUEST_ID_HEADER = "request_id_header"
    ENABLE_TIMING = "enable_timing"
    ENABLE_SQL_LOG = "enable_sql_log"
    SLOW_QUERY_THRESHOLD = "slow_query_threshold"
    RESPONSE_FORMATTER = "response_formatter"
    BEFORE_HOOKS = "before_hooks"
    AFTER_HOOKS = "after_hooks"
    TIMESTAMP_FORMAT = "timestamp_format"
    TIMEZONE = "timezone"
