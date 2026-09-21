from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectMember(Base):
    __tablename__="project_members"
    
    
    # prevents the same user being assigned to the same project more than once
    __table_args__ = (
        UniqueConstraint(
          "project_id",
          "user_id",
          name="uq_project_member",  
        ),
    )
    
    
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
    
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    
    project = relationship(
        "Project",
        back_populates="members",
    )
    
    user = relationship(
        "User",
        back_populates="project_memberships",
    )
    
    