from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth import register_user, authenticate_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register")
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    user = register_user(
        db=db,
        user_data=user_data
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    
    return {
        "message": "User registered successfully",
        "user_id": user.id
    }
    

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(
        db=db,
        email=form_data.username,
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )
        
    access_token = create_access_token(
        {
            "sub": str(user.id)
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    