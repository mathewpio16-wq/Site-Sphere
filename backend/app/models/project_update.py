from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Text, DateTime

from app.core.database import Base

class ProjectUpdate(Base):
    __tablename__="project_updates"
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    
    title: Mapped[str] = mapped_column(
        String(150),
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
    
    
    