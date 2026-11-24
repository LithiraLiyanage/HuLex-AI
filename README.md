# HuLex — The Writing Studio

> Your thoughts. Beautifully expressed.

HuLex is an editorial-style writing application built with a Python/FastAPI backend, PostgreSQL, and a trained scikit-learn text classifier. The website combines account sign-in, a writing workspace, a document library, and transparent writing-pattern analysis.

## Interface

A quiet, modern workspace, designed with deliberate typography, botanical greens, and purposeful layouts. Responsive on mobile, tablet, and desktop. Framework-free frontend (HTML/CSS/JavaScript) means no npm install is required for local use.

## Core functions

- Login & registration using the existing JWT API
- Dashboard showing real document counts, word totals, and recent activity
- Writing studio to edit, analyze, polish, save, copy, and export
- Protected writing-pattern classifier at `/api/ml/detect`
- Document library backed by PostgreSQL through your existing FastAPI routes
- Settings and simple writing preferences
- Rewrite API at `/api/rewrite` (offline basic substitutions, or optional API-based model rewriting)

## Local run

In Windows PowerShell:

```powershell
cd C:\Projects\HumanFlow-AI\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Go to `http://127.0.0.1:8000/app` for the website, or `/docs` for API documentation. PostgreSQL must be started; your ML `.joblib` file must be present locally for analysis.

To use model-backed rewriting, set `HULEX_REWRITE_API_KEY` in the private `backend/.env` file and restart the server. Never commit `.env` or the dataset to GitHub.

## ML evaluation notes

The classification baseline was trained on balanced HC3 human/AI answer pairs using TF-IDF features and logistic regression. A group-aware test split minimizes question-pair overlap. Dataset-specific performance is not proof that the detector will generalize to unseen authors, languages, genres, or more recent generation systems. Predictions are **not** authorship evidence or general writing-quality grades. Reporting should include domain-shift tests, false-positive rates, and source/author leakage assessments.

## Development status and limitations

This upgraded frontend is integrated against the known working endpoints; verify API compatibility with the exact state of your local repository. The API-backed rewrite is an optional provider integration, with a light offline fallback; semantic preservation is **not automatically certified**. Full production deployment requires SSL/TLS, security review, robust credential/session management, full API integration testing, rate limiting, and proper persistence for rewritten drafts, style profiles, and feedback.

## Stack

FastAPI · PostgreSQL · SQLAlchemy · Alembic · scikit-learn · HTML/CSS/JavaScript
