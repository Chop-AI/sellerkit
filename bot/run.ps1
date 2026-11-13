$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path .venv)) { python -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install -q -r requirements.txt
if (-not (Test-Path .env)) {
  Copy-Item .env.example .env
  Write-Host "Created .env — insert BOT_TOKEN from @BotFather, then re-run."
  exit 1
}
& .\.venv\Scripts\python.exe bot.py
