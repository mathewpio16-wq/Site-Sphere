from app.models.user import User
from fastapi import HTTPException, status


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