from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.core.security import hash_password, verify_password
from app.core.security import verify_password


def register_user(
    db: Session,
    user_data: RegisterRequest,
):
    #check whether the email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )
    
    if existing_user:
        return None
    
    # hash the password before storing it
    hashed_password = hash_password(user_data.password)
    
    # create new user
    new_user = User(
        organization_id=user_data.organization_id,
        role_id=user_data.role_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        hashed_password=hashed_password,
        phone=user_data.phone,
    )
    
    # save the user
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def authenticate_user(
    db: Session,
    email: str,
    password: str
):
    # find the user using their email
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )
    
    # User does not exist
    if not user:
        return None
    
    # check the entered password matches the stored hash password 
    if not verify_password(
        password,
        user.hashed_password
    ):
        return None
    
    # Prevent inactive users from logging in
    if not user.is_active:
        return None
    
    return user