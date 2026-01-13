@echo off
REM SupplyChain Planning System - Startup Script for Windows

echo.
echo ========================================
echo  SupplyChain Planning System
echo  Startup Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "myenv" (
    echo Creating virtual environment...
    python -m venv myenv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call myenv\Scripts\activate.bat
echo.

REM Install/update dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
echo Dependencies installed successfully!
echo.

REM Start the server
echo.
echo ========================================
echo  Starting SupplyChain Server
echo ========================================
echo.
echo Server starting on http://localhost:8000
echo.
echo Open your browser to:
echo   http://localhost:8000
echo.
echo API Documentation available at:
echo   http://localhost:8000/docs        (Swagger UI)
echo   http://localhost:8000/redoc       (ReDoc)
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn server:app --host 0.0.0.0 --port 8000
