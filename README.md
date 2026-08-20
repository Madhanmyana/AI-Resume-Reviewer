# 🤖 AI Resume Reviewer

An intelligent resume analysis API built with **FastAPI** that leverages LLMs to provide professional resume reviews and actionable improvement suggestions. Upload a PDF resume and receive a comprehensive, structured evaluation covering ATS compatibility, impact metrics, language quality, and skills optimization.

---

## ✨ Features

- **PDF Resume Upload** — Upload any PDF resume (up to 5 MB, 10 pages)
- **AI-Powered Review** — Scores your resume across 4 dimensions (out of 100)
- **Actionable Improvements** — Rewrites weak bullets, improves your summary, and suggests ATS keywords
- **Structured JSON Response** — Fully typed Pydantic response models for easy frontend integration
- **Target Role Tailoring** — Optionally specify a target role for role-specific feedback
- **Rate Limiting** — Built-in protection against API abuse (5 requests/minute per IP)
- **Robust Validation** — 8 layers of input validation before any LLM call
- **Comprehensive Test Suite** — 58 tests with 99% code coverage

---

## 🏗️ Architecture

```
POST /review-resume (PDF + optional target_role)
        │
        ▼
┌─────────────────────┐
│   File Validation    │  content type, empty check, magic bytes,
│   (8 checks)         │  file size, corruption, page count,
│                      │  text extraction, text length
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   PDF Text           │  PyMuPDF extracts readable text
│   Extraction         │  from all pages
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Resume Review      │  LLM Call #1 → ResumeReviewResponse
│   Service            │  (scores, strengths, weaknesses,
│                      │   bullet transformations, hiring readiness)
└────────┬────────────┘
         │  review result passed directly ↓
         ▼
┌─────────────────────┐
│   Resume Improvement │  LLM Call #2 → ResumeImprovementResponse
│   Service            │  (improved summary, bullets, skills,
│                      │   ATS keyword suggestions)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Combined Response  │  ResumeAnalysisResponse
│   { review,          │  (both results in one JSON response)
│     improvements }   │
└─────────────────────┘
```

> **Key Design Decision**: The review result from LLM Call #1 is passed directly into LLM Call #2. The resume is reviewed **once**, and improvements are generated based on that review — no duplicate LLM calls.

---

## 📁 Project Structure

```
ai-resume-reviewer/
├── app/
│   ├── main.py                              # FastAPI app, routers, rate limiter setup
│   ├── limiter.py                           # SlowAPI rate limiter configuration
│   ├── api/
│   │   ├── api.py                           # POST /review-resume endpoint
│   │   └── health.py                        # GET /health endpoint
│   ├── prompts/
│   │   ├── resume_review_prompt.py          # LLM prompt for resume scoring
│   │   └── resume_improvement_prompt.py     # LLM prompt for improvement suggestions
│   ├── schemas/
│   │   ├── resume_review_schema.py          # Pydantic models for review response
│   │   ├── resume_improvement_schema.py     # Pydantic models for improvement response
│   │   └── resume_analysis_response_schema.py  # Combined response model
│   └── services/
│       ├── resume_upload_service.py         # PDF validation & text extraction
│       ├── resume_review_service.py         # LLM review call (Groq API)
│       └── resume_improvement_service.py    # LLM improvement call (Groq API)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                          # Shared fixtures & test configuration
│   ├── test_basic.py                        # Pytest learning tests
│   ├── test_schemas.py                      # Pydantic schema validation tests
│   ├── test_upload_service.py               # File validation & PDF processing tests
│   ├── test_review_service.py               # Review service unit tests
│   ├── test_improvement_service.py          # Improvement service unit tests
│   └── test_api_endpoint.py                 # Endpoint integration tests
├── .env                                     # GROQ_API_KEY (not committed)
├── .gitignore
├── pytest.ini                               # Pytest configuration
└── requirements.txt                         # Python dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com/keys)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Madhanmyana/AI-Resume-Reviewer.git
   cd AI-Resume-Reviewer
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Run the server**
   ```bash
   cd app
   uvicorn main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`

---

## 📡 API Reference

### Health Check

```http
GET /health
```

**Response** `200 OK`
```json
{
  "health": "healthy"
}
```

---

### Review Resume

```http
POST /review-resume
```

**Parameters**

| Parameter     | Type         | In    | Required | Description                              |
|---------------|--------------|-------|----------|------------------------------------------|
| `resume`      | `file`       | form  | ✅       | PDF file (max 5 MB, max 10 pages)        |
| `target_role` | `string`     | query | ❌       | Target job role for tailored feedback     |

**Example Request (cURL)**
```bash
curl -X POST "http://127.0.0.1:8000/review-resume?target_role=Backend%20Engineer" \
  -F "resume=@my_resume.pdf"
