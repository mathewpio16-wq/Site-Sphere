from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import OrganizationUserCreate
from app.dependencies.auth import get_current_user
from app.core.permissions import require_role
from app.schemas.user import (
    OrganizationUserResponse,
    OrganizationUserUpdate,
)
from app.services.users import (
    create_organization_user,
    get_organization_users,
    get_organization_user,
    update_organization_user,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: OrganizationUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(
        current_user,
        ["Admin", "Manager"],
    )
    
    user, error = create_organization_user(
        db=db,
        organization_id=current_user.organization_id,
        creator_role=current_user.role.name,
        user_data=user_data,
    )
    
    
    if error == "email_exists":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )
        
    if error == "role_not_allowed":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to create this role"
        )
        
    if error == "role_not_found":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Requested role is not configured"
        )
    
    
    return {
        "message": "User created successfully",
        "user_id": user.id,
    }
    


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[OrganizationUserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(
        current_user,
        ["Admin", "Manager"],
    )
    
    users = get_organization_users(
        db=db,
        organization_id=current_user.organization_id,
    )
    
    return users

    
@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationUserResponse
)
def get_single_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    
):
    require_role(
        current_user,
        ["Admin", "Manager"],
    )
    
    user, error = get_organization_user(
        db=db,
        user_id=user_id,
        organization_id=current_user.organization_id,
    )
    
    if error == "user_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    return user


@router.patch(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationUserResponse,
)
def update_user(
    user_id: int,
    update_data: OrganizationUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(
        current_user,
        ["Admin", "Manager"],
    )
    
    updated_user, error = update_organization_user(
        db=db,
        user_id=user_id,
        organization_id=current_user.organization_id,
        creator_id=current_user.id,
        creator_role=current_user.role.name,
        update_data=update_data
    )
    
    if error == "user_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    if error == "cannot_modify_user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the permission to modify this user"
        )
        
    if error == "role_not_allowed":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role not allowed"
        )
        
    if error == "role_not_found":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Role not found"
        )
        
    if error == "cannot_deactivate_self":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot deactivate your own account",
        )
        
    if error == "cannot_change_own_role":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot change your own role",
        )
        
    return updated_user