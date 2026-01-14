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
Write-Host "  Starting SupplyChain Backend Server" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""
Write-Host "Backend Server starting on http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 IMPORTANT - Frontend Server Needed:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Open ANOTHER PowerShell terminal and run:" -ForegroundColor Cyan
Write-Host "   python -m http.server 8001 --directory ." -ForegroundColor Green
Write-Host ""
Write-Host "   Then access the UI at: http://localhost:8001/index.html" -ForegroundColor Green
Write-Host ""
Write-Host "API Documentation available at:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000/docs        (Swagger UI)" -ForegroundColor Green
Write-Host "  http://localhost:8000/redoc       (ReDoc)" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn server:app --host 0.0.0.0 --port 8000
