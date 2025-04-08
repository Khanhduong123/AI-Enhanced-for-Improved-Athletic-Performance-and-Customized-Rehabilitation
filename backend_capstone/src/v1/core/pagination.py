from typing import Optional
from pydantic import BaseModel, Field

class PaginationParams(BaseModel):
    """
    Pagination parameters for API endpoints
    
    Attributes:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
    """
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of records to return")

def get_pagination_params(
    skip: Optional[int] = 0,
    limit: Optional[int] = 10
) -> PaginationParams:
    """
    Dependency function to get pagination parameters
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        PaginationParams object with validated values
    """
    return PaginationParams(skip=skip, limit=limit) 