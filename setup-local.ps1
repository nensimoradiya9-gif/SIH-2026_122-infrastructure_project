$ErrorActionPreference = 'Stop'
Write-Host "Infra-Pulse local SQLite setup" -ForegroundColor Cyan
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw "Node.js is not installed. Install Node.js 18+ first." }
Set-Location $PSScriptRoot
Write-Host "Installing Node dependencies..." -ForegroundColor Cyan
npm install
Write-Host "Starting Infra-Pulse..." -ForegroundColor Green
npm start
