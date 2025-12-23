from typing import Any, Optional
from pydantic import BaseModel

class TaskResult(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
