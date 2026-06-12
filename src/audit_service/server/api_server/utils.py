from typing import Optional
from pydantic import BaseModel, Field

class ApiResponse(BaseModel):
    success: bool
    message: str = ""
    data: Optional[dict] = None