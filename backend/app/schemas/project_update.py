from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class ProjectUpdateCreate(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=150
    )
    content: str = Field(
        min_length=2,
    )

class ProjectUpdateUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    content: str | None = Field(
        default=None,
        min_length=2,
    )
        
class ProjectUpdateResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    title: str
    content: str 
    created_at: datetime
    updated_at: datetime
    
    
    model_config = ConfigDict(
        from_attributes=True
    )