from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

def create_project(
    db: Session,
    project_data: ProjectCreate,
    organization_id: int,
):
    project = Project(
        organization_id = organization_id,
        **project_data.model_dump()
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


def get_projects(
    db: Session,
    organization_id: int,
):
    projects = (
        db.query(Project)
        .filter(
            Project.organization_id == organization_id
        )
        .all()
    )
    
    return projects


def get_project_by_id(
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
    
    return project



def update_project(
    db: Session,
    project_id: int,
    organization_id: int,
    project_data: ProjectUpdate
):
    project = get_project_by_id(
        db=db,
        project_id=project_id,
        organization_id=organization_id,
    )
    
    if not project:
        return None
    
    update_data = project_data.model_dump(
        exclude_unset=True
    )
    
    for field, value in update_data.items():
        setattr(project, field, value)
        
    db.commit()
    db.refresh(project)
    
    return project



def delete_project(
    db: Session,
    project_id: int,
    organization_id: int,
):
    project = get_project_by_id(
        db=db,
        project_id=project_id,
        organization_id=organization_id,
    )
    
    if not project:
        return False
    
    db.delete(project)
    db.commit()
    
    return True