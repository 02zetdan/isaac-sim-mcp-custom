@echo off
REM Run Isaac Sim MCP Server in Docker (for testing)

echo ==========================================
echo Isaac Sim MCP Server - Docker Test Run
echo ==========================================
echo.
echo Make sure Isaac Sim is running with the MCP extension!
echo Waiting for Isaac Sim on port 8766...
echo.

REM Check if Isaac Sim is running
powershell -Command "Test-NetConnection -ComputerName localhost -Port 8766 -InformationLevel Quiet" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Isaac Sim is not running or not listening on port 8766
    echo.
    echo Please start Isaac Sim with the MCP extension:
    echo   start-isaac-sim.bat
    echo.
    pause
    exit /b 1
)

echo Isaac Sim detected on port 8766
echo.
echo Starting MCP server in Docker...
echo Press Ctrl+C to stop
echo.
echo ==========================================
echo.

REM Run the container interactively
docker compose run --rm isaac-mcp-server
