FROM python:3.12-slim

# Don't buffer stdout/stderr; no .pyc files in the image.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x scripts/start.sh

# Run as a non-root user.
RUN useradd --create-home --uid 1000 appuser
USER appuser

# Applies migrations, then starts uvicorn on $PORT (Render injects it; default 10000).
CMD ["sh", "scripts/start.sh"]
