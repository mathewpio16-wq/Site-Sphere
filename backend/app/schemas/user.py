from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Literal
from datetime import datetime

class OrganizationUserCreate(BaseModel):
    first_name: str = Field(
        min_length=2,
        max_length=100,
    )    
    
    last_name: str = Field(
        min_length=2,
        max_length=100,
    )
    
    email: EmailStr
    
    password: str = Field(
        min_length=8,
        max_length=128,
    )
    
    phone: str | None = None
    
    role: Literal[
        "Manager",
        "Staff",
        "Client",
    ]
    
    
class OrganizationUserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None
    is_active: bool
    role_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    
class OrganizationUserUpdate(BaseModel):
    first_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    
    last_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    
    phone: str | None = None
    
    role: Literal[
        "Manager",
        "Staff",
        "Client",
    ] | None = None
    
    is_active: bool | None = None