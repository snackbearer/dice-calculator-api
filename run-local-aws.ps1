param(
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$StartServer
)

$ErrorActionPreference = "Stop"

Write-Host "== DiceCalculatorFastAPI local AWS startup ==" -ForegroundColor Cyan

if (-not (Test-Path ".\.env")) {
    throw "Missing .env file in repo root."
}

# Load .env values for preflight checks
Get-Content .\.env |
    Where-Object { $_ -match "^\s*[^#].+=.*$" } |
    ForEach-Object {
        $parts = $_ -split "=", 2
        if ($parts.Count -eq 2) {
            [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
        }
    }

if ($env:DATABASE_MODE -ne "aws") {
    Write-Warning "DATABASE_MODE is '$($env:DATABASE_MODE)'. Expected 'aws' for this script."
}

$required = @("AWS_REGION", "AWS_DB_HOST", "AWS_DB_PORT", "AWS_DB_NAME", "AWS_DB_USER")
$missing = $required | Where-Object { [string]::IsNullOrWhiteSpace((Get-Item "Env:$_" -ErrorAction SilentlyContinue).Value) }
if ($missing.Count -gt 0) {
    throw "Missing required .env values: $($missing -join ', ')"
}

Write-Host "Checking AWS credentials with STS..." -ForegroundColor Yellow
aws sts get-caller-identity | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "AWS credentials are not working in this shell."
}
Write-Host "AWS identity OK" -ForegroundColor Green

Write-Host "Checking TCP connectivity to RDS endpoint..." -ForegroundColor Yellow
$net = Test-NetConnection -ComputerName $env:AWS_DB_HOST -Port ([int]$env:AWS_DB_PORT) -WarningAction SilentlyContinue
if (-not $net.TcpTestSucceeded) {
    throw "Cannot reach $($env:AWS_DB_HOST):$($env:AWS_DB_PORT). Check VPN/SG/NACL/routing."
}
Write-Host "RDS network path OK" -ForegroundColor Green

if ($StartServer) {
    Write-Host "Starting FastAPI on http://${BindHost}:$Port" -ForegroundColor Cyan
    $venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        & $venvPython -m uvicorn app.main:app --reload --host $BindHost --port $Port --env-file .env
    }
    else {
        uvicorn app.main:app --reload --host $BindHost --port $Port --env-file .env
    }
}
else {
    Write-Host "Preflight checks passed." -ForegroundColor Green
    Write-Host "Run with -StartServer to launch FastAPI." -ForegroundColor Green
}
