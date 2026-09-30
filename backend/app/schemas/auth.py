from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class RegisterRequest(BaseModel):
    first_name: str = Field(
        min_length=2,
        max_length=100
    )

    last_name: str = Field(
        min_length=2,
        max_length=100
    )
    
    email: EmailStr
    
    password: str = Field(
        min_length=8,
        max_length=128
    )
    
    organization_name: str = Field(
        min_length=2,
        max_length=150,
    )
    
    phone: str | None = None
    

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"