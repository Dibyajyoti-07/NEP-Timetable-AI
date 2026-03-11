# PowerShell script to start the AI Timetable Backend
Write-Host "Starting AI Timetable Backend..." -ForegroundColor Green

# Ensure Node.js and npm are on the PATH (refreshes from registry)
$regUserPath = [Environment]::GetEnvironmentVariable('Path','User')
$regMachinePath = [Environment]::GetEnvironmentVariable('Path','Machine')
$env:Path = "$regMachinePath;$regUserPath"

Set-Location backend
Write-Host "📁 Changed to backend directory" -ForegroundColor Yellow

# Activate virtual environment
if (Test-Path "activate.ps1") {
    Write-Host "🔧 Activating Python environment..." -ForegroundColor Cyan
    .\activate.ps1
}

Write-Host "🌐 Starting FastAPI server..." -ForegroundColor Green
Write-Host "📊 API Documentation will be available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🔗 API will be running at: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

# Start the server
& "venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
