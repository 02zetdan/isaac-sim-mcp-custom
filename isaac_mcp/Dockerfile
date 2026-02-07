# Isaac Sim MCP Server Dockerfile
# Simple, straightforward build

FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    mkdir -p /app && \
    chown -R mcpuser:mcpuser /app

WORKDIR /app

# Copy application code
COPY --chown=mcpuser:mcpuser . .

# Install dependencies directly using pip
RUN pip install --no-cache-dir "mcp[cli]>=1.0.0"

# Switch to non-root user
USER mcpuser

# Set Python to unbuffered mode for immediate log output
ENV PYTHONUNBUFFERED=1

# Default environment variables (can be overridden)
ENV ISAAC_SIM_HOST=host.docker.internal
ENV ISAAC_SIM_PORT=8766

# The MCP server communicates via stdin/stdout (JSON-RPC)
ENTRYPOINT ["python", "server.py"]
