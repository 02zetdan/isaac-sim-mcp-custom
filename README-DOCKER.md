# Isaac Sim MCP Server - Docker Setup

This guide explains how to run the Isaac Sim MCP Server in a Docker container for **zero local dependencies** and **maximum portability**.

## Prerequisites

- ✅ **Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
- ✅ **Isaac Sim** installed and running with the MCP extension
- ❌ **No need for**: uv, Python, or any other local dependencies!

## Quick Start

### 1. Build the Docker Image

```bash
# Windows
build-docker.bat

# Linux/Mac
docker compose build
```

This creates the `isaac-mcp-server:latest` image with all dependencies bundled.

### 2. Start Isaac Sim with MCP Extension

Make sure Isaac Sim is running and listening on port 8766:

```bash
# Check if Isaac Sim is ready
# Windows PowerShell:
Test-NetConnection localhost -Port 8766

# Linux/Mac:
nc -zv localhost 8766
```

### 3. Configure Cursor/VSCode to Use Docker

#### For Cursor

Edit `%APPDATA%\Cursor\User\settings.json` (or use Cursor Settings UI):

```json
{
  "mcpServers": {
    "isaac-sim": {
      "command": "docker",
      "args": ["compose", "run", "--rm", "isaac-mcp-server"],
      "cwd": "C:\\path\\to\\isaac-sim-mcp"
    }
  }
}
```

**Important:** Replace `C:\\path\\to\\isaac-sim-mcp` with the actual path to this project.

#### For VSCode/Claude Code

The project's `.vscode/settings.json` is already configured:

```json
{
  "claude.mcpServers": {
    "isaac-sim": {
      "command": "docker",
      "args": ["compose", "run", "--rm", "isaac-mcp-server"]
    }
  }
}
```

### 4. Restart Your IDE

- **Cursor**: Completely quit and reopen
- **VSCode**: Reload window (`Ctrl+Shift+P` → "Developer: Reload Window")

### 5. Verify It Works

Open a chat and type `@` - you should see "isaac-sim" in the MCP tools list!

Try calling a tool:
```
get_scene_info()
```

Should return Isaac Sim connection info! 🎉

## How It Works

### Docker Networking (Windows)

On Windows, Docker containers can't use `--network=host` like Linux. Instead, we use **`host.docker.internal`** which Docker Desktop provides to access the host machine's localhost.

The server automatically uses:
- **Local/Linux**: `localhost:8766`
- **Docker (Windows)**: `host.docker.internal:8766`

This is configured via environment variables in `docker-compose.yml`.

### Environment Variables

You can customize the connection:

```yaml
# docker-compose.yml
environment:
  - ISAAC_SIM_HOST=host.docker.internal  # or 'localhost' on Linux
  - ISAAC_SIM_PORT=8766                  # default port
```

## Manual Testing

### Test the Container Directly

```bash
# Start the server manually
docker compose run --rm isaac-mcp-server

# You should see:
# ============================================================
# Isaac Sim MCP Server Starting
# Python version: 3.11.x
# Working directory: /app
# Server file: /app/server.py
# Isaac Sim target: host.docker.internal:8766
# ============================================================
# Connected to Isaac at host.docker.internal:8766
```

Press `Ctrl+C` to stop.

### Test MCP Protocol

Send an MCP initialize request:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | docker compose run --rm isaac-mcp-server
```

Should return a JSON-RPC response with server capabilities!

## Troubleshooting

### Container can't connect to Isaac Sim

**Symptom**: `Failed to connect to Isaac`

**Solutions**:
1. Verify Isaac Sim is running: `Test-NetConnection localhost -Port 8766`
2. Check Isaac Sim logs for: `"Isaac Sim MCP server started on localhost:8766"`
3. On Windows, ensure Docker Desktop is running in **WSL 2 mode** (not Hyper-V)
4. Try updating `ISAAC_SIM_HOST` in `docker-compose.yml`:
   ```yaml
   environment:
     - ISAAC_SIM_HOST=host.docker.internal  # Windows
     # or
     - ISAAC_SIM_HOST=localhost             # Linux
   ```

### "docker: command not found"

**Solution**: Install Docker Desktop from https://docker.com/products/docker-desktop

### Build fails with permission errors

**Solution**: On Linux, you might need to run with sudo or add your user to the docker group:
```bash
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

