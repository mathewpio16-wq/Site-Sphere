from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class ProjectUpdateCommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    
    
class ProjectUpdateCommentResponse(BaseModel):
    id: int
    project_update_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    
    model_config=ConfigDict(from_attributes=True)