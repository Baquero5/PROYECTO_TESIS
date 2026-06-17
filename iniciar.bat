@echo off
echo ========================================
echo   Iniciando Sistema de Prediccion
echo ========================================
echo.

:: Backend
start "Backend" cmd /k "cd /d D:\visual\TESIS\backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

:: Frontend
start "Frontend" cmd /k "cd /d D:\visual\TESIS\frontend && npm run dev"

echo.
echo ========================================
echo   URLs del Sistema
echo ========================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   Docs:     http://localhost:8000/docs
echo ========================================
echo.
pause
