from fastapi import APIRouter, HTTPException, Depends
from app.auth.dependencies import get_current_user
from app.database.mongo import db_manager

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

@router.get("/{report_id}")
async def get_prediction_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    pred = await db_manager.find_one("predictions", {"report_id": report_id})
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction report not found")
    return pred["report_data"]

@router.get("/")
async def list_user_predictions(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user.get("user_id", current_user.get("_id", "guest")))
    query = {} if current_user.get("role") == "admin" else {"user_id": user_id}
    
    preds = await db_manager.find("predictions", query, limit=limit)
    
    summary_list = []
    for p in preds:
        report_data = p.get("report_data", {})
        summary_list.append({
            "report_id": p.get("report_id"),
            "filename": p.get("filename"),
            "primary_emotion": p.get("primary_emotion"),
            "hidden_emotion": p.get("hidden_emotion"),
            "primary_intent": p.get("primary_intent"),
            "overall_tone": p.get("overall_tone"),
            "confidence": p.get("confidence"),
            "created_at": p.get("created_at"),
            "document_type": report_data.get("metadata", {}).get("document_type", "General")
        })
    return summary_list
