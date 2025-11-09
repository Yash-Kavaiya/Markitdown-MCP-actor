# Use Apify's Python base image
FROM apify/actor-python:3.12

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src ./src

# Install runtime dependencies
# Install uv (for running markitdown-mcp) and project dependencies
RUN pip install --no-cache-dir uv && \
    pip install --no-cache-dir \
    apify>=2.0.0 \
    mcp>=1.3.2 \
    pydantic>=2.10.6 \
    httpx>=0.28.1 \
    uvicorn>=0.34.0 \
    starlette>=0.42.0 \
    'uvloop>=0.21.0; sys_platform != "win32"'

# Set the entry point
CMD ["python", "-m", "src"]
