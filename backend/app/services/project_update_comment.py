from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_update import ProjectUpdate
from app.models.user import User
from app.models.project_update_comment import ProjectUpdateComment


def create_project_update_comment(
    db: Session,
    organization_id: int,
    project_id: int,
    user_id: int,
    update_id: int,
    content: str,
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
    
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.organization_id == organization_id,
        )
        .first()
    )
    
    if not user:
        return None, "user_not_found"
    
    project_update_comment = ProjectUpdateComment(
        project_update_id=update_id,
        user_id=user_id,
        content=content,
    )
    
    db.add(project_update_comment)
    db.commit()
    db.refresh(project_update_comment)
    
    return project_update_comment, None



def get_project_update_comments(
    db: Session,
    organization_id: int,
    project_id: int,
    update_id: int,
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
    
    comments = (
        db.query(ProjectUpdateComment)
        .filter(
            ProjectUpdateComment.project_update_id == update_id
        )
        .all()
    )
    
    return comments, None



def update_project_update_comment(
    db: Session,
    organization_id: int,
    project_id: int,
    user_id: int,
    comment_id: int,
    update_id: int,
    content: str,
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
    
    update = (
        db.query(ProjectUpdate)
        .filter(
            ProjectUpdate.id == update_id,
            ProjectUpdate.project_id == project_id,
        )
        .first()
    )
    
    if not update:
        return None, "update_not_found"
    
    comment = (
        db.query(ProjectUpdateComment)
        .filter(
            ProjectUpdateComment.id == comment_id,
            ProjectUpdateComment.project_update_id == update_id,
        )
        .first()
    )
    
    if not comment:
        return None, "comment_not_found"
    
    user_comment = (
        comment.user_id == user_id
    )
    
    if not user_comment:
        return None, "not_comment_owner"
    
    comment.content = content
    
    db.commit()
    db.refresh(comment)
    
    return comment, None
    
    
    
    
def delete_project_update_comment(
    db: Session,
    project_id: int,
    update_id: int,
    organization_id: int,
    comment_id: int,
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
        return None, "project_not_found"
    
    update = (
        db.query(ProjectUpdate)
        .filter(
            ProjectUpdate.id == update_id,
            ProjectUpdate.project_id == project_id,
        )
        .first()
    )
    
    if not update:
        return None, "update_not_found"
    
    comment = (
        db.query(ProjectUpdateComment)
        .filter(
            ProjectUpdateComment.id == comment_id,
            ProjectUpdateComment.project_update_id == update_id,
        )
        .first()
    )
    
    if not comment:
        return None, "comment_not_found"
    
    if comment.user_id != user_id:
        return None, "not_comment_owner"
    
    db.delete(comment)
    db.commit()
    
    return True, None