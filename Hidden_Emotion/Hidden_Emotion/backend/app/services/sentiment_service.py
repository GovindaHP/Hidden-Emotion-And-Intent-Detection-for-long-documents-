import logging
from typing import Dict, List, Any
from app.config import settings

logger = logging.getLogger(__name__)

class SentimentService:
    def __init__(self):
        self.pipeline = None
        self._is_loaded = False

    def _lazy_load(self):
        if not self._is_loaded:
            try:
                from transformers import pipeline
                self.pipeline = pipeline(
                    "text-classification",
                    model=settings.SENTIMENT_MODEL_NAME,
                    return_all_scores=True
                )
                self._is_loaded = True
                logger.info(f"Loaded sentiment model: {settings.SENTIMENT_MODEL_NAME}")
            except Exception as e:
                logger.warning(f"Could not load HuggingFace sentiment model ({e}). Utilizing VADER/lexicon fallback.")
                self.pipeline = None
                self._is_loaded = True

    def analyze_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self._lazy_load()
        results = []
        for chunk in chunks:
            text = chunk["text"]
            score = self.score_text(text)
            results.append({
                "chunk_index": chunk["index"],
                "positive": score["positive"],
                "negative": score["negative"],
                "neutral": score["neutral"],
                "compound": score["compound"]
            })
        return results

    def score_text(self, text: str) -> Dict[str, float]:
        if self.pipeline is not None:
            try:
                res = self.pipeline(text[:512])[0]
                pos_score = next((item["score"] for item in res if item["label"].upper() in ["POSITIVE", "LABEL_1"]), 0.5)
                neg_score = next((item["score"] for item in res if item["label"].upper() in ["NEGATIVE", "LABEL_0"]), 0.5)
                neu_score = round(max(0.0, 1.0 - (pos_score + neg_score)), 2)
                compound = round(pos_score - neg_score, 2)
                return {"positive": round(pos_score, 3), "negative": round(neg_score, 3), "neutral": neu_score, "compound": compound}
            except Exception:
                pass
                
        # Rule-based sentiment fallback
        words = text.lower().split()
        pos_words = {"good", "great", "excellent", "happy", "love", "awesome", "fantastic", "positive", "solution", "resolve", "improved", "best"}
        neg_words = {"bad", "terrible", "worst", "error", "fail", "issue", "problem", "hate", "unacceptable", "broken", "loss", "useless"}
        
        pos_cnt = sum(1 for w in words if w in pos_words)
        neg_cnt = sum(1 for w in words if w in neg_words)
        tot = len(words) or 1
        
        pos_ratio = min(1.0, (pos_cnt * 3) / tot)
        neg_ratio = min(1.0, (neg_cnt * 3) / tot)
        neu_ratio = max(0.0, round(1.0 - pos_ratio - neg_ratio, 2))
        
        return {
            "positive": round(pos_ratio, 2),
            "negative": round(neg_ratio, 2),
            "neutral": neu_ratio,
            "compound": round(pos_ratio - neg_ratio, 2)
        }

sentiment_service = SentimentService()
