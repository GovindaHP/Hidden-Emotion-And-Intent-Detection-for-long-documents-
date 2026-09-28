# Deployment Guide

## Project Title: Hidden Emotion & Intent Detection From Long Documents

---

## 1. Local Execution (Standalone)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Launch Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Access application UI at: `http://localhost:8000/`

---

## 2. Docker & Docker Compose Deployment

### Step 1: Build & Launch Container Stack
```bash
docker-compose up --build -d
```

---

## 3. Cloud Deployment (Render / Railway / MongoDB Atlas)

1. **MongoDB Atlas**:
   - Create a MongoDB cluster on MongoDB Atlas.
   - Obtain connection string URI and set `MONGODB_URL` environment variable.
2. **Render / Railway**:
   - Deploy backend service from GitHub repository.
   - Set environment variable `SECRET_KEY` and `MONGODB_URL`.
