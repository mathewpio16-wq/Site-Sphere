from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
)
from typing import Annotated
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.project import (
    ProjectCreate, 
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project import (
    create_project,
    get_projects,
    get_project_by_id,
    update_project,
    delete_project,
)

from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectMemberDetailResponse,
)

from app.services.project_member import (
    add_project_member,
    get_project_members,
    remove_project_member,
)

from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)

from app.services.task import (
    create_task,
    get_project_tasks,
    get_task,
    update_task,
    delete_task,
)
from app.schemas.project_update import (
    ProjectUpdateCreate,
    ProjectUpdateResponse,
    ProjectUpdateUpdate,
)
from app.services.project_update import (
    create_project_update,
    get_project_updates,
    get_project_update,
)
from app.services.project_update import (
    update_project_update,
    delete_project_update,
)

from app.services.project_update_image import (
    create_project_update_image,
    get_project_update_images,
)
from app.schemas.product_update_image import ProjectUpdateImageResponse
from app.schemas.project_update_comment import (
    ProjectUpdateCommentResponse,
    ProjectUpdateCommentCreate,
)
from app.services.project_update_comment import (
    create_project_update_comment,
    get_project_update_comments,
    update_project_update_comment,
    delete_project_update_comment,
    get_project_update_comment,
)

from app.core.permissions import (
    has_role, 
    require_role, 
    require_project_access, 
    require_update_ownership,
    require_comment_ownership,
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

@router.get("/test-permissions")
def test_permissions(
    current_user: User = Depends(get_current_user),
):
    require_role(
        current_user,
        ["Admin", "Manager"],
    )

    return {
        "message": "You have permission to access this route",
        "role": current_user.role.name,
    }   
    
    

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    require_role(
        current_user,
        ["Admin", "Manager"],
    )
    
    project = create_project(
        db=db,
        project_data=project_data,
        organization_id=current_user.organization_id,
    )
    
    return project



@router.get(
    "",
    response_model=list[ProjectResponse],
)
def get_all_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = get_projects(
        db=db,
        organization_id=current_user.organization_id,
        user=current_user,
    )
    
    return projects


@router.get(
    "/{project_id}",
    response_model=ProjectResponse
)
def get_single_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_project_by_id(
        db=db,
        project_id=project_id,
        organization_id=current_user.organization_id
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )
    
    return project


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_existing_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = update_project(
        db=db,
        project_id=project_id,
        organization_id=current_user.organization_id,
        project_data=project_data,
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_project(
        db=db,
        project_id=project_id,
        organization_id=current_user.organization_id,   
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    return None



@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member_to_project(
    member_data: ProjectMemberCreate,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # The service performs the important security checks:
    # - project belongs to current organisation
    # - user belongs to current organisation
    # - user isn't already assigned to the project
    
    require_role(
        current_user,
        ["Admin", "Manager"],
    )
    
    project_member, error = add_project_member(
        db=db,
        project_id=project_id,
        user_id=member_data.user_id,
        organization_id=current_user.organization_id,
    )
    
    # convert service errors into apprioprate HTTP responses.
    if error == "project_not_found":
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if error == "user_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in you organization"
        )
        
    if error == "already_member":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this project",
        )
        
    return project_member


@router.get(
    "/{project_id}/members",
    response_model=list[ProjectMemberDetailResponse],
)
def get_members_of_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only retrieve members if the project belongs
    # to the authenticated user's organisation.
    members = get_project_members(
        project_id = project_id,
        db=db,
        organization_id=current_user.organization_id,
    )
    
    if members is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )
    
    return members



@router.delete(
    "/{project_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_member_from_project(
    project_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(
        current_user,
        ["Admin", "Manager"],
    )
    
    deleted, error = remove_project_member(
        db=db,
        project_id=project_id,
        member_id=member_id,
        organization_id=current_user.organization_id
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "member_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )
        
    return None



@router.post(
    "/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_task(
    project_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # project_id comes from the URL.
    # organization_id comes from the authenticated user.
    # task_data contains the information submitted in the request body.
    
    require_role(
        current_user,
        ["Admin", "Manager"],
    )
    
    task, error = create_task(
        db=db,
        project_id=project_id,
        organization_id=current_user.organization_id,
        task_data=task_data
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
        
    if error == "user_not_project_member":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned user is not a member of this project",
        )
        
    return task


@router.get(
    "/projects/{project_id}/tasks",
    response_model=list[TaskResponse],
)
def list_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = get_project_tasks(
        db=db,
        project_id=project_id,
        organization_id=current_user.organization_id
    )
    
    if tasks is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
        
    require_role(
        current_user,
        ["Admin", "Manager", "Staff"],
    )
    
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )
        
    return tasks


@router.get(
    "/projects/{project_id}/tasks/{task_id}",
    response_model=TaskResponse,
)
def get_project_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(
        db=db,
        project_id=project_id,
        task_id=task_id,
        organization_id=current_user.organization_id,
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
        
    require_role(
        current_user,
        ["Admin", "Manager", "Staff"],
    )    
    
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )
    
    return task



@router.patch(
    "/projects/{project_id}/tasks/{task_id}",
    response_model=TaskResponse,
)
def update_project_task(
    task_data: TaskUpdate,
    task_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(
        current_user,
        ["Admin", "Manager"]
    )
    
    task, error = update_task(
        db=db,
        project_id=project_id,
        task_id=task_id,
        organization_id=current_user.organization_id,
        task_data=task_data,
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
        
    if error == "task_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
        
    if error == "user_not_project_member":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a member of this project"
        )
    
    return task



@router.delete(
    "/projects/{project_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_role(
        current_user,
        ["Admin", "Manager"]
    )
    
    _, error = delete_task(
        db=db,
        project_id=project_id,
        task_id=task_id,
        organization_id=current_user.organization_id,
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
        
    if error == "task_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return None



@router.post(
    "/projects/{project_id}/updates",
    response_model=ProjectUpdateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_the_project_update(
    project_id: int,
    create_data: ProjectUpdateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(
        current_user,
        ["Admin", "Manager", "Staff"],
    )
    
    project = get_project_by_id(
        db=db,
        project_id=project_id,
        organization_id=current_user.organization_id,
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )
    
    project_update, error = create_project_update(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        user_id=current_user.id,
        update_data=create_data,
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    return project_update



@router.get(
    "/projects/{project_id}/updates",
    response_model=list[ProjectUpdateResponse]
)
def list_project_updates(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project_updates, error = get_project_updates(
        db=db,
        project_id=project_id,
        organization_id=current_user.organization_id,
    )

    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
        
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )
        
    return project_updates



@router.get(
    "/projects/{project_id}/updates/{update_id}",
    response_model=ProjectUpdateResponse
)
def the_project_update(
    project_id: int,
    update_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_update, error = get_project_update(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        update_id=update_id,
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project update not found"
        )
    
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )
    
    return project_update



@router.patch(
    "/projects/{project_id}/updates/{update_id}",
    response_model=ProjectUpdateResponse,
)
def edit_update_project(
    project_id: int,
    update_id: int,
    update_data: ProjectUpdateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(
        current_user,
        ["Admin", "Manager", "Staff"]
    )
    
    existing_update, error = get_project_update(
        db=db,
        organization_id=current_user.organization_id,
        update_id=update_id,
        project_id=project_id,
    )
        
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
        
    # Staff must belong to the project.
    # Admin/Manager automatically pass.
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )

    # Admin/Manager automatically pass.
    # Staff must be the creator of the update.
    require_update_ownership(
        user=current_user,
        project_update=existing_update,
    )
    
    
    # It is now safe to modify the database.
    update, error = update_project_update(
        db=db,
        organization_id=current_user.organization_id,
        update_id=update_id,
        project_id=project_id,
        update_data=update_data,
    )

    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
        
    return update
        
        
        
@router.delete(
    "/projects/{project_id}/updates/{update_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_project_update(
    project_id:int,
    update_id:int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(
        current_user,
        ["Admin", "Manager", "Staff"],
    )
    
    existing_update, error = get_project_update(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        update_id=update_id,
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found"
        )
        
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )
    
    require_update_ownership(
        user=current_user,
        project_update=existing_update,
    )
    
    _, error = delete_project_update(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        update_id=update_id,
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
        
    return None



@router.post(
    "/projects/{project_id}/updates/{update_id}/images",
    status_code=status.HTTP_201_CREATED,
    response_model=list[ProjectUpdateImageResponse],
)
def upload_image_file(
    project_id: int,
    update_id: int,
    images: Annotated[list[UploadFile], File()],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(
        current_user,
        ["Admin", "Manager", "Staff"],
    )
    
    existing_update, error = get_project_update(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        update_id=update_id,
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
    
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )
    
    image_upload, error = create_project_update_image(
        db=db,
        organization_id=current_user.organization_id,
        update_id=update_id,
        project_id=project_id, 
        images=images,  
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
    
    if error == "invalid_image_extension":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image extension",
        )
        
    if error == "invalid_image_type":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image type",
        )
        
    if error == "image_save_failed":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image save failed",
        )
        
    if error == "no_images":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No images"
        )
        
    if error == "too_many_images":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A Maximum of 10 images can be uploaded at once"
        )
        
    return image_upload


@router.get(
    "/projects/{project_id}/updates/{update_id}/images",
    status_code=status.HTTP_200_OK,
    response_model=list[ProjectUpdateImageResponse],
)
def get_project_update_images_route(
    project_id: int,
    update_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    images, error = get_project_update_images(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        update_id=update_id
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found"
        )
        
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )
        
    return images



@router.post(
    "/projects/{project_id}/updates/{update_id}/comments",
    status_code=status.HTTP_201_CREATED,
    response_model=ProjectUpdateCommentResponse,
)
def create_comment(
    project_id: int,
    update_id: int,
    comment_data: ProjectUpdateCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, error = get_project_update(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        update_id=update_id,
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
    
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )
    
    project_update_comment, error = create_project_update_comment(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        user_id=current_user.id,
        content=comment_data.content,
        update_id=update_id
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
        
    if error == "user_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
        
    return project_update_comment


@router.get(
    "/projects/{project_id}/updates/{update_id}/comments",
    status_code=status.HTTP_200_OK,
    response_model=list[ProjectUpdateCommentResponse],
)
def get_comments(
    project_id: int,
    update_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _, error = get_project_update(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        update_id=update_id,
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
    
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )

    comments, error = get_project_update_comments(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        update_id=update_id,
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found"
        )

    return comments



@router.patch(
    "/projects/{project_id}/updates/{update_id}/comments/{comment_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProjectUpdateCommentResponse,
)
def update_comment(
    project_id: int,
    update_id: int,
    comment_id: int,
    comment_data: ProjectUpdateCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, error = get_project_update(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        update_id=update_id,
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
    
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )  
    
    existing_comment, error = get_project_update_comment(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        update_id=update_id,
        comment_id=comment_id
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
    
    if error == "comment_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
        
    require_comment_ownership(
        user=current_user,
        project_update_comment=existing_comment,
    )
    
    comment, error = update_project_update_comment(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        update_id=update_id,
        comment_id=comment_id,
        content=comment_data.content,
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
        
    if error == "comment_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
        
        
    return comment



@router.delete(
    "/projects/{project_id}/updates/{update_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    project_id: int,
    update_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, error = get_project_update(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        update_id=update_id,
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
    
    require_project_access(
        db=db,
        user=current_user,
        project_id=project_id,
    )  
    
    existing_comment, error = get_project_update_comment(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        update_id=update_id,
        comment_id=comment_id
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
    
    if error == "comment_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
        
    require_comment_ownership(
        user=current_user,
        project_update_comment=existing_comment,
    )
    
    _, error = delete_project_update_comment(
        db=db,
        organization_id=current_user.organization_id,
        update_id=update_id,
        comment_id=comment_id,
        project_id=project_id
    )
    
    if error == "project_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
        
    if error == "update_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found"
        )
        
    if error == "comment_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
        
    return None