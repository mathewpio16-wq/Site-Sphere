from app.models.notification import Notification
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.services.notification import create_notification
from app.models.user import User
from app.services.notification import get_user_notifications


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)



@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_notification_route(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if os.getenv("APP_ENV") != "development":
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )
        
    if notification_data.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only create test notifications for yourself"
        )
    
    notification, error = create_notification(
        db=db,
        notification_data=notification_data
    )
    
    if error == "user_not_found":
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
        
    return notification


@router.get(
    "/",
    response_model=list[NotificationResponse],
    status_code=status.HTTP_200_OK,
)
def get_user_notifications_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notifications = get_user_notifications(
        db=db,
        user_id=current_user.id
    )
    
    return notifications