import pydantic
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.models.project_member import ProjectMember

def create_task(
    db: Session,
    project_id: int,
    organization_id: int,
    task_data: TaskCreate,
):
    # Make sure project exists and belongs to logged in user's organization
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.organization_id == organization_id
        )
        .first()
    )
    
    if not project:
        return None, "project_not_found"
    
    # Only perform the membership check if somebody
    # has actually been assigned to the task.
    
    if task_data.assigned_user_id is not None:
        
        # A valid assignment requires a ProjectMember
        # record connecting this user to this project.
        project_member = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == task_data.assigned_user_id,
            )
            .first()
        )
        
        if not project_member:
            return None, "user_not_project_member"
    
    # Convert the validated Pydantic data into values
    # that can be passed to our SQLAlchemy Task model.
    task = Task(
        project_id=project_id,
        **task_data.model_dump()
    )
    
    db.add(task)
    db.commit()
    
    db.refresh(task)
    
    return task, None



def get_project_tasks(
    db: Session,
    project_id: int,
    organization_id: int,
):
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
    
    tasks = (
        db.query(Task)
        .filter(
            Task.project_id == project_id
        )
        .all()
    )
    
    return tasks



def get_task(
    db: Session,
    project_id: int,
    task_id: int,
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
        return None
    
    # find he specific task in the project
    
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.project_id == project_id,
        )
        .first()
    )
    
    return task


def update_task(
    db: Session,
    project_id: int,
    organization_id: int,
    task_id: int,
    task_data: TaskUpdate,
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
    
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.project_id == project_id,
        )
        .first()
    )
    
    if not task:
        return None, "task_not_found"
    
    
    if task_data.assigned_user_id is not None:
        member = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == task_data.assigned_user_id,
            )
            .first()
        )
    
        if not member:
            return None, "user_not_project_member"
    
    updated_task = task_data.model_dump(
        exclude_unset=True,
    )
    
    for field, value in updated_task.items():
        setattr(task, field, value)
        
    db.commit()
    db.refresh(task)
    
    return task, None



def delete_task(
    db: Session,
    task_id: int,
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
        return False, "project_not_found"
    
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.project_id == project_id,
        )
        .first()
    )
    
    if not task:
        return False, "task_not_found"
    
    db.delete(task)
    db.commit()
    
    return True, None