```

**Example Request (Python)**
```python
import requests

with open("my_resume.pdf", "rb") as f:
    response = requests.post(
        "http://127.0.0.1:8000/review-resume",
        params={"target_role": "Backend Engineer"},
        files={"resume": ("resume.pdf", f, "application/pdf")},
    )

print(response.json())
```

**Response** `200 OK`
```json
{
  "review": {
    "overall_score": 72,
    "category_scores": {
      "ATS_structure": 18,
      "impact_and_metrics": 20,
      "language_and_brevity": 14,
      "skills_and_keywords": 20
    },
    "executive_summary": "The candidate demonstrates solid backend experience...",
    "strengths": [
      "Strong quantified achievements",
      "Clear technical skill categorization",
      "Logical chronological structure"
    ],
    "weaknesses": [
      "Missing professional summary",
      "Some bullets lack measurable outcomes",
      "Skills not categorized by type"
    ],
    "ATS_compatibility_suggestions": {
      "parsing_safety": "Use single-column layout with standard headers...",
      "keyword_optimization_strategy": "Include both acronyms and full forms..."
    },
    "prioritized_action_plan": {
      "P0": "Add a professional summary section",
      "P1": "Rewrite weak bullets with X-Y-Z framework",
      "P2": "Separate skills into categories"
    },
    "bullet_transformations": [
      {
        "original": "Developed internal tools for data processing",
        "critique": "Vague — no specifics about tools, data, or impact",
        "improved": "Engineered internal data processing tools using Python, streamlining daily workflows"
      }
    ],
    "hiring_readiness": "Good",
    "section_analysis": [
      {
        "section": "Experience",
        "present": true,
        "strengths": ["Quantified achievements"],
        "weaknesses": ["Some bullets lack metrics"],
        "recommendations": ["Apply X-Y-Z framework to all bullets"]
      }
    ]
  },
  "improvements": {
    "target_role": "Backend Engineer",
    "improved_summary": "Results-driven Senior Software Engineer with 7+ years...",
    "improved_bullets": [
      {
        "original": "Developed internal tools for data processing",
        "improved": "Engineered internal data processing tools using Python",
        "reason": "Added specificity without inventing metrics"
      }
    ],
    "skills_improvements": {
      "current_skills": ["Python", "FastAPI", "Django", "PostgreSQL"],
      "recommendations": ["Group skills into categories"]
    },
    "ats_keyword_suggestions": {
      "keywords": ["Python", "FastAPI", "REST API", "microservices"],
      "recommendations": ["Include full forms alongside acronyms"]
    }
  }
}
```

---

### Error Responses

| Status Code | Cause                                    | Detail                                                       |
|-------------|------------------------------------------|--------------------------------------------------------------|
| `400`       | Non-PDF file uploaded                    | `"Only PDF files are allowed."`                              |
| `400`       | Empty file                               | `"Uploaded PDF is empty."`                                   |
| `400`       | Invalid PDF (bad magic bytes)            | `"Invalid PDF file."`                                        |
| `400`       | File exceeds 5 MB                        | `"PDF file size must not exceed 5 MB."`                      |
| `400`       | Corrupted/unreadable PDF                 | `"Invalid or corrupted PDF file."`                           |
| `400`       | PDF exceeds 10 pages                     | `"Resume must not exceed 10 pages."`                         |
| `400`       | No extractable text                      | `"Could not extract readable text from the PDF."`            |
| `400`       | Extracted text exceeds 30,000 chars      | `"Resume text exceeds the maximum allowed length of 30,000 characters."` |
| `429`       | Rate limit exceeded (5/min per IP)       | Rate limit exceeded message                                  |
| `429`       | Groq API rate limit                      | `"Groq has rate-limited us"`                                 |
| `500`       | Invalid API credentials                  | `"Our Groq API credentials are invalid"`                     |
| `500`       | API connection failure                   | `"connection error, check internet"`                         |
| `500`       | Other API errors                         | `"AI service is temporarily unavailable. Please try again later."` |

---

## 📊 Scoring System

The resume is scored out of **100 points** across four dimensions:

| Dimension                          | Max Points | What It Evaluates                                             |
|------------------------------------|------------|---------------------------------------------------------------|
| **ATS Compatibility & Structure**  | 25         | Layout, headers, contact info, chronological consistency      |
| **Impact & Outcome Metrics**       | 30         | X-Y-Z framework, quantification, business outcomes            |
| **Language, Tone & Brevity**       | 20         | Action verbs, buzzword avoidance, grammar, conciseness        |
| **Skills Depth & Keywords**        | 25         | Skill categorization, acronym/full-form usage, in-context use |

### Hiring Readiness Levels

| Level                  | Meaning                                           |
|------------------------|---------------------------------------------------|
| **Excellent**          | Ready for top-tier roles immediately               |
| **Good**               | Competitive with minor improvements needed         |
| **Needs Improvement**  | Significant gaps to address before applying         |
| **Not Competitive Yet**| Major restructuring required                       |

---

## 🧪 Testing

The project includes a comprehensive test suite with **58 tests** and **99% code coverage**.

### Test Categories

| File                           | Tests | What It Covers                                  |
|--------------------------------|-------|-------------------------------------------------|
| `test_basic.py`                | 3     | Pytest fundamentals (AAA pattern)                |
| `test_schemas.py`              | 16    | Pydantic schema constraints & enum validation    |
| `test_upload_service.py`       | 9     | All 8 file validation rules + happy path         |
| `test_review_service.py`       | 7     | Review service with mocked LLM + error handling  |
| `test_improvement_service.py`  | 8     | Improvement service with mocked LLM + data flow  |
| `test_api_endpoint.py`         | 9     | Happy path, target_role, flow verification, rate limiting |

> **No real API calls are made during testing.** All LLM interactions are mocked, so tests are fast, free, deterministic, and require no internet access.

### Running Tests

```bash
# Run all tests
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/test_upload_service.py -v

