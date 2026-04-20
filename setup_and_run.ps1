# Attendance Management System - Centralized Setup and Launcher

# ── 1. Determine Root Directory Robustly ──
# $PSScriptRoot ensures we always point to the script's location, even if run from subfolders
$ROOT_DIR = $PSScriptRoot
if (-not $ROOT_DIR) { $ROOT_DIR = Get-Location } # Fallback

$BACKEND_DIR = Join-Path $ROOT_DIR "backend"
$FRONTEND_DIR = Join-Path $ROOT_DIR "frontend"

Set-Location $ROOT_DIR

try {
    Write-Host "`n[1/4] Configuring Backend Environment..." -ForegroundColor Cyan
    Set-Location $BACKEND_DIR

    # 1. Create venv if not exists
    if (-not (Test-Path "venv")) {
        Write-Host "Creating Python Virtual Environment (using Python 3.12)..." -ForegroundColor Yellow
        py -3.12 -m venv venv
    }

    # 2. Verify Venv Health (Fixes "Fatal error in launcher" if folder was moved)
    # If pip fails to run, we recreate the venv to fix internal paths
    $pipPath = ".\venv\Scripts\pip.exe"
    try {
        & $pipPath --version | Out-Null
    } catch {
        Write-Host "Virtual Environment path is broken. Repairing..." -ForegroundColor Red
        Remove-Item -Recurse -Force "venv"
        py -3.12 -m venv venv
    }

    Write-Host "Installing Python Dependencies..." -ForegroundColor Yellow
    & $pipPath install -r requirements.txt

    Write-Host "`n[2/4] Initializing Database..." -ForegroundColor Cyan
    $pythonPath = $pipPath.Replace("pip.exe", "python.exe")
    & $pythonPath scripts\init_db.py

    Write-Host "`n[3/4] Configuring Frontend Environment..." -ForegroundColor Cyan
    Set-Location $FRONTEND_DIR

    # 3. NPM Install - Only run if node_modules is missing for speed
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing Node Modules (This may take a minute)..." -ForegroundColor Yellow
        npm install
    } else {
        Write-Host "Node Modules already installed. Skipping..." -ForegroundColor Gray
        # Optional: npm install --prefer-offline 
    }

    Write-Host "`n[4/4] Launching Application..." -ForegroundColor Green
    Write-Host "Starting System..." -ForegroundColor Green

    # 4. Start the Application
    npm start

} finally {
    # ── 3. Always Return to Root ──
    # This ensures even if the app stays in 'frontend', the next terminal command starts at root
    Write-Host "`n[4/4] Returning to Root Directory." -ForegroundColor Gray
    Set-Location $ROOT_DIR
}
