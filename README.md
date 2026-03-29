# apistd - API Response Standardization

让 Python Web 框架的 API 响应格式统一、可定制、易调试。

统一 FastAPI 和 Flask 的 API 响应格式，提供灵活的调试模式和自定义响应格式支持。

## 特性

- ✅ **统一响应格式**：为 FastAPI 和 Flask 提供一致的 API 响应格式
- ✅ **自定义格式**：支持注册自定义响应格式转换器
- ✅ **调试模式**：可选的增强调试信息（执行时间、内存使用、请求 ID）
- ✅ **错误处理**：标准化的错误响应，支持详细错误信息
- ✅ **分页支持**：内置分页功能
- ✅ **请求追踪**：自动添加请求 ID 和执行时间

## 安装

```bash
# 从源码安装
pip install -e .

# 安装 FastAPI 支持
pip install fastapi uvicorn

# 安装 Flask 支持
pip install flask
```

## 快速开始

### FastAPI 示例

```python
from fastapi import FastAPI
from apistd import (
    SuccessResponse, 
    FastAPIAdapter, 
    FormattedJSONResponse,
    configure
)
from core.exceptions import NotFoundError

app = FastAPI()

# 配置
configure(debug=False, enable_timing=True)

# 安装适配器
adapter = FastAPIAdapter()
adapter.install(app)

def json_response(response):
    return FormattedJSONResponse(content=response.to_dict(), status_code=response.code)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = get_user_from_db(user_id)  # 你的数据库查询
    if not user:
        raise NotFoundError(message=f"User {user_id} not found")
    
    return json_response(SuccessResponse(data=user, message="User found"))
```

### Flask 示例

```python
from flask import Flask
from apistd import (
    SuccessResponse,
    FlaskAdapter,
    configure
)
from core.exceptions import NotFoundError
from framework.flask import formatted_jsonify

app = Flask(__name__)

# 配置
configure(debug=False, enable_timing=True)

# 安装适配器
adapter = FlaskAdapter()
adapter.install(app)

def json_response(response):
    return formatted_jsonify(response.to_dict()), response.code

@app.route("/users/<int:user_id>")
def get_user(user_id):
    user = get_user_from_db(user_id)  # 你的数据库查询
    if not user:
        raise NotFoundError(message=f"User {user_id} not found")
    
    return json_response(SuccessResponse(data=user, message="User found"))
```

## 响应格式

### 默认响应结构

```json
{
  "code": 200,
  "message": "Success",
  "data": {...},
  "timestamp": 1234567890
}
```

### 错误响应

```json
{
  "code": 404,
  "message": "User not found",
  "data": null,
  "timestamp": 1234567890,
  "error_detail": {
    "type": "NotFoundError",
    "message": "User with id 5 not found"
  }
}
```

### Debug 模式响应

当 `debug=True` 时，响应会包含额外的调试信息：

```json
{
  "code": 200,
  "message": "Success",
  "data": {...},
  "timestamp": 1234567890,
  "_debug": {
    "execution_time_ms": 15.23,
    "memory_mb": 45.67,
    "request_id": "abc-123-def"
  }
}
```

## 配置选项

```python
from apistd import configure

configure(
    debug=False,                    # 启用调试模式
    enable_timing=True,            # 启用执行时间追踪
    slow_query_threshold=500,      # 慢查询阈值（毫秒）
    response_format="default",     # 响应格式名称
    request_id_header="X-Request-ID"  # 请求 ID 头部名称
)
```

## 自定义响应格式

```python
from apistd import register_format

def my_custom_format(code: int, message: str, data, debug_info: dict = None) -> dict:
    result = {
        "status": code,
        "msg": message,
        "result": data,
        "ts": int(time.time())
    }
    if debug_info:
        result["_debug"] = debug_info
    return result

# 注册自定义格式
register_format("my_custom", my_custom_format)

# 使用自定义格式
configure(response_format="my_custom")
```

## 内置异常类型

```python
from core.exceptions import (
    APIException,        # 基础异常
    ValidationError,     # 验证错误 (422)
    AuthenticationError, # 认证错误 (401)
    AuthorizationError,  # 授权错误 (403)
    NotFoundError,       # 资源不存在 (404)
    InternalError,       # 服务器错误 (500)
    DatabaseError        # 数据库错误 (500)
)

# 使用示例
raise NotFoundError(
    message="User not found",
    error_detail={"user_id": 123},
    context={"attempted_at": "2024-01-01"}
)
```

## 分页支持

```python
from apistd import paginate, PageResult

@app.get("/users")
async def list_users(page: int = 1, page_size: int = 10):
    items = get_users_from_db()  # 你的数据库查询
    result = paginate(items, total=100, page=page, page_size=page_size)
    
    return json_response(result.to_response())
```

分页响应：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10
  }
}
```

## 请求 ID 和执行时间

```python
from apistd import get_request_id, get_execution_time

@app.get("/debug")
async def debug_info():
    return json_response(SuccessResponse(
        data={
            "request_id": get_request_id(),
            "execution_time_ms": get_execution_time()
        }
    ))
```

## 运行示例

```bash
# 安装依赖
cd example
pip install -r requirements.txt

# 运行 FastAPI 示例
python fastapi_example.py
# 访问 http://localhost:8000

# 运行 Flask 示例
python flask_example.py
# 访问 http://localhost:5000
```

## 项目结构

```
apistd/
├── config/          # 配置管理
├── core/            # 核心功能（响应、异常、状态码）
├── debug/           # 调试工具
├── extensions/      # 扩展功能（分页、验证、数据库）
├── formats/         # 响应格式
├── framework/       # 框架适配器（FastAPI、Flask）
├── middleware/      # 中间件（请求 ID、计时器、调试）
├── migration/       # 迁移工具
├── example/         # 示例代码
└── README.md        # 本文档
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
