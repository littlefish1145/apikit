# APISTD 项目结构

## 核心架构

```
apikit/
├── apistd/                      # 统一导出模块（主要入口）
│   └── __init__.py              # 提供 from apistd import * 接口
│
├── core/                        # 核心功能层
│   ├── response.py              # 响应类（含 Rust/Python 智能选择）
│   │   ├── Response            # 基础响应类
│   │   ├── SuccessResponse     # 成功响应
│   │   ├── ErrorResponse       # 错误响应
│   │   ├── FastResponse        # 极速响应（__slots__ 优化）
│   │   ├── Success()           # 智能工厂函数
│   │   └── Error()             # 智能工厂函数
│   ├── exceptions.py            # 统一异常类
│   └── status.py                # HTTP 状态码常量
│
├── framework/                   # 框架适配层
│   ├── fastapi.py               # FastAPI 集成（含 Rust 加速）
│   ├── flask.py                 # Flask 集成（含 Rust 加速）
│   └── base.py                  # 基础适配器类
│
├── middleware/                  # 中间件层
│   ├── request_id.py            # Request ID 追踪
│   └── timer.py                 # 执行时间监控
│
├── formats/                     # 响应格式层
│   ├── registry.py              # 格式注册表
│   ├── standard.py              # 标准格式
│   └── alibaba.py               # 阿里格式
│
├── extensions/                  # 扩展功能层
│   ├── pagination.py            # 分页工具
│   └── validation.py            # 验证增强
│
├── config/                      # 配置管理层
│   └── default.py               # 默认配置
│
└── optimization/                # 性能优化层（可选）
    ├── __init__.py              # 导出优化组件
    ├── serializer/              # 序列化加速
    │   └── fast_json.py         # FastJSON 实现
    ├── backend/                 # 后端实现
    │   ├── __init__.py          # 后端选择器
    │   ├── rust_backend.py      # Python 包装模块
    │   └── rust_backend/        # Rust 源码
    │       ├── src/
    │       │   └── lib.rs       # Rust 核心实现
    │       ├── Cargo.toml       # Rust 依赖配置
    │       └── target/release/  # 编译产物
    │           └── rust_backend.dll/.so/.dylib
    └── cache/                   # 缓存优化
        └── lru.py               # LRU 缓存
```

## 核心执行流程

### 1. 响应创建流程

```
用户代码
    ↓
from apistd import Success
    ↓
Success(data)  # 智能工厂
    ↓
┌─────────────────────────────────┐
│ if RUST_AVAILABLE:              │
│   → RustResponse.success()      │  ← 1.52x 性能提升
│ else:                           │
│   → SuccessResponse()           │  ← Python 实现
└─────────────────────────────────┘
    ↓
Response Object
```

### 2. 序列化流程

```
Response.to_json()
    ↓
┌─────────────────────────────────┐
│ if RustResponse:                │
│   → serde_json (Rust)          │  ← 18% 更快
│ else:                           │
│   → orjson / ujson / json      │  ← Python 优化
└─────────────────────────────────┘
    ↓
JSON String
```

### 3. 框架集成流程

```
FastAPI / Flask App
    ↓
FastAPIAdapter / FlaskAdapter.install()
    ↓
注册异常处理器 + 中间件
    ↓
API Route Handler
    ↓
return Success(data)
    ↓
自动格式化为统一响应
```

## 性能优化层次

### Level 1: 智能选择（自动）
- `Success()` / `Error()` 工厂函数
- 自动选择 Rust 或 Python 实现
- 零配置，开箱即用

### Level 2: Rust 后端（推荐）
- `RustResponse` 类
- 零 Python 回调
- serde_json 序列化
- **1.52x 对象创建速度**
- **18% 序列化提升**

### Level 3: 极速模式（按需）
- `FastResponse` 类
- `__slots__` 优化
- 最小化 Python 开销
- 适用于性能敏感场景

### Level 4: 序列化优化（可选）
- `FastJSON` 自动选择
- Rust > orjson > ujson > json
- 根据环境自动降级

## 关键设计决策

### 1. 为什么使用智能工厂？
- **自动降级**: Rust 不可用时自动使用 Python
- **零配置**: 用户无需关心实现细节
- **向后兼容**: 现有代码无需修改

### 2. 为什么保留 Python 实现？
- **核心 DX**: APISTD 的核心价值是开发体验
- **可维护性**: Python 代码更易调试和扩展
- **跨平台**: 无需编译即可使用

### 3. Rust 的角色定位
- **性能加速**: 服务于 DX，不是核心
- **可选优化**: 不影响核心功能
- **零拷贝**: 大数据集优势明显

## 文件说明

### 核心文件
- `apistd/__init__.py`: 主要入口，统一导出
- `core/response.py`: 响应类 + 智能工厂
- `framework/fastapi.py`: FastAPI 适配器
- `framework/flask.py`: Flask 适配器

### 优化文件
- `optimization/backend/rust_backend.py`: Python 包装
- `optimization/backend/rust_backend/src/lib.rs`: Rust 源码
- `optimization/serializer/fast_json.py`: JSON 优化

### 构建文件
- `.github/workflows/build-rust.yml`: CI/CD 配置
- `build.sh`: Linux/macOS 构建脚本
- `build.bat`: Windows 构建脚本

## 依赖关系

```
apistd (顶层)
    ↓
core + framework + middleware (核心层)
    ↓
formats + extensions (扩展层)
    ↓
optimization (可选层)
    ↓
Rust Backend (性能层)
```

## 版本兼容性

- Python: 3.8+
- Rust: 1.70+
- PyO3: 0.20+
- FastAPI: 0.100+
- Flask: 2.0+

## 平台支持

✅ **完全支持**
- Linux x86_64
- Windows x86_64
- macOS x86_64

🔧 **需要测试**
- Linux ARM64
- macOS ARM64 (M1/M2)
- Windows ARM64
