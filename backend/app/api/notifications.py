from app.models.notification import Notification
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.notification import (
    NotificationCreate, 
    NotificationResponse,
    MarkAllNotificationsAsReadResponse
)
from app.models.user import User
from app.services.notification import (
        get_user_notifications,
        create_notification,
        mark_notification_as_read,
        mark_all_notifications_as_read,
)



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



@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
def mark_as_read_route(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mark_as_read, error = mark_notification_as_read(
        db=db,
        user_id=current_user.id,
        notification_id=notification_id,
    )

    if error == "notification_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return mark_as_read


@router.patch(
    "/read-all",
    response_model=MarkAllNotificationsAsReadResponse,
    status_code=status.HTTP_200_OK,
)
def mark_all_as_read_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mark_all_as_read = mark_all_notifications_as_read(
        db=db,
        user_id=current_user.id,
    )

    return {
        "message": "All notifications marked as read",
        "updated_count": mark_all_as_read,
    }