# Free Resume App

A FastAPI app for browsing ATS-friendly resume templates, improving resume content with AI, and downloading editable DOCX resumes in one click.

## Features

- Browse free ATS-friendly resume templates
- Edit resume details in a guided web form
- Use AI to improve summaries and experience bullets
- Run a free ATS check by uploading PDF/DOCX resumes
- Download editable `.docx` files
- Store templates and drafts locally with SQLite

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000`.

## Environment Variables

- `OPENAI_API_KEY`: API key for AI features
- `OPENAI_BASE_URL`: Optional compatible API base URL
- `OPENAI_MODEL`: Chat model used for ATS rewrite/check features (use a low-cost model like `gpt-4o-mini`)


If no API key is set, AI features return a clear configuration error.
