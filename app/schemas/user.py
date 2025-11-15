from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    """
    Base schema for User, containing common fields.
    """
    email: EmailStr

class UserCreate(UserBase):
    """
    Schema for creating a new user.
    Requires a password.
    """
    password: str

class User(UserBase):
    """
    Schema for reading/returning a user.
    This model is used in API responses and does NOT include the password.
    """
    id: int

    class Config:
        from_attributes = True