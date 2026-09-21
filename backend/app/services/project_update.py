from app.models.project import Project
from sqlalchemy.orm import Session
from app.schemas.project_update import (
    ProjectUpdateCreate,
    ProjectUpdateUpdate,
    ProjectUpdateResponse,
)
from app.models.project_member import ProjectMember
from app.models.project_update import ProjectUpdate

def create_project_update(
    db: Session,
    project_id: int,
    organization_id: int,
    user_id: int,
    update_data: ProjectUpdateCreate,
):
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
    
    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
    )
    
    if not member:
        return None, "user_not_project_member"
    
    project_update = ProjectUpdate(
        project_id=project_id,
        user_id=user_id,
        **update_data.model_dump(),
    )
    
    db.add(project_update)
    db.commit()
    db.refresh(project_update)
    
    return project_update, None



def get_project_updates(
    db: Session,
    project_id: int,
    organization_id: int,
):
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
    
    
    project_updates = (
        db.query(ProjectUpdate)
        .filter(
            ProjectUpdate.project_id == project_id
        )
        .order_by(ProjectUpdate.created_at.desc())
        .all()
    )
    
    return project_updates, None
    
    
    
def get_project_update(
    db: Session,
    project_id: int,
    update_id: int,
    organization_id: int,
):
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
    
    project_update = (
        db.query(ProjectUpdate)
        .filter(
            ProjectUpdate.id == update_id,
            ProjectUpdate.project_id == project_id
        )
        .first()
    )
    
    if not project_update:
        return None, "update_not_found"
    
    return project_update, None



def update_project_update(
    db: Session,
    organization_id: int,
    update_id: int,
    user_id: int,
    project_id: int,
    update_data: ProjectUpdateUpdate,
):
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
    
    project_update = (
        db.query(ProjectUpdate)
        .filter(
            ProjectUpdate.id == update_id,
            ProjectUpdate.project_id == project_id,
        )
        .first()
    )
    
    if not project_update:
        return None, "update_not_found"
    
    if project_update.user_id != user_id:
        return None, "not_update_owner"
    
    update = update_data.model_dump(
        exclude_unset=True
    )
    
    for field, value in update.items():
        setattr(project_update, field, value)
            
    db.commit()
    db.refresh(project_update)
    
    return project_update, None



def delete_project_update(
    db: Session,
    project_id: int,
    update_id: int,
    organization_id: int,
    user_id: int,
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.organization_id == organization_id,
        )
        .first()
    )
    
    if not project:
        return False, "project_not_found"
    
    
    project_update = (
        db.query(ProjectUpdate)
        .filter(
            ProjectUpdate.id == update_id,
            ProjectUpdate.project_id == project_id,
        )
        .first()
    )
    
    if not project_update:
        return False, "update_not_found"
    
    
    if project_update.user_id != user_id:
        return False, "not_update_owner"
    
    db.delete(project_update)
    db.commit()
    
    return True, None