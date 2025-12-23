from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class AgentMemory(BaseModel):
    agent_id: str
    interactions: List[dict] = []
    learnings: List[str] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
