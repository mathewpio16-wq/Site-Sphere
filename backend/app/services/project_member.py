from sqlalchemy.orm import Session

from app.models.project_member import ProjectMember
from app.models.project import Project
from app.models.user import User

def add_project_member(
    db: Session,
    project_id: int,
    user_id: int,
    organization_id: int,
):
    # Make sure the project belongs to the
    # authenticated user's organisation.
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.organization_id == organization_id,
        )
        .first()
    )
    
    if not project:
        return None, "project_not_found"
    
    
    # Make sure the user being added actually exists
    # and belongs to the same organisation.
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.organization_id == organization_id
        )
        .first()
    )
    
    if not user:
        return None, "user_not_found"
    
    # Prevent the same user from being added
    # to the same project more than once.
    
    existing_user = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
    )
    
    if existing_user:
        return None, "already_member"
    
    project_member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
    )
    
    db.add(project_member)
    db.commit()
    db.refresh(project_member)

    return project_member, None


def get_project_members(
    db: Session,
    project_id: int,
    organization_id: int,
):
    # check that the requested project belongs to the organizaton of the logged-in user
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.organization_id == organization_id
        )
        .first()
    )
    
    if not project:
        return None
    
    # Retrieve all membership records for this project.
    members = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id
        )
        .all()
    )
    
    result = []
    
    for member in members:
        
        user = member.user
        
        role_name = user.role.name
        
        result.append({
                "member_id": member.id,
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": role_name,
                "assigned_at": member.assigned_at,
            })
        
    return result    


def remove_project_member(
    db: Session,
    project_id: int,
    member_id: int,
    organization_id: int,
):
    # First make sure the project exists and belongs to the logged-in user's organization
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.organization_id == organization_id
        )
        .first()
    )
    
    if not project:
        return False, "project_not_found"
    
    
    # Find the membership using BOTH member_id and project_id.
    # This prevents a membership from another project being
    # removed by manipulating the URL.
    
    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.id == member_id
        )
        .first()
    )
    
    if not member:
        return False, "member_not_found"
    
    db.delete(member)
    db.commit()
    
    return True, None