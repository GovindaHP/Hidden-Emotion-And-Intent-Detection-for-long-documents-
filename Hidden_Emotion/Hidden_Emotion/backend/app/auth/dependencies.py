from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.auth.jwt_handler import decode_access_token
from app.database.mongo import db_manager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        # Return default guest user if no auth token provided, allowing easy demo mode
        return {
            "_id": "guest_user_id",
            "username": "guest",
            "email": "guest@analyzer.ai",
            "role": "user"
        }
        
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload invalid"
        )
        
    user = await db_manager.find_one("users", {"email": email})
    if user is None:
        # Provide fallback user profile for decoded token
        return {
            "_id": payload.get("user_id", "guest_user_id"),
            "username": payload.get("username", email.split("@")[0]),
            "email": email,
            "role": payload.get("role", "user")
        }
        
    return user

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required"
        )
    return current_user
