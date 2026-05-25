@echo off
REM ================================================================
REM Predictive Maintenance System - Local Development Startup (Windows)
REM ================================================================
REM Usage:
REM   dev.bat          - Start backend + frontend in dev mode
REM   dev.bat seed     - Seed the database with sample data
REM   dev.bat docker   - Start full stack with Docker Compose
REM   dev.bat down     - Stop Docker Compose services
REM ================================================================

set PROJECT_ROOT=%~dp0
set BACKEND_DIR=%PROJECT_ROOT%backend
set FRONTEND_DIR=%PROJECT_ROOT%frontend
set DOCKER_DIR=%PROJECT_ROOT%docker

if "%1"=="seed" goto :seed
if "%1"=="docker" goto :docker
if "%1"=="down" goto :down
goto :dev

:seed
echo [maintainiq] Seeding database with industrial sample data...
cd /d "%BACKEND_DIR%"
python -m app.seed_data
echo [maintainiq] Seed complete.
goto :eof

:docker
echo [maintainiq] Starting full stack with Docker Compose...
cd /d "%DOCKER_DIR%"
docker-compose up --build
goto :eof

:down
echo [maintainiq] Stopping Docker Compose services...
cd /d "%DOCKER_DIR%"
docker-compose down
goto :eof

:dev
echo.
echo   [maintainiq] Starting Predictive Maintenance System in dev mode...
echo.
echo   Backend   = http://localhost:8000
echo   Frontend  = http://localhost:5173
echo   Swagger   = http://localhost:8000/docs
echo.

REM Start backend in a new window
start "MaintainIQ Backend" cmd /k "cd /d "%BACKEND_DIR%" && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Start frontend in a new window
start "MaintainIQ Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev"

echo [maintainiq] Both services started in separate windows.
echo [maintainiq] Close the windows or press Ctrl+C in each to stop.
goto :eof
