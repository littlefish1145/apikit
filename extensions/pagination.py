from typing import Any, List, Optional
from core.response import Response, SuccessResponse


class PageResult:
    def __init__(
        self,
        items: List[Any],
        total: int,
        page: int,
        page_size: int
    ):
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
        self.total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

    def to_response(self, message: str = "Success") -> Response:
        return SuccessResponse(
            data={
                "items": self.items,
                "total": self.total,
                "page": self.page,
                "page_size": self.page_size,
                "total_pages": self.total_pages,
            },
            message=message
        )


def paginate(items: List[Any], total: int, page: int, page_size: int) -> PageResult:
    return PageResult(items=items, total=total, page=page, page_size=page_size)


def create_page_result(
    items: List[Any],
    total: int,
    page: int,
    page_size: int
) -> PageResult:
    return PageResult(items=items, total=total, page=page, page_size=page_size)
