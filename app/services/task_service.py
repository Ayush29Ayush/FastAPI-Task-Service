from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, text, column
from typing import List, Optional
from loguru import logger

from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate

def create_task(db: Session, task_in: TaskCreate, owner_id: int) -> Task:
    """
    Creates a new task within a database transaction.
    This demonstrates the transaction handling requirement. 
    """
    logger.info(f"Creating task '{task_in.title}' for user {owner_id}")
    db_task = Task(**task_in.model_dump(), owner_id=owner_id)
    
    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        logger.info(f"Task created with ID: {db_task.id}")
        return db_task
    except Exception as e:
        logger.error(f"Transaction failed for task creation: {e}")
        db.rollback()
        raise

def get_task_by_id(db: Session, task_id: int, owner_id: int) -> Task | None:
    """
    Retrieves a single task by its ID, ensuring it belongs to the owner.
    """
    return (
        db.query(Task)
        .filter(Task.id == task_id, Task.owner_id == owner_id)
        .first()
    )

def get_all_tasks(
    db: Session,
    owner_id: int,
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    filter_query: Optional[str] = None
) -> (int, List[Task]):
    """
    Retrieves a paginated list of tasks for a user.
    - Implements pagination and sorting. [cite: 49]
    - Implements a custom SQL filter query. 
    """
    
    # Base query
    query = (
        db.query(Task)
        .filter(Task.owner_id == owner_id)
        .options(joinedload(Task.owner))
    )

    if filter_query:
        search_term = f"%{filter_query}%"
        query = query.filter(
            Task.title.ilike(search_term) | Task.description.ilike(search_term)
        )

    total_count = query.count()

    # Apply sorting
    if hasattr(Task, sort_by):
        sort_column = getattr(Task, sort_by)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

    # Apply pagination
    tasks = query.limit(limit).offset(offset).all()

    return total_count, tasks

def update_task(
    db: Session, task_id: int, task_in: TaskUpdate, owner_id: int
) -> Task | None:
    """
    Updates an existing task.
    - Uses model_dump(exclude_unset=True) for partial updates (PATCH).
    """
    db_task = get_task_by_id(db, task_id=task_id, owner_id=owner_id)
    if not db_task:
        return None

    update_data = task_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_task, key, value)

    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        logger.info(f"Task updated: {task_id}")
        return db_task
    except Exception as e:
        logger.error(f"Transaction failed for task update: {e}")
        db.rollback()
        raise

def delete_task(db: Session, task_id: int, owner_id: int) -> bool:
    """
    Deletes a task by its ID.
    Returns True if successful, False if not found.
    """
    db_task = get_task_by_id(db, task_id=task_id, owner_id=owner_id)
    if not db_task:
        logger.warning(f"Task not found for deletion: {task_id}")
        return False

    try:
        db.delete(db_task)
        db.commit()
        logger.info(f"Task deleted: {task_id}")
        return True
    except Exception as e:
        logger.error(f"Transaction failed for task deletion: {e}")
        db.rollback()
        raise