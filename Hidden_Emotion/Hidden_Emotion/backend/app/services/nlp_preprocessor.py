import re
from typing import List, Dict, Any
import nltk
from app.config import settings

# Download NLTK data safely if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

ENGLISH_STOPWORDS = set(stopwords.words('english')) if 'stopwords' in nltk.corpus.__dict__ else {
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "what", "which", "this", "that", "these", "those",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "to", "from",
    "in", "out", "on", "off", "over", "under", "again", "further", "then", "once"
}

class NLPPreprocessor:
    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'http\S+|www\.\S+', '[URL]', text)
        text = re.sub(r'\S+@\S+', '[EMAIL]', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def get_sentences(text: str) -> List[str]:
        try:
            sentences = sent_tokenize(text)
        except Exception:
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        return [s for s in sentences if len(s.split()) >= 3]

    @staticmethod
    def tokenize_and_remove_stopwords(text: str) -> List[str]:
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        return [w for w in words if w not in ENGLISH_STOPWORDS]

    @staticmethod
    def create_semantic_chunks(text: str, chunk_size: int = None, overlap: int = None) -> List[Dict[str, Any]]:
        chunk_size = chunk_size or settings.CHUNK_SIZE_WORDS
        overlap = overlap or settings.CHUNK_OVERLAP_WORDS
        
        sentences = NLPPreprocessor.get_sentences(text)
        if not sentences:
            return [{"index": 0, "text": text, "word_count": len(text.split()), "sentence_count": 1}]

        chunks = []
        current_sentences = []
        current_word_count = 0
        chunk_idx = 0

        for sent in sentences:
            sent_words = len(sent.split())
            if current_word_count + sent_words > chunk_size and current_sentences:
                chunk_text = " ".join(current_sentences)
                chunks.append({
                    "index": chunk_idx,
                    "text": chunk_text,
                    "word_count": current_word_count,
                    "sentence_count": len(current_sentences)
                })
                chunk_idx += 1

                # Retain overlapping sentences
                overlap_words = 0
                overlap_sentences = []
                for prev_sent in reversed(current_sentences):
                    pw_count = len(prev_sent.split())
                    if overlap_words + pw_count <= overlap:
                        overlap_sentences.insert(0, prev_sent)
                        overlap_words += pw_count
                    else:
                        break
                
                current_sentences = overlap_sentences
                current_word_count = overlap_words

            current_sentences.append(sent)
            current_word_count += sent_words

        if current_sentences:
            chunks.append({
                "index": chunk_idx,
                "text": " ".join(current_sentences),
                "word_count": current_word_count,
                "sentence_count": len(current_sentences)
            })

        return chunks

nlp_preprocessor = NLPPreprocessor()
