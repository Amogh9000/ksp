FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system deps needed by asyncpg / psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source
COPY app ./app

EXPOSE 9000

CMD ["sh", "-c", "python3 -m uvicorn app.main:app --host 0.0.0.0 --port ${X_ZOHO_CATALYST_LISTEN_PORT:-9000}"]