# Run tests matching a keyword
pytest -k "rate_limit" -v
```

### Installing Test Dependencies

```bash
pip install pytest httpx pytest-asyncio pytest-cov
```

---

## 🛠️ Tech Stack

| Component              | Technology                                              |
|------------------------|---------------------------------------------------------|
| **Web Framework**      | [FastAPI](https://fastapi.tiangolo.com/)                |
| **Data Validation**    | [Pydantic](https://docs.pydantic.dev/)                  |
| **LLM Provider**       | [Groq](https://groq.com/) (OpenAI-compatible client)    |
| **LLM Model**          | `openai/gpt-oss-20b`                                    |
| **PDF Processing**     | [PyMuPDF](https://pymupdf.readthedocs.io/)              |
| **Rate Limiting**      | [SlowAPI](https://github.com/laurentS/slowapi)          |
| **ASGI Server**        | [Uvicorn](https://www.uvicorn.org/)                     |
| **Testing**            | pytest, pytest-asyncio, pytest-cov                      |
| **Environment**        | python-dotenv                                           |

---

## ⚙️ Configuration

| Variable       | Description          | Required |
|----------------|----------------------|----------|
| `GROQ_API_KEY` | Your Groq API key    | ✅       |

### Rate Limits

| Endpoint          | Limit          |
|-------------------|----------------|
| `POST /review-resume` | 5 requests/minute per IP |

### File Constraints

| Constraint            | Value         |
|-----------------------|---------------|
| Allowed file type     | PDF only      |
| Max file size         | 5 MB          |
| Max page count        | 10 pages      |
| Max extracted text    | 30,000 chars  |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Before submitting**, make sure all tests pass:
```bash
pytest --cov=app --cov-report=term-missing
```
