from app.models.user import User
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.project_member import ProjectMember
from app.models.project_update import ProjectUpdate



def has_role(
    user: User,
    allowed_roles: list[str],
) -> bool:
    return user.role.name in allowed_roles


def require_role(
    user: User,
    allowed_roles: list[str],
):
    if not has_role(user, allowed_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
        
        
        
def require_project_access(
    db: Session,
    user: User,
    project_id: int,
):
    if has_role(user, ["Admin", "Manager"]):
        return
    
    membership = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id,
        )
        .first()
    )
    
    if membership:
        return
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have access to this project",
    )
    
    
def require_update_ownership(
    user: User,
    project_update: ProjectUpdate
):
    if has_role(user, ["Admin", "Manager"]):
        return
    
    if project_update.user_id == user.id:
        return
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not allowed to modify this project update",
    )