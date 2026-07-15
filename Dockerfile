FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# app.py resolves FRONTEND as ../frontend, so keep both dirs side by side.
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# backend uses flat imports (from store import Store) — run from inside it.
WORKDIR /app/backend

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
