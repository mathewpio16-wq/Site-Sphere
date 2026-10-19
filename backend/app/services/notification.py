from sqlalchemy.orm import Session
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

def create_notification(
    db: Session,
    notification_data: NotificationCreate,
):
    user = (
        db.query(User)
        .filter(
            User.id == notification_data.user_id,
        )
        .first()
    )
    
    if not user:
        return None, "user_not_found"
    
    notification = Notification(
        **notification_data.model_dump()
    )
    
    db.add(notification)
    db.commit()
    
    db.refresh(notification)
    
    return notification, None



def get_user_notifications(
    db: Session,
    user_id: int,
):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
        )
        .order_by(Notification.created_at.desc())
        .all()
    )
    
    return notifications