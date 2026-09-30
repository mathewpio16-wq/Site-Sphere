from sqlalchemy.orm import Session


from app.schemas.user import OrganizationUserCreate
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password

def create_organization_user(
    db: Session,
    organization_id: int,
    creator_role: str,
    user_data: OrganizationUserCreate
):
    existing_user = (
        db.query(User)
        .filter(
            User.email == user_data.email
        )
        .first()
    )
    
    if existing_user:
        return None, "email_exists"
    
    requested_role = (
        db.query(Role)
        .filter(
            Role.name == user_data.role
        )
        .first()
    )
    
    if not requested_role:
        return None, "role_not_found"
    
    
    # Managers can create staff and client
    # but they caqnnot create another manager
    if creator_role == "Manager" and user_data.role == "Manager":
        return None, "role_not_allowed"
    
    # Hash password before storing it
    hashed_password = hash_password(
        user_data.password
    )
    
    # Create the user inside the creators organization
    new_user = User(
        organization_id=organization_id,
        role_id=requested_role.id,
        first_name=user_data.first_name,
        last_name = user_data.last_name,
        email = user_data.email,
        hashed_password = hashed_password,
        phone = user_data.phone,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user, None


def get_organization_users(
    db: Session,
    organization_id: int,
):
    users = (
        db.query(User)
        .filter(
            User.organization_id == organization_id        
        )
        .all()
    )
    
    return users


def get_organization_user(
    db: Session,
    user_id: int,
    organization_id: int,
):
    user = (
        db.query(User)
        .filter(
            User.organization_id == organization_id,
            User.id == user_id,
        )
        .first()
    )
    
    if not user:
        return None, "user_not_found"
    
    return user, None