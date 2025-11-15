from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.security import get_password_hash
from loguru import logger

def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Retrieves a user from the database by their email.
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Creates a new user in the database.
    - Hashes the password before storing.
    - Handles potential integrity errors (e.g., duplicate email).
    """
    logger.info(f"Attempting to create user: {user_in.email}")
    
    # Check if user already exists
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        logger.warning(f"User already exists: {user_in.email}")
        return None

    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit() # Commit the transaction
    db.refresh(db_user) # Refresh to get the ID from the DB
    
    logger.info(f"Successfully created user with ID: {db_user.id}")
    return db_user