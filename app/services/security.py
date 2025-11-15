from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from loguru import logger

from app.core.config import settings
from app.schemas.token import TokenData

# Use pbkdf2_sha256 which is pure-python and has no bcrypt dependency
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

ALGORITHM = settings.ALGORITHM

def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt_sha256 (preferred).
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a new JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decodes a JWT access token and returns the token data.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("JWT token is missing 'sub' (email) claim.")
            return None
        
        token_data = TokenData(email=email)
        return token_data
    except JWTError as e:
        logger.warning(f"JWT decoding error: {e}")
        return None
    except ValidationError as e:
        logger.warning(f"Pydantic validation error for token data: {e}")
        return None