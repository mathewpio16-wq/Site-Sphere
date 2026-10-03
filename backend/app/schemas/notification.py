from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Literal
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str 
    is_read: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)