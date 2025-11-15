from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from loguru import logger

from app.db.session import get_db
from app.services import user_service, security
from app.models.user import User
from app.schemas.token import TokenData

# This tells FastAPI where to look for the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_rate_limit_key(request: Request) -> str:
    """
    Determines the identifier for rate limiting.
    Using IP address. A more robust solution might use
    an API key or authenticated user ID.
    """
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0]
    
    return request.client.host

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get the current authenticated user.
    - Decodes the JWT token.
    - Fetches the user from the database.
    - Raises 401 exception if invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = security.decode_access_token(token)
    if token_data is None:
        logger.warning("Token decoding failed or token is invalid.")
        raise credentials_exception
    
    user = user_service.get_user_by_email(db, email=token_data.email)
    if user is None:
        logger.warning(f"User not found for email in token: {token_data.email}")
        raise credentials_exception
        
    return user