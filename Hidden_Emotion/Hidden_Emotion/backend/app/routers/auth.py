import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user_schema import UserRegister, UserLogin, TokenResponse, UserResponse
from app.auth.security import get_password_hash, verify_password
from app.auth.jwt_handler import create_access_token
from app.auth.dependencies import get_current_user
from app.database.mongo import db_manager

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    try:
        existing = await db_manager.find_one("users", {"email": user_data.email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
            
        hashed_pwd = get_password_hash(user_data.password)
        uid_str = f"USR-{uuid.uuid4().hex[:6].upper()}"
        new_user = {
            "user_id": uid_str,
            "username": str(user_data.username),
            "email": str(user_data.email),
            "password": str(hashed_pwd),
            "role": str(user_data.role or "user")
        }
        
        saved_user = await db_manager.insert_one("users", new_user)
        user_id_val = str(saved_user.get("user_id") or saved_user.get("_id") or uid_str)
        
        token_payload = {
            "sub": str(saved_user["email"]),
            "user_id": user_id_val,
            "username": str(saved_user["username"]),
            "role": str(saved_user["role"])
        }
        
        token = create_access_token(token_payload)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user_id_val,
                "username": str(saved_user["username"]),
                "email": str(saved_user["email"]),
                "role": str(saved_user["role"])
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration error: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    try:
        user = await db_manager.find_one("users", {"email": credentials.email})
        if not user or not verify_password(credentials.password, str(user["password"])):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
            
        user_id_val = str(user.get("user_id") or user.get("_id") or "USR-GUEST")
        token_payload = {
            "sub": str(user["email"]),
            "user_id": user_id_val,
            "username": str(user["username"]),
            "role": str(user["role"])
        }
        
        token = create_access_token(token_payload)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user_id_val,
                "username": str(user["username"]),
                "email": str(user["email"]),
                "role": str(user["role"])
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Login error: {str(e)}"
        )

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user.get("user_id", current_user.get("_id", "guest_id")),
        "username": current_user.get("username", "Guest User"),
        "email": current_user.get("email", "guest@analyzer.ai"),
        "role": current_user.get("role", "user")
    }
