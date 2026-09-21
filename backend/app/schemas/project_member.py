from datetime import datetime

from pydantic import BaseModel, ConfigDict

class ProjectMemberCreate(BaseModel):
    user_id: int
    

class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    assigned_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True
    )
    
    

class ProjectMemberDetailResponse(BaseModel):
    member_id: int
    user_id: int
    first_name: str
    last_name: str
    email: str
    role: str
    assigned_at: datetime
    