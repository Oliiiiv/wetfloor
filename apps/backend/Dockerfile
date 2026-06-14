FROM python:3.11-slim

# System dependencies (curl is handy for healthchecks)
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for better Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code (FastAPI app + Phase 0 POC scripts)
COPY app ./app
COPY poc ./poc

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Default: run the FastAPI service. The `backend-poc` service in
# docker-compose.yml overrides this with `python -m poc.connect_ibkr`.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
