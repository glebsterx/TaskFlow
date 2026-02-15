"""Telegram authentication for Web UI."""
import hashlib
import hmac
from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, Header
from jose import JWTError, jwt
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

SECRET_KEY = settings.SECRET_KEY if hasattr(settings, 'SECRET_KEY') else settings.TELEGRAM_BOT_TOKEN
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def verify_telegram_auth(auth_data: dict) -> bool:
    """
    Verify Telegram authentication data.
    
    Args:
        auth_data: Dict with id, first_name, username, photo_url, auth_date, hash
    
    Returns:
        True if authentication is valid
    """
    if not auth_data or 'hash' not in auth_data:
        return False
    
    check_hash = auth_data.pop('hash')
    
    # Create data check string
    data_check_arr = [f"{k}={v}" for k, v in sorted(auth_data.items())]
    data_check_string = '\n'.join(data_check_arr)
    
    # Calculate hash
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Check if hash matches
    if calculated_hash != check_hash:
        return False
    
    # Check if auth_date is not too old (1 day)
    auth_date = int(auth_data.get('auth_date', 0))
    current_timestamp = datetime.utcnow().timestamp()
    
    if current_timestamp - auth_date > 86400:  # 24 hours
        return False
    
    return True


def create_access_token(telegram_user: dict) -> str:
    """Create JWT access token for authenticated user."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(telegram_user['id']),
        "username": telegram_user.get('username', ''),
        "first_name": telegram_user.get('first_name', ''),
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    """Verify JWT token from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "id": int(user_id),
            "username": payload.get("username"),
            "first_name": payload.get("first_name")
        }
    except (ValueError, JWTError) as e:
        logger.warning("token_verification_failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid token")


# Dependency for protected routes
async def get_current_user(user: dict = Depends(verify_token)) -> dict:
    """Get current authenticated user."""
    return user
