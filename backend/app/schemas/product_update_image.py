from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class ProjectUpdateImageResponse(BaseModel):
    id: int
    project_update_id: int
    image_url: str
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True
    )