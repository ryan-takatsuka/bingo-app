# Simple Docker build for the Bingo Card Generator
FROM python:3.12-slim

# Install system dependencies for Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev libpng-dev libfreetype6-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# Install Python dependencies via pip
COPY pyproject.toml ./
RUN pip install --no-cache-dir flask jinja2 pillow click rich questionary loguru

# Copy application code
COPY --chown=app:app . .

USER app

EXPOSE 8080

ENV PYTHONUNBUFFERED=1 FLASK_ENV=production FLASK_DEBUG=False PORT=8080 HOST=0.0.0.0

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "app.py"]
