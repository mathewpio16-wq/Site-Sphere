from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class ProjectUpdateImage(Base):
    __tablename__="project_update_images"
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    
    project_update_id: Mapped[int] = mapped_column(
        ForeignKey("project_updates.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )