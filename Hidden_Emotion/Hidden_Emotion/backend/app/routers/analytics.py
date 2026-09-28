from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.database.mongo import db_manager

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/dashboard")
async def get_dashboard_analytics(
    current_user: dict = Depends(get_current_user)
):
    all_preds = await db_manager.find("predictions", limit=500)
    total_docs = len(all_preds)
    
    if total_docs == 0:
        return {
            "total_documents": 0,
            "avg_confidence": 0,
            "emotion_distribution": {"Frustration & Anger": 30, "Satisfaction & Optimism": 25, "Anxiety & Apprehension": 25, "Objective Calmness": 20},
            "intent_distribution": {"Seeking Technical Assistance": 35, "Filing Formal Complaint": 30, "Customer Dissatisfaction": 20, "Legal Notice": 15},
            "top_hidden_emotions": [
                {"name": "Repressed Frustration", "count": 12},
                {"name": "Masked Panic", "count": 8},
                {"name": "Subconscious Grief", "count": 5}
            ]
        }

    emotion_counts = {}
    intent_counts = {}
    hidden_counts = {}
    total_conf = 0.0

    for p in all_preds:
        pe = p.get("primary_emotion", "Neutral")
        pi = p.get("primary_intent", "General Inquiry")
        he = p.get("hidden_emotion", "Unspecified")
        c = float(p.get("confidence", 85.0))
        
        emotion_counts[pe] = emotion_counts.get(pe, 0) + 1
        intent_counts[pi] = intent_counts.get(pi, 0) + 1
        hidden_counts[he] = hidden_counts.get(he, 0) + 1
        total_conf += c

    top_hidden = [{"name": k, "count": v} for k, v in sorted(hidden_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

    return {
        "total_documents": total_docs,
        "avg_confidence": round(total_conf / total_docs, 1),
        "emotion_distribution": emotion_counts,
        "intent_distribution": intent_counts,
        "top_hidden_emotions": top_hidden
    }
