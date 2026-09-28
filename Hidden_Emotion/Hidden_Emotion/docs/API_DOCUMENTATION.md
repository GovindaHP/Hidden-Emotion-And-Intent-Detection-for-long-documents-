# API Documentation

## Base URL: `http://localhost:8000/api`

---

## 1. Authentication Endpoints

### `POST /auth/register`
Registers a new user account.
- **Request Body**:
  ```json
  {
    "username": "jsmith",
    "email": "jsmith@company.com",
    "password": "secretpassword",
    "role": "user"
  }
  ```
- **Response**: JWT access token and user profile object.

### `POST /auth/login`
Authenticates existing credentials.
- **Request Body**:
  ```json
  {
    "email": "jsmith@company.com",
    "password": "secretpassword"
  }
  ```
- **Response**: JWT access token.

---

## 2. Document Processing Endpoints

### `POST /documents/upload`
Uploads a document file (`.pdf`, `.docx`, `.txt`) and executes the full NLP pipeline.
- **Form Data**:
  - `file`: Multipart binary file
  - `doc_type`: "General", "Complaint Letter", "Research Paper", "Medical Report", "Legal Document", etc.
- **Response**: Complete AI Psychological & Intent Analysis Report JSON.

### `POST /documents/analyze-text`
Analyzes raw long text input.
- **Request Body**:
  ```json
  {
    "title": "Escalation Letter",
    "text": "Full document content...",
    "doc_type": "Complaint Letter"
  }
  ```
- **Response**: Complete AI Report JSON.

---

## 3. History & Export Endpoints

### `GET /history/`
Returns historical document predictions with optional search & filter parameters (`search`, `emotion`, `intent`).

### `GET /history/export/{report_id}?format=pdf|csv|json`
Downloads formatted PDF report, CSV table, or raw JSON data.
