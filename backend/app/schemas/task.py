from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# Restricts status and priority to values wour application understands.
TaskStatus = Literal[
    "pending",
    "in_progress",
    "completed",
]

TaskPriority = Literal[
    "low",
    "medium",
    "high",
]

class TaskCreate(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=150,
    )
    
    description: str | None = None
    
    assigned_user_id: int | None = None
    
    status: TaskStatus = "pending"
    
    priority: TaskPriority = "medium"
    
    due_date: date | None = None
    
    
class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    
    description: str | None = None
    assigned_user_id: int | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None
    
    
class TaskResponse(BaseModel):
    id: int
    project_id: int
    assigned_user_id: int | None
    
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: date | None
    
    created_at: datetime
    updated_at: datetime
    
    
    model_config = ConfigDict(
        from_attributes=True
    )