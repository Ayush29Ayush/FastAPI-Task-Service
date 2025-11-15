from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger

from app.db.session import get_db
from app.schemas.user import User, UserCreate
from app.services import user_service

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db)
):
    """
    Creates a new user.
    """
    db_user = user_service.get_user_by_email(db, email=user_in.email)
    if db_user:
        logger.warning(f"Attempt to create duplicate user: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
        
    user = user_service.create_user(db=db, user_in=user_in)
    return user