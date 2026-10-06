from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (1 to 100)")

class PaginationMeta(BaseModel):
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(default_factory=list, description="Paginated item records")
    meta: PaginationMeta = Field(..., description="Pagination metadata")

    model_config = ConfigDict(from_attributes=True)

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message description")
    code: Optional[str] = Field(None, description="Optional machine-readable error code")

class SuccessResponse(BaseModel):
    message: str = Field("Operation successful", description="Success message")
    data: Optional[Any] = Field(None, description="Optional payload returned by operation")
