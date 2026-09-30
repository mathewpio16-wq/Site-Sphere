from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role
from app.models.organization import Organization
from app.schemas.auth import RegisterRequest
from app.core.security import hash_password, verify_password
from app.core.security import verify_password
from app.schemas.user import OrganizationUserCreate


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
        return None, "email_exists"
    
    # Get the user role
    admin_role = (
        db.query(Role)
        .filter(
            Role.name == "Admin",
        )
        .first()
    )
    
    if not admin_role:
        return None, "admin_role_not_found"
    
    try:
        # Prepare new organization
        new_organization = Organization(
            name=user_data.organization_name,
        )
        
        db.add(new_organization)
        
        # send INSERT without commiting
        db.flush()
        
        # hash the password before storing it
        hashed_password = hash_password(user_data.password)
        
        # create new user
        new_user = User(
            organization_id=new_organization.id,
            role_id=admin_role.id,
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
    except Exception:
        db.rollback()
        return None, "registration_failed"    
        
    return new_user, None


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


