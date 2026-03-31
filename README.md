# APISTD - 让 FastAPI/Flask 开发更简单

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-supported-green.svg)](https://fastapi.tiangolo.com/)
[![Flask](https://img.shields.io/badge/Flask-supported-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**统一的 API 响应标准 · 强大的调试工具 · 优雅的错误处理 · Rust 性能加速**

APISTD 是一个开发者体验（DX）增强框架，让 FastAPI 和 Flask 应用开发更简单、更规范、调试更方便。

---

## ✨ 核心特性

### 🎯 统一的 API 响应
- **标准化返回**: 统一的响应格式（code, message, data）
- **多格式支持**: 支持 standard、alibaba 等多种格式
- **类型安全**: 完整的类型注解

### 🐛 强大的调试
- **请求追踪**: 自动添加 Request ID
- **性能监控**: 执行时间、内存使用
- **调试面板**: 详细的调试信息
- **异常捕获**: 统一的错误处理

### 🔌 框架集成
- **FastAPI**: 完整支持（含 Rust 加速）
- **Flask**: 完整支持（含 Rust 加速）
- **可扩展**: 易于添加新框架

### 🧩 丰富扩展
- **分页支持**: 内置分页工具
- **数据验证**: 增强的验证功能
- **数据库**: 连接池管理

### ⚡ 性能优化（可选）
- **Rust 后端**: PyO3 实现的零拷贝序列化
- **FastJSON**: 自动选择最优 JSON 后端（Rust > orjson > ujson > json）
- **批量处理**: 大数据集性能优化
- **智能响应工厂**: 自动选择 Rust/Python 实现（1.5x 性能提升）

---

## 📦 安装

### 基础安装（仅核心功能）

```bash
pip install fastapi  # 或 flask
```

### 完整安装（含 Rust 加速）

#### 1. 从源码构建

```bash
# 克隆仓库
git clone https://github.com/apistd/apikit.git
cd apikit

# 安装 Python 依赖
pip install -e .

# 构建 Rust 后端
# Linux/macOS:
./build.sh

# Windows:
build.bat
```

#### 2. 使用预编译包

从 [GitHub Releases](https://github.com/apistd/apikit/releases) 下载对应平台的预编译库。

#### 3. 可选依赖

```bash
# 安装 orjson（备选优化）
pip install orjson
```

---

## 🎯 快速开始

### 统一导入接口

```python
from apistd import (
    SuccessResponse, ErrorResponse,
    APIException, ValidationError,
    FastAPIAdapter, FlaskAdapter,
    configure, get_request_id, get_execution_time
)
```

### FastAPI 示例

```python
from fastapi import FastAPI
from apistd import SuccessResponse, APIException, FastAPIAdapter, configure

app = FastAPI()

# 配置 APISTD
configure(debug=True, enable_timing=True)

# 安装适配器
adapter = FastAPIAdapter()
adapter.install(app)

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """获取用户信息"""
    return SuccessResponse(data={"user_id": user_id, "name": "Test"})

@app.post("/users")
async def create_user(name: str):
    """创建用户"""
    if not name:
        raise APIException(message="Name is required", status_code=400)
    return SuccessResponse(data={"name": name}, message="Created")
```

### Flask 示例

```python
from flask import Flask
from apistd import SuccessResponse, FlaskAdapter, configure

app = Flask(__name__)

# 配置 APISTD
configure(debug=True, enable_timing=True)

# 安装适配器
adapter = FlaskAdapter()
adapter.install(app)

@app.route('/users/<user_id>')
def get_user(user_id):
    return SuccessResponse(data={"user_id": user_id})
```

### 调试模式

```python
from apistd import configure

configure(
    debug=True,              # 开启调试模式
    response_format="standard",  # 响应格式：standard/alibaba
    request_id_header="X-Request-ID",
    enable_timing=True,      # 启用执行时间
    enable_optimization=True # 启用性能优化（Rust 后端）
)
```

---

## 📖 核心功能

### 1. 统一响应格式

#### SuccessResponse - 成功响应
```python
from apistd import SuccessResponse

# 简单用法
return SuccessResponse(data={"key": "value"})

# 自定义消息
return SuccessResponse(data=data, message="Operation successful")

# 自定义状态码
return SuccessResponse(data=data, code=201)
```

#### ErrorResponse - 错误响应
```python
from apistd import ErrorResponse

return ErrorResponse(
    message="Invalid input",
    code=400,
    error_detail={"field": "required"}
)
```

#### 响应格式
```python
# Standard 格式（默认）
{
    "code": 200,
    "message": "Success",
    "data": {...},
    "timestamp": 1234567890.123
}

# Alibaba 格式
{
    "Code": 200,
    "Message": "Success",
    "Data": {...},
    "RequestId": "xxx-xxx-xxx"
}
```

### 2. 统一异常处理

```python
from apistd import APIException, ValidationError, NotFoundError

# 抛出异常（自动捕获并格式化）
raise APIException(
    message="Resource not found",
    status_code=404,
    error_detail={"resource_id": "123"}
)

# 预定义异常
raise NotFoundError(message="User not found")
raise ValidationError(message="Invalid input")
raise AuthenticationError(message="Token expired")
```

### 3. 调试功能

#### 请求头信息
```
X-Request-ID: abc-123-def      # 请求追踪 ID
X-Execution-Time: 45.23ms      # 执行时间
X-Debug-Memory: 125.5MB        # 内存使用（debug 模式）
```

#### 获取调试信息
```python
from apistd import get_request_id, get_execution_time

@app.get("/debug")
async def debug_info():
    return SuccessResponse(data={
        "request_id": get_request_id(),
        "execution_time_ms": get_execution_time()
    })
```

### 4. 分页支持

```python
from apistd import PageResult, paginate

@app.get("/users")
async def list_users(page: int = 1, page_size: int = 20):
    users = get_users(page, page_size)
    
    result = paginate(users, total=100, page=page, page_size=page_size)
    return SuccessResponse(data=result)
```

### 5. 性能优化（可选）

```python
from apistd import FastJSON, OPTIMIZATION_AVAILABLE

if OPTIMIZATION_AVAILABLE:
    # 使用 Rust 加速的 JSON 序列化
    json_serializer = FastJSON()
    json_bytes = json_serializer.dumps(large_data)
```

### 6. Rust 智能响应（超快）

```python
from apistd import Success, Error, RustResponse

# 智能工厂 - 自动使用 Rust（如果可用）
resp = Success(data={"key": "value"})  # 自动使用 RustResponse

# 手动指定
resp = Success(data=data, use_rust=True)  # 强制使用 Rust
resp = Success(data=data, use_rust=False)  # 强制使用 Python

# 直接使用 RustResponse
resp = RustResponse.success(data=data, message="Success")
json_str = resp.to_json()  # 超快序列化
```

---

## 🏗️ 项目结构

```
apikit/
├── apistd/                  # 统一导出模块
│   └── __init__.py          # 便捷导入接口
├── core/                    # 核心功能
│   ├── response.py          # 统一响应类（Rust 加速）
│   ├── exceptions.py        # 统一异常类
│   └── status.py            # 状态码定义
├── framework/               # 框架适配层
│   ├── fastapi.py           # FastAPI 集成（Rust 加速）
│   ├── flask.py             # Flask 集成（Rust 加速）
│   └── base.py              # 基础适配器
├── middleware/              # 中间件
│   ├── request_id.py        # 请求 ID 追踪
│   └── timer.py             # 性能计时
├── formats/                 # 响应格式
│   ├── registry.py          # 格式注册表
│   ├── standard.py          # 标准格式
│   └── alibaba.py           # 阿里格式
├── extensions/              # 扩展功能
│   ├── pagination.py        # 分页
│   └── validation.py        # 验证增强
├── config/                  # 配置管理
│   └── default.py           # 默认配置
└── optimization/            # 性能优化（可选）
    ├── serializer/          # 序列化加速
    │   └── fast_json.py     # FastJSON 实现
    └── backend/             # Rust 后端
        └── rust_backend/    # PyO3 实现
```

---

## 🔧 高级用法

### 自定义响应格式

```python
from apistd import register_format

def my_custom_formatter(code: int, message: str, data, debug_info=None) -> dict:
    return {
        "status": code,
        "msg": message,
        "result": data,
        "ts": int(time.time())
    }

register_format("my_custom", my_custom_formatter)
configure(response_format="my_custom")
```

### 自定义异常

```python
from apistd import APIException

class UserNotFoundException(APIException):
    status_code = 404
    
    def __init__(self, user_id: str):
        super().__init__(
            message=f"User {user_id} not found",
            error_detail={"user_id": user_id}
        )

# 使用
raise UserNotFoundException("123")
```

### 使用 FormattedJSONResponse（FastAPI）

```python
from apistd import FormattedJSONResponse, SuccessResponse

@app.get("/")
async def root():
    response = SuccessResponse(data={"message": "Hello"})
    return FormattedJSONResponse(content=response.to_dict())
```

---

## 📊 调试模式 vs 生产模式

### Debug=True
```json
{
    "code": 404,
    "message": "Not found",
    "data": null,
    "timestamp": 1234567890.123,
    "_debug": {
        "memory_mb": 125.5,
        "cpu_percent": 12.3,
        "execution_time_ms": 45.23,
        "request_id": "abc-123-def"
    }
}
```

### Debug=False
```json
{
    "code": 404,
    "message": "Not found",
    "data": null
}
```

---

## 🆚 与其他框架对比

| 特性 | APISTD | FastAPI 原生 | Flask 原生 |
|------|--------|------------|-----------|
| **统一响应格式** | ✅ | ❌ | ❌ |
| **异常自动处理** | ✅ | 部分 | ❌ |
| **请求追踪** | ✅ | ❌ | ❌ |
| **调试面板** | ✅ | ❌ | ❌ |
| **多格式支持** | ✅ | ❌ | ❌ |
| **开箱即用** | ✅ | ❌ | ❌ |
| **Rust 加速** | ✅ | ❌ | ❌ |

---

## 📝 最佳实践

### 1. 始终使用统一响应
```python
# ✅ 推荐
return SuccessResponse(data=user)

# ❌ 不推荐
return {"user": user}
```

### 2. 使用异常而非错误码
```python
# ✅ 推荐
raise NotFoundError(message="User not found")

# ❌ 不推荐
return {"error": "not found", "code": 404}
```

### 3. 开发时开启 Debug
```python
configure({"debug": True})  # 开发环境
configure({"debug": False}) # 生产环境
```

### 4. 使用 Request ID 追踪
```python
# 所有响应自动包含 X-Request-ID
# 便于日志追踪和调试
```

### 5. 启用性能优化
```python
# 生产环境建议启用
configure(enable_optimization=True)
```

---

## 🧪 测试

```bash
# 运行示例
python example/flask_example.py
python example/fastapi_example.py

# 运行测试
python tests/test_init.py

# 性能基准（可选）
python tests/test_performance.py
```

---

## 📚 API 参考

### Core
- `Response` - 基础响应类
- `SuccessResponse` - 成功响应
- `ErrorResponse` - 错误响应
- `APIException` - 统一异常
- `ValidationError` - 验证错误
- `NotFoundError` - 未找到错误
- `StatusCode` - 状态码常量

### Framework
- `FastAPIAdapter` - FastAPI 集成
- `FlaskAdapter` - Flask 集成
- `FormattedJSONResponse` - FastAPI 格式化响应

### Extensions
- `PageResult` - 分页结果
- `paginate` - 分页工具函数

### Config
- `configure` - 配置函数
- `get_config` - 获取配置

### Middleware
- `get_request_id` - 获取请求 ID
- `get_execution_time` - 获取执行时间

### Format Registry
- `ResponseFormatterRegistry` - 格式注册表
- `register_format` - 注册格式函数

### Optimization (Optional)
- `FastJSON` - 快速 JSON 序列化
- `OPTIMIZATION_AVAILABLE` - 优化模块是否可用

### Rust Backend (Optional - High Performance)
- `RustResponse` - Rust 实现的响应类（零 Python 开销）
- `RUST_AVAILABLE` - Rust 后端是否可用
- `Success` - 智能成功响应工厂（自动选择 Rust/Python）
- `Error` - 智能错误响应工厂（自动选择 Rust/Python）

---

## 🎯 适用场景

### ✅ 适合
- 需要统一 API 风格的项目
- 需要快速开发的创业公司
- 需要强大调试功能的团队
- 多框架混合使用的环境
- 对性能有要求的场景（启用 Rust 后端）

### ❌ 不适合
- 已有完整框架体系的项目
- 不需要统一响应规范的项目

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

```bash
git clone https://github.com/apistd/apikit.git
cd apikit
pip install -e .
```

---

## 📧 联系方式

- **GitHub**: https://github.com/apistd
- **文档**: https://apistd.github.io/docs
- **问题**: https://github.com/apistd/apikit/issues

---

**APISTD - 让 API 开发更简单！** 🚀
