# Hidden Emotion & Intent Detection From Long Documents

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-success.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An Industry-Level Full Stack AI Application designed to read long documents (PDF, DOCX, TXT, Research Papers, Complaint Letters, Medical Reports, Legal Notices, Emails, Customer Reviews) and generate a **Psychological & Intent Analysis Report**.

---

## 🌟 Core Features

- **Long Document Context Engine**: Semantic sliding-window chunking (250 words, 50 word overlap) ensures transformer context limits are overcome without document truncation.
- **Hidden Emotion Detection**: Identifies discrepancies between surface statements and underlying psychological cues (repressed frustration, masked anxiety, hidden optimism, subconscious grief).
- **Deep Intent & Future Step Prediction**: Predicts Primary Intent, Secondary Intent, and Possible Future Action (e.g. escalation risk, cancellation intent, legal recourse).
- **Summary Insight Synthesis**: Generates human-readable narrative paragraphs answering: *What happened, Why the user feels this way, What the user wants, Problem identified, Next action*.
- **Multi-Level Document Summaries**: Produces Short, Medium, Detailed (multi-paragraph), and Bullet summaries.
- **Top 20 Keywords Extraction**: Powered by KeyBERT and TF-IDF rank scoring.
- **Named Entity Recognition (NER)**: Extracts Persons, Organizations, Locations, Dates, Technologies, and Products.
- **Emotional Timeline Trajectory**: Visualizes emotional shift across Beginning, Middle, Later, and Ending document phases.
- **Actionable AI Recommendations**: Automatically maps detected intent to enterprise workflow recommendations.
- **Multi-Format Report Export**: Download reports as PDF, JSON, or CSV.
- **Visual Analytics**: Interactive Chart.js charts for emotion distribution, sentiment split, intent confidence, and timeline graphs.
- **JWT Authentication & User/Admin Portal**: User login, upload history tracking, search & filters, admin user management, and system logs audit.
- **Dual Database Architecture**: MongoDB with automatic persistent local JSON DB fallback for zero-config standalone execution.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom Dark Mode & Glassmorphism design system), Responsive Grid (Bootstrap 5), JavaScript ES6, Chart.js, Font Awesome.
- **Backend**: Python 3.10+, FastAPI, Uvicorn, PyMongo, Motor, ReportLab.
- **Machine Learning & NLP**:
  - **Emotion**: `j-hartmann/emotion-english-distilroberta-base`
  - **Sentiment**: `distilbert-base-uncased-finetuned-sst-2-english`
  - **Summarization**: `facebook/bart-large-cnn`
  - **Embeddings**: `all-MiniLM-L6-v2`
  - **NER**: spaCy (`en_core_web_trf` / `en_core_web_sm`)
  - **Keywords**: KeyBERT & NLTK
- **Deployment**: Docker, Docker Compose, GitHub Actions.

---

## 📂 Project Structure

```
Hidden_Emotion/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI core app & static mount
│   │   ├── config.py                   # App config & environment variables
│   │   ├── auth/                       # JWT security & dependencies
│   │   ├── database/                   # Mongo & local JSON database fallback
│   │   ├── services/                   # AI/NLP pipeline modules
│   │   │   ├── text_extractor.py       # PDF, DOCX, TXT file parser
│   │   │   ├── nlp_preprocessor.py     # Tokenizer, cleaning, chunker
│   │   │   ├── embedding_service.py    # SentenceTransformers vectorizer
│   │   │   ├── emotion_service.py      # Primary, secondary, hidden emotion engine
│   │   │   ├── intent_service.py       # Primary, secondary, future intent engine
│   │   │   ├── sentiment_service.py    # Sentiment split analyzer
│   │   │   ├── summarizer_service.py   # BART & TextRank summarizers
│   │   │   ├── ner_service.py          # Entity recognition service
│   │   │   ├── keyword_service.py      # KeyBERT top 20 keywords
│   │   │   ├── timeline_service.py     # Phase trajectory analyzer
│   │   │   └── report_generator.py     # Master AI report synthesizer
│   │   ├── routers/                    # REST API routers
│   │   │   ├── auth.py
│   │   │   ├── documents.py
│   │   │   ├── predictions.py
│   │   │   ├── history.py
│   │   │   ├── analytics.py
│   │   │   └── admin.py
│   │   └── schemas/                    # Pydantic data schemas
│   ├── tests/                          # Pytest unit & integration tests
│   │   ├── test_nlp.py
│   │   └── test_api.py
│   ├── requirements.txt                # Python dependencies
│   └── Dockerfile                      # Backend container configuration
├── frontend/
│   ├── index.html                      # Single page application UI
│   ├── css/
│   │   └── style.css                   # Custom dark mode glassmorphism styles
│   └── js/
│       ├── app.js                      # Main UI controller & stepper
│       ├── auth.js                     # JWT auth session manager
│       ├── charts.js                   # Chart.js visualizer
│       ├── report.js                   # Report renderer
│       ├── history.js                  # History manager & filters
│       └── admin.js                    # Admin dashboard controller
├── docs/                               # Comprehensive Technical Docs
│   ├── ARCHITECTURE.md
│   ├── DFD.md
│   ├── USE_CASE.md
│   ├── SEQUENCE_DIAGRAM.md
│   ├── ER_DIAGRAM.md
│   ├── API_DOCUMENTATION.md
│   └── DEPLOYMENT_GUIDE.md
├── docker-compose.yml                  # Docker Compose orchestration
├── .github/
│   └── workflows/
│       └── ci.yml                      # CI workflow
└── README.md
```

---

## ⚡ Quick Start

### Option 1: Standalone Run (Local Machine)

1. Clone repository and navigate to `backend`:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run FastAPI application:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. Open your browser at `http://localhost:8000/`.

---

### Option 2: Docker Compose

```bash
docker-compose up --build
```
Access the application at `http://localhost:8000/`.

---

## 🧪 Running Unit & Integration Tests

```bash
cd backend
pytest
```

---

## 📄 License

MIT License. Designed and developed as a complete industry-level full stack AI document analysis solution.
