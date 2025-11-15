from pydantic import BaseModel
from typing import List, Generic, TypeVar, Optional

# Create a generic TypeVar
T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response schema.
    """
    total: int
    limit: int
    offset: int
    data: List[T]