#!/usr/bin/env pwsh

Write-Host "Starting Kiddy AI Backend Development Environment..." -ForegroundColor Green
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host ".env file not found. Running setup..." -ForegroundColor Yellow
    python setup_env.py
}

# Start the development service
Write-Host "Building and starting development container..." -ForegroundColor Cyan
Write-Host ""

try {
    docker-compose up kiddy-ai-dev
} catch {
    Write-Host "Failed to start development environment" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Development server started!" -ForegroundColor Green
Write-Host "Open your browser to: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Health check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "API docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow 