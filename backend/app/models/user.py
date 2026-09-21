from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
    )
    
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False,
    )
    
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    
    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(225),
        nullable=False,
    )
    
    phone: Mapped[str | None] = mapped_column(
        String(225),
        nullable=True,
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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
    
    organization = relationship(
        "Organization",
        back_populates="users"
    )
    
    role = relationship(
        "Role",
        back_populates="users"
    )
    
    project_memberships = relationship(
        "ProjectMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    assigned_tasks = relationship(
        "Task",
        back_populates="assigned_user"
    )