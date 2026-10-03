from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    
    user = relationship(
        "User",
        back_populates="notifications",
    )