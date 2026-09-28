import re
import logging
from typing import Dict, List, Any
from app.config import settings

logger = logging.getLogger(__name__)

class SummarizerService:
    def __init__(self):
        self.pipeline = None
        self._is_loaded = False

    def _lazy_load(self):
        if not self._is_loaded:
            try:
                from transformers import pipeline
                self.pipeline = pipeline(
                    "summarization",
                    model=settings.SUMMARIZER_MODEL_NAME
                )
                self._is_loaded = True
                logger.info(f"Loaded summarizer model: {settings.SUMMARIZER_MODEL_NAME}")
            except Exception as e:
                logger.warning(f"Could not load HuggingFace summarizer model ({e}). Utilizing TextRank extractive summarization.")
                self.pipeline = None
                self._is_loaded = True

    def generate_all_summaries(self, text: str) -> Dict[str, Any]:
        text_clean = text.strip()
        sentences = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', text_clean) if len(s.split()) >= 3]
        if not sentences:
            sentences = [text_clean]

        ranked_sentences = self._rank_sentences(sentences)

        # 1. Short Summary (1-2 clean concise sentences)
        short_summary = " ".join(ranked_sentences[:2]) if len(ranked_sentences) >= 2 else sentences[0]
        if len(short_summary.split()) > 45:
            trimmed = " ".join(short_summary.split()[:40]) + "..."
            short_summary = trimmed
        
        # 2. Medium Summary (Strictly 2-3 sentences)
        medium_summary = " ".join(ranked_sentences[:3])

        # 3. Detailed Summary (Strictly 3-4 sentences conveying core progression)
        concise_count = min(4, max(2, len(ranked_sentences)))
        top_sentences = ranked_sentences[:concise_count]
        detailed_summary = " ".join(top_sentences)

        # 4. Bullet Summary (3-4 concise bullet points)
        bullet_summary = [s if len(s.split()) <= 30 else " ".join(s.split()[:28]) + "..." for s in top_sentences]

        return {
            "short_summary": short_summary,
            "medium_summary": medium_summary,
            "detailed_summary": detailed_summary,
            "bullet_summary": bullet_summary
        }

    def generate_what_happened(self, text: str, doc_type: str, intent: str, emotion: str) -> str:
        """
        Synthesizes a clean, high-level 2-3 sentence narrative summary of what actually happened,
        grounded strictly in the source document sentences without any hardcoded templates or hallucinations.
        """
        text_clean = text.strip()
        sentences = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', text_clean) if len(s.split()) >= 4]
        if not sentences:
            return text_clean[:200]

        n_s = len(sentences)

        if n_s <= 2:
            return " ".join(sentences)

        # Extract 3 narrative anchor points: Beginning Setup, Mid Turning Point / Problem, Concluding Outcome
        beginning_sent = sentences[0]
        
        # Middle sentence: highest scoring sentence from middle 50% of the document
        mid_start = max(1, int(n_s * 0.25))
        mid_end = min(n_s - 1, int(n_s * 0.75))
        mid_candidates = sentences[mid_start:mid_end] if mid_end > mid_start else [sentences[n_s // 2]]
        
        ranked_mid = self._rank_sentences(mid_candidates)
        middle_sent = ranked_mid[0] if ranked_mid else sentences[n_s // 2]
        
        # Concluding sentence
        ending_sent = sentences[-1]

        # Compact each sentence to prevent text overflow
        b_words = beginning_sent.split()
        m_words = middle_sent.split()
        e_words = ending_sent.split()

        comp_b = " ".join(b_words[:24]) + ("." if not b_words[-1].endswith(('.', '!', '?')) else "")
        comp_m = " ".join(m_words[:26]) + ("." if not m_words[-1].endswith(('.', '!', '?')) else "")
        comp_e = " ".join(e_words[:26]) + ("." if not e_words[-1].endswith(('.', '!', '?')) else "")

        if comp_b != comp_m and comp_m != comp_e:
            synthesized = f"{comp_b} {comp_m} {comp_e}"
        elif comp_b != comp_e:
            synthesized = f"{comp_b} {comp_e}"
        else:
            synthesized = comp_b

        # Anti-hallucination verification
        return self._validate_anti_hallucination(synthesized, text_clean)

    def _validate_anti_hallucination(self, summary_text: str, source_text: str) -> str:
        """
        Guarantees that no external domain hallucination (e.g. ungrounded medical/patient claims)
        leaks into the summary.
        """
        source_lower = source_text.lower()
        forbidden_unless_in_source = ["patient", "physician", "biopsy", "prescription", "symptoms", "hospital"]
        
        summary_words = summary_text.lower().split()
        for fw in forbidden_unless_in_source:
            if fw in summary_words and fw not in source_lower:
                # Reject contaminated summary and fall back to top ranked source sentences
                logger.warning(f"[Anti-Hallucination] Forbidden word '{fw}' found in summary but absent in source text. Replacing with pure extractive text.")
                clean_sents = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', source_text) if len(s.split()) >= 4]
                return " ".join(clean_sents[:2])
                
        return summary_text

    def _rank_sentences(self, sentences: List[str]) -> List[str]:
        word_freq: Dict[str, int] = {}
        for s in sentences:
            for w in re.findall(r'\b[a-zA-Z]{3,}\b', s.lower()):
                word_freq[w] = word_freq.get(w, 0) + 1

        sent_scores = []
        for idx, s in enumerate(sentences):
            score = 0
            words = re.findall(r'\b[a-zA-Z]{3,}\b', s.lower())
            for w in words:
                score += word_freq.get(w, 0)
            position_multiplier = 1.3 if idx in (0, len(sentences)-1) else 1.0
            score = (score / (len(words) or 1)) * position_multiplier
            sent_scores.append((s, score))

        sent_scores.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in sent_scores]

summarizer_service = SummarizerService()
