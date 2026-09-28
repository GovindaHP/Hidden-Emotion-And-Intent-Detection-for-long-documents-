# System Architecture Documentation

## Project Title: Hidden Emotion & Intent Detection From Long Documents

---

## 1. High-Level Architecture

The system follows a microservices-inspired modular full-stack architecture comprising a **FastAPI Machine Learning Backend**, a **Responsive Single-Page Web Frontend** (HTML5, Glassmorphism CSS, ES6 Javascript, Chart.js), and a **Dual Storage Engine** (MongoDB + High-Performance Local JSON Fallback).

```
+---------------------------------------------------------------------------------+
|                                 CLIENT LAYER                                    |
|   HTML5 / Glassmorphism CSS / Vanilla ES6 JS / Chart.js / Font Awesome Icons    |
+---------------------------------------------------------------------------------+
                                       |
                                       | HTTP REST API / JWT Bearer Tokens
                                       v
+---------------------------------------------------------------------------------+
|                                FASTAPI BACKEND                                  |
|   - Authentication Middleware (JWT)                                             |
|   - Multi-Format File Parser (PDF, DOCX, TXT)                                   |
|   - OpenAPI Router Gateway                                                      |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                              AI & NLP PIPELINE                                  |
|   1. Cleaning & Tokenization (NLTK)                                             |
|   2. Semantic Sliding-Window Chunking (250 words, 50 word overlap)              |
|   3. Embedding Generator (all-MiniLM-L6-v2)                                     |
|   4. Emotion Classifier (j-hartmann/emotion-english-distilroberta-base)         |
|   5. Hidden Emotion Inference & Evidence Sentence Extraction                    |
|   6. Intent Classification & Future Step Predictor                              |
|   7. Sentiment Split Analysis (distilbert-base-uncased-finetuned-sst-2-english) |
|   8. Multi-Level Abstractive/Extractive Summarization (facebook/bart-large-cnn) |
|   9. Named Entity Recognition (spaCy)                                           |
|  10. Top 20 Keyword Ranking (KeyBERT)                                           |
|  11. Emotional Timeline Trajectory Across Document Phases                       |
|  12. Master Psychological Report Aggregator                                     |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                             DATA PERSISTENCE LAYER                              |
|   - Primary: MongoDB (Motor Async Driver)                                       |
|   - Zero-Config Standalone Fallback: Local Persistent JSON Database             |
+---------------------------------------------------------------------------------+
```

---

## 2. Long Document Chunking & Aggregation Engine

Transformer models encounter strict maximum context length limits (typically 512 tokens). To prevent document truncation and preserve full contextual integrity across lengthy documents:

1. **Text Extraction**: Converts incoming files (PDF, DOCX, TXT) into unified UTF-8 text strings.
2. **Semantic Sentence Splitting**: Identifies sentence boundaries using NLTK `sent_tokenize`.
3. **Sliding Window Chunking**: Group sentences into chunks of 250 words with a 50-word overlap between consecutive chunks.
4. **Vector Embedding**: Each chunk is transformed into a dense vector embedding using `all-MiniLM-L6-v2`.
5. **Prediction Aggregation**:
   - Scores from all chunks are accumulated to compute exact document-wide emotion distributions.
   - Discrepancies between surface statements and underlying chunk sentiment trigger **Hidden Emotion Inference** (e.g. detecting repressed frustration behind formal civility).
