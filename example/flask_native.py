"""
纯 Flask 示例 - 不使用 APISTD

这个示例展示了如何使用原生 Flask 实现与 APISTD 相同的功能，
用于对比 APISTD 带来的便利性和性能优势。
"""

from flask import Flask, jsonify, request, g
import time
import uuid
from functools import wraps

app = Flask(__name__)

# ============================================================================
# 1. 手动实现统一响应格式（APISTD 的 SuccessResponse/ErrorResponse）
# ============================================================================

def success_response(data, message="Success", code=200):
    """手动实现成功响应格式"""
    return jsonify({
        "code": code,
        "message": message,
        "data": data,
        "timestamp": time.time()
    }), code

def error_response(message, code=500, error_detail=None):
    """手动实现错误响应格式"""
    response_data = {
        "code": code,
        "message": message,
        "data": None
    }
    if error_detail:
        response_data["error_detail"] = error_detail
    return jsonify(response_data), code

# ============================================================================
# 2. 手动实现 Request ID 中间件（APISTD 的 RequestIDMiddleware）
# ============================================================================

@app.before_request
def before_request():
    """请求前处理：添加 Request ID 和开始计时"""
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()

@app.after_request
def after_request(response):
    """请求后处理：添加 Request ID 和 Execution Time 到响应头"""
    response.headers['X-Request-ID'] = getattr(g, 'request_id', 'N/A')
    
    # 计算执行时间
    if hasattr(g, 'start_time'):
        execution_time = (time.time() - g.start_time) * 1000  # 毫秒
        response.headers['X-Execution-Time'] = f"{execution_time:.2f}ms"
    
    return response

# ============================================================================
# 3. 手动实现全局异常处理（APISTD 的异常处理）
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return error_response("Resource not found", code=404)

@app.errorhandler(500)
def internal_error(error):
    return error_response("Internal server error", code=500)

@app.errorhandler(Exception)
def handle_exception(error):
    """全局异常处理器"""
    # 生产环境应该记录日志
    # app.logger.error(f"Error: {error}")
    return error_response(str(error), code=500)

# ============================================================================
# 4. 手动实现数据验证（APISTD 的验证功能）
# ============================================================================

def validate_json(*required_fields):
    """装饰器：验证 JSON 请求体"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return error_response("Content-Type must be application/json", code=400)
            
            data = request.get_json()
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return error_response(
                    f"Missing required fields: {', '.join(missing_fields)}",
                    code=400
                )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============================================================================
# 5. API 路由（与 APISTD 版本功能一致）
# ============================================================================

# 模拟数据库
users_db = {
    "1": {"id": "1", "name": "Alice", "email": "alice@example.com"},
    "2": {"id": "2", "name": "Bob", "email": "bob@example.com"},
    "3": {"id": "3", "name": "Charlie", "email": "charlie@example.com"},
    "4": {"id": "4", "name": "David", "email": "david@example.com"},
    "5": {"id": "5", "name": "Eve", "email": "eve@example.com"},
}

@app.route('/users', methods=['GET'])
def get_users():
    """获取所有用户"""
    return success_response({
        "users": list(users_db.values()),
        "total": len(users_db)
    })

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户"""
    user = users_db.get(user_id)
    
    if not user:
        return error_response(f"User {user_id} not found", code=404)
    
    return success_response(user)

@app.route('/users', methods=['POST'])
@validate_json('name', 'email')
def create_user():
    """创建用户"""
    data = request.get_json()
    
    # 生成新 ID
    new_id = str(max(int(uid) for uid in users_db.keys()) + 1)
    
    # 创建用户
    new_user = {
        "id": new_id,
        "name": data['name'],
        "email": data['email']
    }
    users_db[new_id] = new_user
    
    return success_response(new_user, message="User created successfully", code=201)

@app.route('/users/<user_id>', methods=['PUT'])
@validate_json('name', 'email')
def update_user(user_id):
    """更新用户"""
    if user_id not in users_db:
        return error_response(f"User {user_id} not found", code=404)
    
    data = request.get_json()
    
    # 更新用户
    users_db[user_id].update({
        "name": data['name'],
        "email": data['email']
    })
    
    return success_response(users_db[user_id], message="User updated successfully")

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    if user_id not in users_db:
        return error_response(f"User {user_id} not found", code=404)
    
    del users_db[user_id]
    return success_response(None, message=f"User {user_id} deleted successfully")

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return success_response({
        "status": "healthy",
        "timestamp": time.time()
    })

# ============================================================================
# 6. 启动应用
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("纯 Flask 示例 - 不使用 APISTD")
    print("=" * 70)
    print("\n对比 APISTD 版本，这个示例需要:")
    print("1. 手动实现统一响应格式函数")
    print("2. 手动实现 Request ID 中间件")
    print("3. 手动实现全局异常处理")
    print("4. 手动实现数据验证装饰器")
    print("5. 每个路由都要手动调用响应函数")
    print("\n而使用 APISTD，这些都可以简化为:")
    print("  from apistd import Success, FlaskAdapter")
    print("  adapter = FlaskAdapter()")
    print("  adapter.install(app)")
    print("  return Success(data=user)")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
