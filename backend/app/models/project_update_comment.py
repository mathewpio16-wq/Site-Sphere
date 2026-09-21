from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Text, DateTime

from app.core.database import Base


class ProjectUpdateComment(Base):
    __tablename__ = "project_update_comments"
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    
    project_update_id: Mapped[int] = mapped_column(
        ForeignKey("project_updates.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )