import re
from typing import List, Dict, Any
from app.services.emotion_service import emotion_service
from app.services.intent_service import intent_service
from app.services.sentiment_service import sentiment_service

class TimelineService:
    @staticmethod
    def generate_timeline(chunks: List[Dict[str, Any]], doc_type: str = "General", doc_id: str = "DOC-UNKNOWN") -> List[Dict[str, Any]]:
        full_text = " ".join([c["text"] for c in chunks])
        sentences = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', full_text) if len(s.split()) >= 3]

        if not sentences:
            sentences = [full_text]

        phase_names = [
            ("Beginning", "Opening Context & Setup"),
            ("Middle", "Obstacles, Events & Friction"),
            ("Later", "Turning Point & Escalation"),
            ("Ending", "Resolution & Terminal Outcome")
        ]

        phases = []
        n_sentences = len(sentences)

        if n_sentences == 1:
            phases.append(TimelineService._analyze_phase("Overview", "Full Document Context", sentences[0], doc_type, 0, doc_id))
        elif n_sentences <= 4:
            for idx in range(min(n_sentences, 4)):
                p_name, p_label = phase_names[idx]
                phases.append(TimelineService._analyze_phase(p_name, p_label, sentences[idx], doc_type, idx, doc_id))
        else:
            step = n_sentences / 4.0
            for idx, (p_name, p_label) in enumerate(phase_names):
                start_i = int(idx * step)
                end_i = int((idx + 1) * step) if idx < 3 else n_sentences
                seg_text = " ".join(sentences[start_i:end_i])
                phases.append(TimelineService._analyze_phase(p_name, p_label, seg_text, doc_type, idx, doc_id))

        return phases

    @staticmethod
    def _analyze_phase(phase_name: str, phase_label: str, text: str, doc_type: str, phase_index: int, doc_id: str) -> Dict[str, Any]:
        emo_res = emotion_service.analyze(text, [{"index": 0, "text": text}], doc_id=f"{doc_id}-p{phase_index}")
        intent_res = intent_service.analyze(text, doc_type, doc_id=f"{doc_id}-p{phase_index}")
        senti_res = sentiment_service.score_text(text)
        
        sentences = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', text) if len(s.split()) >= 3]
        excerpt = sentences[0] if sentences else text[:120]
        if len(excerpt) > 130:
            excerpt = excerpt[:127] + "..."

        p_emo = emo_res["primary_emotion"]
        h_emo = emo_res["hidden_emotion"]
        p_intent = intent_res["primary_intent"]

        if senti_res["compound"] >= 0.15:
            emo_flow_desc = f"Exhibits an optimistic tone of {p_emo.lower()}, expressing progress or positive feedback."
        elif senti_res["compound"] <= -0.15:
            emo_flow_desc = f"Reflects a critical tone of {p_emo.lower()}, highlighting obstacles or emotional tension."
        else:
            emo_flow_desc = f"Maintains an observational tone centered around {p_emo.lower()}."

        if "General Informational" not in p_intent and "No Intent" not in p_intent:
            intent_flow_desc = f"Focuses on {p_intent.lower()}, addressing phase-specific objectives."
        else:
            intent_flow_desc = "Provides descriptive background context and event details."

        return {
            "phase": phase_name,
            "phase_label": phase_label,
            "dominant_emotion": p_emo,
            "hidden_emotion": h_emo,
            "emotion_flow_description": emo_flow_desc,
            "phase_intent": p_intent,
            "intent_flow_description": intent_flow_desc,
            "sentiment_score": senti_res["compound"],
            "positive_pct": emo_res["positive_percentage"],
            "neutral_pct": emo_res["neutral_percentage"],
            "negative_pct": emo_res["negative_percentage"],
            "excerpt": excerpt
        }

timeline_service = TimelineService()
