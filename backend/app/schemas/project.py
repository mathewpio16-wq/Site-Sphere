from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    location: str | None = None
    start_date: str | None = None
    expected_end_date: date | None = None
    

class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    location: str | None = None
    status: str | None = None
    start_date: str | None = None
    expected_end_date: str | None = None
    
    
class ProjectResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    description: str | None
    location: str | None
    status: str
    start_date: date | None
    expected_end_date: date | None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)