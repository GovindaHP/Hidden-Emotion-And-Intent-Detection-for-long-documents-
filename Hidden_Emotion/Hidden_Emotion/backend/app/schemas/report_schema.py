from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TextInputRequest(BaseModel):
    title: Optional[str] = "Untitled Document"
    text: str = Field(..., min_length=10)
    doc_type: Optional[str] = "General"

class DocumentMetadata(BaseModel):
    document_name: str
    document_type: str
    upload_time: str
    word_count: int
    reading_time_minutes: float
    language: str

class EmotionAnalysis(BaseModel):
    primary_emotion: str
    secondary_emotion: Optional[str] = ""
    hidden_emotion: str
    positive_percentage: float
    neutral_percentage: float
    negative_percentage: float
    overall_tone: str
    confidence: float
    emotion_reasoning: str
    supporting_evidence: List[str]
    distribution: Dict[str, float]

class IntentAnalysis(BaseModel):
    primary_intent: str
    secondary_intent: Optional[str] = ""
    future_intent: Optional[str] = ""
    confidence: float
    reasoning: str
    supporting_sentences: List[str]

class SummaryInsight(BaseModel):
    what_happened: str
    why_feels_this_way: str
    what_user_wants: str
    problem_identified: str
    possible_next_action: Optional[str] = ""
    narrative_paragraph: str

class DocumentSummary(BaseModel):
    short_summary: str
    medium_summary: str
    detailed_summary: str
    bullet_summary: List[str]

class EntityExtraction(BaseModel):
    persons: List[str]
    organizations: List[str]
    locations: List[str]
    dates: List[str]
    technologies: List[str]
    products: List[str]

class KeywordInfo(BaseModel):
    keyword: str
    score: float
    rank: int

class TimelinePhase(BaseModel):
    phase: str
    dominant_emotion: str
    sentiment_score: float
    excerpt: str

class ConfidenceScores(BaseModel):
    emotion_detection: float
    intent_detection: float
    summary: float
    ner: float
    keywords: float
    overall_prediction: float

class ActionableSuggestion(BaseModel):
    category: Optional[str] = ""
    action: Optional[str] = ""
    priority: Optional[str] = ""

class ReportResponse(BaseModel):
    report_id: str
    metadata: DocumentMetadata
    emotion_analysis: EmotionAnalysis
    intent_analysis: IntentAnalysis
    summary_insight: SummaryInsight
    summaries: DocumentSummary
    keywords: List[KeywordInfo]
    entities: EntityExtraction
    main_topic: str
    sub_topics: List[str]
    important_sentences: List[str]
    emotional_timeline: List[TimelinePhase]
    confidence_scores: ConfidenceScores
    suggestions: Optional[List[ActionableSuggestion]] = []
    final_conclusion: str
