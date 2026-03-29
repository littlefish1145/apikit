import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from apistd import (
    Response, SuccessResponse, ErrorResponse,
    StatusCode, APIException,
    PageResult, paginate,
    FastAPIAdapter,
    configure,
    get_request_id, get_execution_time,
    RequestIDMiddleware, TimerMiddleware, DebugMiddleware
)
from apistd.core.exceptions import ValidationError, NotFoundError

app = FastAPI()

configure(debug=True, enable_timing=True, slow_query_threshold=500)

adapter = FastAPIAdapter()
adapter.install(app)


class User(BaseModel):
    id: int
    name: str
    email: str


class CreateUserRequest(BaseModel):
    name: str
    email: str


users_db = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
]


@app.get("/")
async def root():
    return SuccessResponse(
        data={"message": "Welcome to apistd FastAPI Example"},
        message="Welcome"
    )


@app.get("/users", response_model=Response)
async def list_users(page: int = 1, page_size: int = 10):
    start = (page - 1) * page_size
    end = start + page_size
    items = users_db[start:end]

    result = paginate(items, total=len(users_db), page=page, page_size=page_size)
    return result.to_response()


@app.get("/users/{user_id}", response_model=Response)
async def get_user(user_id: int):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise NotFoundError(message=f"User with id {user_id} not found")

    return SuccessResponse(data=user, message="User found")


@app.post("/users", response_model=Response)
async def create_user(req: CreateUserRequest):
    if not req.email or "@" not in req.email:
        raise ValidationError(
            message="Invalid email format",
            error_detail={"field": "email", "value": req.email}
        )

    new_id = max(u["id"] for u in users_db) + 1
    new_user = {"id": new_id, "name": req.name, "email": req.email}
    users_db.append(new_user)

    return SuccessResponse(data=new_user, message="User created", code=StatusCode.CREATED)


@app.delete("/users/{user_id}", response_model=Response)
async def delete_user(user_id: int):
    global users_db
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise NotFoundError(message=f"User with id {user_id} not found")

    users_db = [u for u in users_db if u["id"] != user_id]

    return SuccessResponse(data={"deleted": user_id}, message="User deleted")


@app.get("/debug/info")
async def debug_info(request: Request):
    return SuccessResponse(
        data={
            "request_id": get_request_id(),
            "execution_time_ms": get_execution_time(),
            "path": request.url.path,
            "method": request.method,
        },
        message="Debug info"
    )


@app.get("/error/sample")
async def sample_error():
    raise APIException(
        message="This is a sample error",
        code=1000,
        status_code=400,
        error_detail={"sample": "error detail"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
