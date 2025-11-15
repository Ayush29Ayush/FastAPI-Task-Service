from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .user import User

class TaskBase(BaseModel):
    """
    Base schema for Task.
    """
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    Inherits title and description from TaskBase.
    """
    pass

class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.
    All fields are optional for PATCH behavior.
    """
    title: Optional[str] = None
    description: Optional[str] = None

class Task(TaskBase):
    """
    Schema for reading/returning a task.
    This model is used in API responses.
    """
    id: int
    created_at: datetime
    owner_id: int
    owner: User

    class Config:
        from_attributes = True