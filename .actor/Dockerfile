# First stage: Build stage with all build dependencies
FROM apify/actor-python:3.12 AS builder

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY pyproject.toml poetry.lock* ./

# Install dependencies using Poetry
RUN poetry install --only main --no-root --no-interaction --no-ansi

# Second stage: Runtime stage with minimal dependencies
FROM apify/actor-python:3.12

# Install runtime dependencies (uv for running markitdown-mcp)
RUN pip install --no-cache-dir uv

# Copy virtual environment from builder
COPY --from=builder /usr/local /usr/local

# Copy source code
COPY src ./src
COPY pyproject.toml README.md ./

# Set the entry point
CMD ["python", "-m", "src"]