### MCP tools not showing in Cursor/VSCode

**Solutions**:
1. Verify `cwd` path is correct in MCP configuration (must be absolute path to project)
2. Completely restart the IDE (don't just reload)
3. Check Docker image exists: `docker images | grep isaac-mcp-server`
4. Rebuild image: `build-docker.bat` or `docker compose build --no-cache`

### Slow container startup

This is normal on first run - Docker needs to pull base images. Subsequent runs are much faster due to layer caching.

## Architecture

```
┌─────────────────────┐
│   Cursor/VSCode     │
│                     │
│   MCP Client        │
└──────────┬──────────┘
           │ stdin/stdout (JSON-RPC)
           │
           ▼
┌─────────────────────────────────┐
│   Docker Container              │
│                                 │
│   ┌─────────────────────────┐  │
│   │  Isaac MCP Server       │  │
│   │  (Python + FastMCP)     │  │
│   └────────────┬────────────┘  │
│                │                │
└────────────────┼────────────────┘
                 │ TCP 8766
                 │ via host.docker.internal
                 ▼
┌─────────────────────────────────┐
│   Host Machine                  │
│                                 │
│   Isaac Sim                     │
│   MCP Extension                 │
│   Port: 8766                    │
└─────────────────────────────────┘
```

## Development Workflow

### Code Changes

The `docker-compose.yml` mounts the source code as a volume:

```yaml
volumes:
  - ./isaac_mcp:/app:ro  # Read-only mount
```

This means:
- **No rebuild needed** for code changes in `server.py`
- Changes take effect immediately on next container start
- For dependency changes (pyproject.toml), rebuild: `build-docker.bat`

### Updating Dependencies

1. Edit `isaac_mcp/pyproject.toml`
2. Rebuild: `build-docker.bat`
3. Restart Cursor/VSCode

## Portability Benefits

✅ **Clone and go**: `git clone` + `docker compose up` - that's it!
✅ **Same environment everywhere**: Dev, staging, production all use identical containers
✅ **No conflicts**: Isolated from system Python/packages
✅ **Version controlled**: Dockerfile defines exact environment
✅ **Easy cleanup**: `docker compose down` removes everything

## Production Deployment

For production, consider:

1. **Remove volume mount** in docker-compose.yml (commented by default)
2. **Use specific tags**: `isaac-mcp-server:1.0.0` instead of `:latest`
3. **Health checks**: Add Docker health check for monitoring
4. **Logging**: Configure log aggregation
5. **Registry**: Push to container registry (Docker Hub, ghcr.io, etc.)

## Advanced: Linux with Host Networking

On Linux, you can use host networking for better performance:

```yaml
# docker-compose.yml (Linux only)
services:
  isaac-mcp-server:
    network_mode: host  # Direct access to host network
    environment:
      - ISAAC_SIM_HOST=localhost
      - ISAAC_SIM_PORT=8766
```

This gives the container direct access to host ports without NAT overhead.

## Getting Help

- Check Docker logs: `docker compose logs isaac-mcp-server`
- Verify image: `docker images | grep isaac-mcp`
- Test connection: `run-docker.bat`
- Isaac Sim logs: Check Isaac Sim console for MCP extension status

## Next Steps

- ✅ Set up Isaac Sim MCP extension (see main README.md)
- ✅ Build Docker image: `build-docker.bat`
- ✅ Configure Cursor/VSCode with Docker command
- ✅ Test tools: Try `get_scene_info()`, `create_robot()`, etc.
- 🚀 Build amazing Isaac Sim simulations with AI assistance!
