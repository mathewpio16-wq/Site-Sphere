from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    
    # Every task must belong to a constructive project
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )
    
    # The task can initially be unassigned, so this is nullable.
    assigned_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )
    
    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )
    
    priority: Mapped[str] = mapped_column(
        String(50),
        default="medium",
        nullable=False,
    )
    
    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
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
    
    project = relationship(
        "Project",
        back_populates="tasks",
    )
    
    assigned_user = relationship(
        "User",
        back_populates="assigned_tasks"
    )