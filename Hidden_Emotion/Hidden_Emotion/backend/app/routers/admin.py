from fastapi import APIRouter, Depends
from app.auth.dependencies import get_admin_user
from app.database.mongo import db_manager

router = APIRouter(prefix="/api/admin", tags=["Admin Portal"])

@router.get("/users")
async def list_users(admin: dict = Depends(get_admin_user)):
    users = await db_manager.find("users", limit=100)
    # Strip passwords
    clean_users = []
    for u in users:
        clean_users.append({
            "id": u.get("user_id", u.get("_id")),
            "username": u.get("username"),
            "email": u.get("email"),
            "role": u.get("role", "user"),
            "created_at": u.get("created_at")
        })
    return clean_users

@router.get("/logs")
async def list_logs(admin: dict = Depends(get_admin_user)):
    logs = await db_manager.find("logs", limit=100)
    return logs

@router.get("/system-status")
async def get_system_status(admin: dict = Depends(get_admin_user)):
    user_count = await db_manager.count("users")
    doc_count = await db_manager.count("documents")
    pred_count = await db_manager.count("predictions")
    
    return {
        "status": "HEALTHY",
        "database": "MongoDB (Active)" if db_manager.is_mongo_connected else "Local File DB (Active)",
        "users_count": user_count,
        "documents_count": doc_count,
        "predictions_count": pred_count,
        "engine_version": "1.0.0-PROD"
    }
