FROM python:3.11-slim

WORKDIR /app

COPY requirements .

RUN pip install --no-cache-dir -r requirements

COPY . .

# Production FastAPI server
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "3", "-b", "0.0.0.0:8000", "app.main:app"]
