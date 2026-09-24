from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.project import Project
from app.models.project_update import ProjectUpdate
from app.models.project_member import ProjectMember
from app.models.project_update_image import ProjectUpdateImage

from pathlib import Path
from uuid import uuid4
import os

def create_project_update_image(
    db: Session,
    project_id: int,
    update_id: int,
    organization_id: int,
    images: list[UploadFile],
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.organization_id == organization_id,
        )
        .first()
    )
    
    if not project:
        return None, "project_not_found"
    
    project_update = (
        db.query(ProjectUpdate)
        .filter(
            ProjectUpdate.id == update_id,
            ProjectUpdate.project_id == project_id,
        )
        .first()
    )
    
    if not project_update:
        return None, "update_not_found"
    
    if not images:
        return None, "no_images"
    
    if len(images) > 10:
        return None, "too_many_images"
    
    
    allowed_image_types = [
        "image/jpeg",
        "image/png",
        "image/webp",
    ]
    
    
    allowed_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    ]
    
    print("Number of images", len(images))
    
    for image in images:
        if image.content_type not in allowed_image_types:
            return None, "invalid_image_type"
    
        extension = Path(image.filename or "").suffix.lower()

        
        if extension not in allowed_extensions:
            return None, "invalid_image_extension"
    
    upload_directory = "uploads/project_updates"
    os.makedirs(upload_directory, exist_ok=True)
    
    saved_file_paths = []
    project_update_images = []
    
    try:
        # save every image and prepare its database recors
        for image in images:
            extension = Path(image.filename or "").suffix.lower()
            filename = f"{uuid4()}{extension}"
            
            file_path = os.path.join(upload_directory, filename)
            
            with open(file_path, "wb") as buffer:
                buffer.write(image.file.read())
                
            saved_file_paths.append(file_path)
            
            image_url = f"/uploads/project_updates/{filename}"
        
            project_update_image = ProjectUpdateImage(
                project_update_id=update_id,
                image_url=image_url,
            )
            
            project_update_images.append(project_update_image)
    
        db.add_all(project_update_images)
        db.commit()
        
        for project_update_image in project_update_images:
            db.refresh(project_update_image)
    
    except Exception:
        db.rollback()
        
        for file_path in saved_file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
            
        return None, "image_save_failed"
        
    return project_update_images, None



def get_project_update_images(
    db: Session,
    project_id: int,
    update_id: int,
    organization_id: int,
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.organization_id == organization_id,
        )
        .first()
    )
    
    if not project:
        return None, "project_not_found"
    
    
    project_update = (
        db.query(ProjectUpdate)
        .filter(
            ProjectUpdate.project_id == project_id,
            ProjectUpdate.id == update_id,
        )
        .first()
    )
    
    if not project_update:
        return None, "update_not_found"
    
    images = (
        db.query(ProjectUpdateImage)
        .filter(
            ProjectUpdateImage.project_update_id == update_id,
        )
        .order_by(ProjectUpdateImage.created_at.asc())
        .all()
    )
    
    return images, None