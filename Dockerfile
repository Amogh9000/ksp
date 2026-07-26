FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY query ./query
COPY track1_dataset.json ./
COPY lid.176.ftz ./

EXPOSE 9000

CMD ["sh", "-c", "python3 -m uvicorn query.api:app --host 0.0.0.0 --port ${X_ZOHO_CATALYST_LISTEN_PORT:-9000}"]
