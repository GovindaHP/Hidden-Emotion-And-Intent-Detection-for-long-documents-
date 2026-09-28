import re
import logging
from typing import List, Dict, Any
from app.config import settings
from app.services.nlp_preprocessor import nlp_preprocessor

logger = logging.getLogger(__name__)

class KeywordService:
    def __init__(self):
        self.kw_model = None
        self._is_loaded = False

    def _lazy_load(self):
        if not self._is_loaded:
            try:
                from keybert import KeyBERT
                self.kw_model = KeyBERT()
                self._is_loaded = True
                logger.info("Loaded KeyBERT model.")
            except Exception as e:
                logger.warning(f"Could not load KeyBERT ({e}). Utilizing TF-IDF keyword ranker.")
                self.kw_model = None
                self._is_loaded = True

    def extract_top_keywords(self, text: str, top_n: int = 20) -> List[Dict[str, Any]]:
        self._lazy_load()

        if self.kw_model is not None and len(text.split()) > 15:
            try:
                keywords_raw = self.kw_model.extract_keywords(
                    text, 
                    keyphrase_ngram_range=(1, 2), 
                    stop_words='english', 
                    top_n=top_n
                )
                results = []
                for idx, (kw, score) in enumerate(keywords_raw, start=1):
                    results.append({
                        "keyword": kw.title(),
                        "score": round(float(score), 4),
                        "rank": idx
                    })
                return results
            except Exception as e:
                logger.error(f"KeyBERT extraction failed: {e}")

        # TF-IDF / Term Frequency fallback keyword ranker
        words = nlp_preprocessor.tokenize_and_remove_stopwords(text)
        freq_map: Dict[str, int] = {}
        for w in words:
            if len(w) >= 3:
                freq_map[w] = freq_map.get(w, 0) + 1

        sorted_words = sorted(freq_map.items(), key=lambda x: x[1], reverse=True)[:top_n]
        max_freq = sorted_words[0][1] if sorted_words else 1

        results = []
        for idx, (kw, freq) in enumerate(sorted_words, start=1):
            score = round(min(0.99, max(0.20, (freq / max_freq) * 0.9 + 0.1)), 4)
            results.append({
                "keyword": kw.title(),
                "score": score,
                "rank": idx
            })

        return results

keyword_service = KeywordService()
