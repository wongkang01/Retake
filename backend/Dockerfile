# Use a base image with Python
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Install system dependencies
# We include basic tools and then use playwright's own dependency installer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files from backend directory (context is repo root)
COPY backend/pyproject.toml backend/uv.lock backend/README.md ./

# Install dependencies using uv
RUN uv sync --frozen --no-cache --no-install-project

# Install Playwright and its system dependencies
RUN uv run playwright install-deps chromium
RUN uv run playwright install chromium

# Copy the application code from backend directory
COPY backend/app ./app

# Ensure chroma_db directory exists
RUN mkdir -p chroma_db

# Expose the port
EXPOSE 8000

# Command to run the application (shell form for variable expansion)
CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT"]