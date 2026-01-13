# SupplyChain Planning System - Startup Script for PowerShell

Write-Host ""
Write-Host "========================================"
Write-Host "  SupplyChain Planning System"
Write-Host "  Startup Script"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "myenv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv myenv
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "myenv\Scripts\Activate.ps1"
Write-Host ""

# Install/update dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
Write-Host "Dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

# Start the server
Write-Host ""
Write-Host "========================================"
Write-Host "  Starting SupplyChain Server" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""
Write-Host "Server starting on http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Open your browser to:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "API Documentation available at:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000/docs        (Swagger UI)" -ForegroundColor Green
Write-Host "  http://localhost:8000/redoc       (ReDoc)" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python server.py
