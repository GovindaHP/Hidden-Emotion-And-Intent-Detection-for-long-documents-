import os
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.services.text_extractor import text_extractor
from app.services.report_generator import report_generator
from app.database.mongo import db_manager
from app.schemas.report_schema import TextInputRequest

router = APIRouter(prefix="/api/documents", tags=["Document Processing"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("General"),
    current_user: dict = Depends(get_current_user)
):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
            
        contents = await file.read()
        if len(contents) > 15 * 1024 * 1024: # 15 MB
            raise HTTPException(status_code=400, detail="File size exceeds 15 MB limit")
            
        raw_text = text_extractor.extract_text(contents, file.filename)
        if not raw_text or len(raw_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Could not extract readable text from document. Please ensure the file contains extractable text.")

        report = report_generator.generate(raw_text, filename=file.filename, doc_type=doc_type)

        user_id = current_user.get("username", "guest")
        pred_entry = {
            "report_id": report["report_id"],
            "doc_id": report["report_id"],
            "user_id": user_id,
            "filename": file.filename,
            "primary_emotion": report["emotion_analysis"]["primary_emotion"],
            "hidden_emotion": report["emotion_analysis"]["hidden_emotion"],
            "primary_intent": report["intent_analysis"]["primary_intent"],
            "overall_tone": report["emotion_analysis"]["overall_tone"],
            "confidence": report["confidence_scores"]["overall_prediction"],
            "report_data": report,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        await db_manager.insert_one("documents", {
            "doc_id": report["report_id"],
            "filename": file.filename,
            "doc_type": doc_type,
            "word_count": report["metadata"]["word_count"],
            "uploaded_by": user_id,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        })
        await db_manager.insert_one("predictions", pred_entry)
        await db_manager.insert_one("history", pred_entry)

        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@router.post("/analyze-text")
async def analyze_text(
    payload: TextInputRequest,
    current_user: dict = Depends(get_current_user)
):
    if not payload.text or len(payload.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text content is too short for analysis")

    title = payload.title if payload.title and payload.title.strip() else "Pasted Text Document"
    report = report_generator.generate(payload.text, filename=title, doc_type=payload.doc_type or "General")

    user_id = current_user.get("username", "guest")
    pred_entry = {
        "report_id": report["report_id"],
        "doc_id": report["report_id"],
        "user_id": user_id,
        "filename": title,
        "primary_emotion": report["emotion_analysis"]["primary_emotion"],
        "hidden_emotion": report["emotion_analysis"]["hidden_emotion"],
        "primary_intent": report["intent_analysis"]["primary_intent"],
        "overall_tone": report["emotion_analysis"]["overall_tone"],
        "confidence": report["confidence_scores"]["overall_prediction"],
        "report_data": report,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db_manager.insert_one("documents", {
        "doc_id": report["report_id"],
        "filename": title,
        "doc_type": payload.doc_type or "General",
        "word_count": report["metadata"]["word_count"],
        "uploaded_by": user_id,
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    })
    await db_manager.insert_one("predictions", pred_entry)
    await db_manager.insert_one("history", pred_entry)

    return report
