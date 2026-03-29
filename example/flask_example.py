import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from flask import Flask, request

from apistd import (
    SuccessResponse, ErrorResponse,
    StatusCode, APIException,
    PageResult, paginate,
    FlaskAdapter,
    configure, get_config,
    get_request_id, get_execution_time,
    register_format, ResponseFormatterRegistry
)
from apistd.core.exceptions import ValidationError, NotFoundError, DatabaseError
from apistd.framework.flask import formatted_jsonify

app = Flask(__name__)


def my_custom_formatter(code: int, message: str, data, debug_info: dict = None) -> dict:
    result = {
        "status": code,
        "msg": message,
        "result": data,
        "ts": int(time.time())
    }
    if debug_info:
        result["_debug"] = debug_info
    return result


register_format("my_custom", my_custom_formatter)

configure(debug=False, enable_timing=True, slow_query_threshold=500, response_format="my_custom")

adapter = FlaskAdapter()
adapter.install(app)


users_db = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
]


def json_response(response):
    return formatted_jsonify(response.to_dict()), response.code


@app.route("/")
def root():
    return json_response(SuccessResponse(
        data={"message": "Welcome to apistd Flask Example"},
        message="Welcome"
    ))


@app.route("/users", methods=["GET"])
def list_users():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))

    start = (page - 1) * page_size
    end = start + page_size
    items = users_db[start:end]

    result = paginate(items, total=len(users_db), page=page, page_size=page_size)
    return json_response(result.to_response())


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise NotFoundError(message=f"User with id {user_id} not found")

    return json_response(SuccessResponse(data=user, message="User found"))


@app.route("/users", methods=["POST"])
def create_user():
    req = request.get_json()
    name = req.get("name")
    email = req.get("email")

    if not email or "@" not in email:
        raise ValidationError(
            message="Invalid email format",
            error_detail={"field": "email", "value": email}
        )

    new_id = max(u["id"] for u in users_db) + 1
    new_user = {"id": new_id, "name": name, "email": email}
    users_db.append(new_user)

    return json_response(SuccessResponse(data=new_user, message="User created", code=StatusCode.CREATED))


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    global users_db
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise NotFoundError(message=f"User with id {user_id} not found")

    users_db = [u for u in users_db if u["id"] != user_id]

    return json_response(SuccessResponse(data={"deleted": user_id}, message="User deleted"))


@app.route("/debug/info", methods=["GET"])
def debug_info():
    return json_response(SuccessResponse(
        data={
            "request_id": get_request_id(),
            "execution_time_ms": get_execution_time(),
            "path": request.path,
            "method": request.method,
        },
        message="Debug info"
    ))


@app.route("/error/db", methods=["GET"])
def db_error():
    raise DatabaseError(
        message="Database connection failed",
        error_detail={
            "type": "ConnectionError",
            "file": "database.py",
            "line": 42,
            "function": "connect_db"
        },
        context={
            "db_host": "localhost:5432",
            "db_name": "prod_db",
            "attempt": 3
        }
    )


@app.route("/error/sample", methods=["GET"])
def sample_error():
    raise APIException(
        message="This is a sample error",
        code=400,
        status_code=400,
        error_detail={"sample": "error detail"}
    )


@app.route("/config", methods=["GET"])
def show_config():
    cfg = get_config()
    return json_response(SuccessResponse(
        data={
            "response_format": cfg.response_format,
            "available_formats": ResponseFormatterRegistry.list_formatters(),
            "debug": cfg.debug,
        },
        message="Current config"
    ))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
