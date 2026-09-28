import csv
import io
import json
from fastapi import APIRouter, HTTPException, Depends, Response, Query
from fastapi.responses import StreamingResponse
from app.auth.dependencies import get_current_user
from app.database.mongo import db_manager

router = APIRouter(prefix="/api/history", tags=["History & Export"])

@router.get("/")
async def get_history(
    search: str = Query(None),
    emotion: str = Query(None),
    intent: str = Query(None),
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user.get("user_id", current_user.get("_id", "guest")))
    query = {} if current_user.get("role") == "admin" else {"user_id": user_id}
    
    items = await db_manager.find("history", query, limit=limit)
    
    filtered = []
    for item in items:
        # Apply optional filters
        if search:
            s_lower = search.lower()
            fname = str(item.get("filename", "")).lower()
            rid = str(item.get("report_id", "")).lower()
            if s_lower not in fname and s_lower not in rid:
                continue

        if emotion and emotion.lower() not in str(item.get("primary_emotion", "")).lower():
            continue

        if intent and intent.lower() not in str(item.get("primary_intent", "")).lower():
            continue

        filtered.append(item)
        
    return filtered

@router.get("/export/{report_id}")
async def export_report(
    report_id: str,
    format: str = Query("json", pattern="^(json|csv|pdf)$"),
    current_user: dict = Depends(get_current_user)
):
    pred = await db_manager.find_one("predictions", {"report_id": report_id})
    if not pred:
        raise HTTPException(status_code=404, detail="Report not found")
        
    report = pred["report_data"]

    if format == "json":
        json_bytes = json.dumps(report, indent=2, default=str).encode("utf-8")
        return Response(
            content=json_bytes,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{report_id}_report.json"'}
        )

    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Report ID", report_id])
        writer.writerow(["Document Name", report["metadata"]["document_name"]])
        writer.writerow(["Document Type", report["metadata"]["document_type"]])
        writer.writerow(["Primary Emotion", report["emotion_analysis"]["primary_emotion"]])
        writer.writerow(["Hidden Emotion", report["emotion_analysis"]["hidden_emotion"]])
        writer.writerow(["Primary Intent", report["intent_analysis"]["primary_intent"]])
        writer.writerow(["Overall Tone", report["emotion_analysis"]["overall_tone"]])
        writer.writerow(["Confidence %", report["confidence_scores"]["overall_prediction"]])
        writer.writerow([])
        writer.writerow(["Keyword Rank", "Keyword", "Score"])
        for kw in report["keywords"]:
            writer.writerow([kw["rank"], kw["keyword"], kw["score"]])
            
        csv_str = output.getvalue()
        return Response(
            content=csv_str,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{report_id}_report.csv"'}
        )

    elif format == "pdf":
        # Generate formatted PDF
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#4F46E5"), spaceAfter=12)
            sub_title_style = ParagraphStyle('SubTitleStyle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor("#1E293B"), spaceBefore=10, spaceAfter=6)
            body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=10, leading=14, textColor=colors.HexColor("#334155"))

            story = []
            story.append(Paragraph(f"AI Psychological & Intent Analysis Report", title_style))
            story.append(Paragraph(f"Document Name: {report['metadata']['document_name']} | Type: {report['metadata']['document_type']} | Report ID: {report_id}", body_style))
            story.append(Spacer(1, 12))

            story.append(Paragraph("1. Emotion Analysis", sub_title_style))
            story.append(Paragraph(f"<b>Primary Emotion:</b> {report['emotion_analysis']['primary_emotion']} | <b>Hidden Emotion:</b> {report['emotion_analysis']['hidden_emotion']}", body_style))
            story.append(Paragraph(f"<b>Overall Tone:</b> {report['emotion_analysis']['overall_tone']}", body_style))
            story.append(Paragraph(f"<b>Reasoning:</b> {report['emotion_analysis']['emotion_reasoning']}", body_style))
            story.append(Spacer(1, 10))

            story.append(Paragraph("2. Intent Analysis", sub_title_style))
            story.append(Paragraph(f"<b>Primary Intent:</b> {report['intent_analysis']['primary_intent']} | <b>Future Intent:</b> {report['intent_analysis']['future_intent']}", body_style))
            story.append(Paragraph(f"<b>Reasoning:</b> {report['intent_analysis']['reasoning']}", body_style))
            story.append(Spacer(1, 10))

            story.append(Paragraph("3. Summary Insight", sub_title_style))
            story.append(Paragraph(report['summary_insight']['narrative_paragraph'], body_style))
            story.append(Spacer(1, 10))

            story.append(Paragraph("4. Final AI Conclusion", sub_title_style))
            story.append(Paragraph(report['final_conclusion'], body_style))

            doc.build(story)
            pdf_bytes = pdf_buffer.getvalue()
        except Exception as e:
            # Simple text/HTML PDF fallback
            pdf_bytes = f"AI Psychological & Intent Analysis Report\nReport ID: {report_id}\nDocument: {report['metadata']['document_name']}\nPrimary Emotion: {report['emotion_analysis']['primary_emotion']}\nHidden Emotion: {report['emotion_analysis']['hidden_emotion']}\nPrimary Intent: {report['intent_analysis']['primary_intent']}\n\nSummary Insight:\n{report['summary_insight']['narrative_paragraph']}\n\nFinal Conclusion:\n{report['final_conclusion']}".encode("utf-8")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{report_id}_report.pdf"'}
        )
