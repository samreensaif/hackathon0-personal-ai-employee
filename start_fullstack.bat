@echo off
echo ========================================
echo Personal AI Employee - Full Stack Launch
echo ========================================
echo.

echo [1/3] Checking Python dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo FastAPI not found. Installing...
    pip install -r requirements.txt
)

echo [2/3] Starting Backend API...
start "AI Employee API" cmd /k "cd api && python server.py"

timeout /t 3 /nobreak >nul

echo [3/3] Starting Frontend...
cd frontend

if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

if not exist ".env.local" (
    echo Creating environment file...
    copy .env.local.example .env.local
)

start "AI Employee Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo Full Stack Launched Successfully!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend UI:  http://localhost:3000
echo API Docs:     http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul
