from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.schemas.pagination import PaginatedResponse
from app.services import task_service
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task.
    """
    return task_service.create_task(db=db, task_in=task_in, owner_id=current_user.id)

@router.get("/", response_model=PaginatedResponse[Task])
def read_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at", alias="sortBy"),
    sort_order: str = Query("desc", alias="sortOrder", regex="^(asc|desc)$"),
    filter_query: Optional[str] = Query(None, alias="filter")
):
    """
    Retrieve all tasks for the current user with pagination, sorting, and filtering.
    """
    total, tasks = task_service.get_all_tasks(
        db=db,
        owner_id=current_user.id,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
        filter_query=filter_query
    )
    return PaginatedResponse(total=total, limit=limit, offset=offset, data=tasks)

@router.get("/{task_id}", response_model=Task)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a single task by its ID.
    """
    db_task = task_service.get_task_by_id(db=db, task_id=task_id, owner_id=current_user.id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return db_task

@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing task.
    This endpoint can be used for partial updates (PATCH) as
    the Pydantic schema has optional fields.
    """
    db_task = task_service.update_task(
        db=db, task_id=task_id, task_in=task_in, owner_id=current_user.id
    )
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return db_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task.
    """
    success = task_service.delete_task(db=db, task_id=task_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return