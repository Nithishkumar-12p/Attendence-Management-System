# Build Script for Attendance Management System
# This script bundles the Python backend and Electron frontend into a single desktop application.

$ROOT_DIR = $PSScriptRoot
$BACKEND_DIR = Join-Path $ROOT_DIR "backend"
$FRONTEND_DIR = Join-Path $ROOT_DIR "frontend"

Write-Host "`n[1/4] Building Backend Executable..." -ForegroundColor Cyan
Set-Location $BACKEND_DIR

# Ensure venv exists and has dependencies
if (-not (Test-Path "venv")) {
    Write-Host "Creating Virtual Environment..." -ForegroundColor Yellow
    py -3.12 -m venv venv
}

$pipPath = Join-Path $BACKEND_DIR "venv\Scripts\pip.exe"
$pythonPath = Join-Path $BACKEND_DIR "venv\Scripts\python.exe"

Write-Host "Installing PyInstaller and dependencies..." -ForegroundColor Yellow
& $pipPath install -r requirements.txt
& $pipPath install pyinstaller

Write-Host "Running PyInstaller..." -ForegroundColor Yellow
# We run from root so 'backend.app' imports work correctly
Set-Location $ROOT_DIR
& $pythonPath -m PyInstaller --onefile --name backend --distpath backend/dist --workpath backend/build --specpath backend backend/app.py

Write-Host "`n[2/4] Building Frontend Desktop App..." -ForegroundColor Cyan
Set-Location $FRONTEND_DIR

Write-Host "Installing Node dependencies..." -ForegroundColor Yellow
npm install

Write-Host "Running Electron Builder..." -ForegroundColor Yellow
npm run build

Write-Host "`n[3/4] Cleaning up..." -ForegroundColor Cyan
Set-Location $ROOT_DIR

Write-Host "`n[SUCCESS] Build Complete!" -ForegroundColor Green
Write-Host "Your portable desktop application is located in: " -ForegroundColor White
Write-Host "$FRONTEND_DIR\dist\" -ForegroundColor Yellow
