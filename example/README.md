# FastAPI Example with apistd

## Installation

```bash
pip install -r requirements.txt
pip install -e ..
```

## Run

```bash
cd example
python fastapi_example.py
```

Server will start at http://localhost:8000

## API Endpoints

### GET /
Welcome message

### GET /users?page=1&page_size=10
List users with pagination

### GET /users/{user_id}
Get a single user by ID

### POST /users
Create a new user
```json
{
    "name": "John",
    "email": "john@example.com"
}
```

### DELETE /users/{user_id}
Delete a user

### GET /debug/info
Get debug information (request_id, execution_time)

### GET /error/sample
Sample error response

## Response Format

All responses follow the unified apistd format:

```json
{
    "code": 0,
    "message": "Success",
    "data": { ... },
    "timestamp": 1234567890.123
}
```

Error responses:

```json
{
    "code": -1,
    "message": "Error description",
    "error_detail": { ... },
    "timestamp": 1234567890.123
}
```

Paginated responses:

```json
{
    "code": 0,
    "message": "Success",
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "page_size": 10,
        "total_pages": 10
    },
    "timestamp": 1234567890.123
}
```
