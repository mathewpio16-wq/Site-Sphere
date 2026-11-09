from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_update import ProjectUpdate
from app.models.user import User
from app.models.project_update_comment import ProjectUpdateComment
from app.models.notification import Notification
from sqlalchemy.exc import SQLAlchemyError

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

    try:
    
        project_update_comment = ProjectUpdateComment(
            project_update_id=update_id,
            user_id=user_id,
            content=content,
        )
        
        db.add(project_update_comment)

        if project_update.user_id != user_id:
            recipient = (
                db.query(User)
                .filter(
                    User.id == project_update.user_id,
                    User.organization_id == organization_id,
                    User.is_active.is_(True),
                )
                .first()
            )

            if recipient:
                notification = Notification(
                    user_id=recipient.id,
                    message=f"{user.first_name} commented on your project update: {project_update_comment.content}",
                    is_read=False
                )

                db.add(notification)

        db.commit()
        db.refresh(project_update_comment)

    except SQLAlchemyError:
        db.rollback()
        raise
    
    return project_update_comment, None


# Get a single comment
def get_project_update_comment(
    db: Session,
    organization_id: int,
    project_id: int,
    update_id: int,
    comment_id: int,
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
    
    comment = (
        db.query(ProjectUpdateComment)
        .filter(
            ProjectUpdateComment.project_update_id == update_id,
            ProjectUpdateComment.id == comment_id,
        )
        .first()
    )
    
    if not comment:
        return None, "comment_not_found"
    
    return comment, None



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
    
    db.delete(comment)
    db.commit()
    
    return True, None