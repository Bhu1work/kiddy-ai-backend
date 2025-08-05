@echo off
echo Starting Kiddy AI Backend Development Environment...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Start the development service
echo Building and starting development container...
docker-compose up kiddy-ai-dev

echo.
echo Development server started!
echo Open your browser to: http://localhost:8000
echo Health check: http://localhost:8000/health
echo API docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
pause 