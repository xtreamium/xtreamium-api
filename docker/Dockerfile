# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies needed for the app
RUN apt-get update && apt-get install -y \
    libxml2 \
    libxslt1.1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache --no-dev

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/ping || exit 1

# Run migrations and start app
CMD ["sh", "-c", "uv run alembic upgrade head && uv run python app/main.py"]
