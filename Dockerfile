# Multi-stage Docker build for the Bingo Card Generator
# Optimized for AWS free tier deployment

# Build stage
FROM python:3.11-slim as builder

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies with uv (creates virtual environment)
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    # Required for Pillow (image processing)
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy the virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Make sure we use venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY --chown=app:app . .

# Create necessary directories
RUN mkdir -p /app/logs && chown -R app:app /app

# Switch to non-root user
USER app

# Expose port 8080 (AWS App Runner default)
EXPOSE 8080

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_DEBUG=False
ENV PORT=8080
ENV HOST=0.0.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the Flask app
CMD ["python", "app.py"]