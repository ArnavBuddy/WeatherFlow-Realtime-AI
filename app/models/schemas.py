from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class SessionCreate(BaseModel):
    user_id: Optional[str] = None

class Message(BaseModel):
    role: str # 'user', 'ai', 'system'
    content: str

class EventLog(BaseModel):
    session_id: str
    event_type: str
    content: str
    timestamp: datetime = datetime.now()
