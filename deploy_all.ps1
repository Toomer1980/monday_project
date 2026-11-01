$ErrorActionPreference = "Stop"
$CoreDir = "C:\Users\toome\Desktop\SovereignCore"
$DataDir = "$CoreDir\data"
$ModuleDir = "$CoreDir\modules"
$LogDir = "$CoreDir\logs"
$ProjectDir = "C:\Users\toome\monday_project"

foreach ($dir in @($CoreDir, $DataDir, $ModuleDir, $LogDir, $ProjectDir)) {
    if (-not (Test-Path $dir)) { New-Item -Path $dir -ItemType Directory -Force | Out-Null }
}

Write-Host "[+] Generating SovereignCore subsystems..." -ForegroundColor Cyan

[System.IO.File]::WriteAllText("$ModuleDir\db.py", "import os, json, sqlite3`nfrom datetime import datetime`nDB_PATH = r\c_path\sovereign_tasks.db".Replace("c_path", $DataDir))

[System.IO.File]::WriteAllText("$ProjectDir\Dockerfile", @"
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git sqlite3 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY . .
RUN mkdir -p /app/data /app/logs /app/config /app/modules
EXPOSE 8000
CMD [\"gunicorn\", \"--bind\", \"0.0.0.0:8000\", \"--workers\", \"1\", \"--threads\", \"4\", \"sovereign_daemon:app\"]
"@)

[System.IO.File]::WriteAllText("$ProjectDir\requirements.txt", "flask==3.0.2`nflask-socketio==5.3.6`nrequests==2.31.0`nrich==13.7.0`npsutil==5.9.8`nstripe==8.11.0`ngunicorn==21.2.0")

[System.IO.File]::WriteAllText("$ProjectDir\render.yaml", @"
services:
  - type: web
    name: sovereigncore-gateway
    env: docker
    plan: free
    autoDeploy: true
    envVars:
      - key: STRIPE_SECRET_KEY
        sync: false
      - key: STRIPE_WEBHOOK_SECRET
        sync: false
"@)

[System.IO.File]::WriteAllText("$ProjectDir\.dockerignore", ".venv`n__pycache__`n*.pyc`n.git`n.gitignore`ndata/*.db`ndata/backups/")

Set-Location $ProjectDir
git add -A
git commit -m "SovereignCore Ultimate Automated Deployment"
git push origin main
Write-Host "[+] All SovereignCore subsystems and cloud assets successfully deployed and pushed!" -ForegroundColor Green
