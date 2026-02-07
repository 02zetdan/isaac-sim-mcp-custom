@echo off
REM Build Isaac Sim MCP Server Docker Image

echo ==========================================
echo Building Isaac Sim MCP Server Docker Image
echo ==========================================
echo.

REM Build using docker compose
docker compose build

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo Build successful!
    echo ==========================================
    echo.
    echo Image: isaac-mcp-server:latest
    echo.
    echo To run the server:
    echo   docker compose run --rm isaac-mcp-server
    echo.
    echo To test manually:
    echo   run-docker.bat
    echo.
) else (
    echo.
    echo ==========================================
    echo Build failed!
    echo ==========================================
    echo.
    echo Please check the error messages above.
    exit /b 1
)
