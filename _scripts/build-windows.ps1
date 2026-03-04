param(
    [switch]$Clean,
    [switch]$OneFile,
    [switch]$SkipDeps,
    [string]$Name = "ZapZap"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
Set-Location $repoRoot

function Require-Command {
    param([string]$CommandName)
    if (-not (Get-Command $CommandName -ErrorAction SilentlyContinue)) {
        throw "Command not found: $CommandName"
    }
}

function Invoke-CheckedCommand {
    param(
        [string]$Exe,
        [string[]]$ArgList,
        [string]$Label
    )

    & $Exe @ArgList
    if ($LASTEXITCODE -ne 0) {
        throw "Failed: $Label (exit code: $LASTEXITCODE)"
    }
}

function Ensure-PipAvailable {
    param([string]$PythonExe)

    & $PythonExe -m pip --version *> $null
    if ($LASTEXITCODE -eq 0) {
        return
    }

    Write-Host "==> pip not available or broken, running ensurepip repair"
    Invoke-CheckedCommand -Exe $PythonExe -ArgList @("-m", "ensurepip", "--upgrade") -Label "ensurepip"
    Invoke-CheckedCommand -Exe $PythonExe -ArgList @("-m", "pip", "--version") -Label "verify pip after ensurepip"
}

Require-Command python

Write-Host "==> Building $Name for Windows"
Write-Host "==> Repository: $repoRoot"

$venvDir = Join-Path $repoRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "==> Creating local virtualenv (.venv)"
    python -m venv $venvDir
}

if (-not (Test-Path $venvPython)) {
    throw "Could not create .venv Python interpreter: $venvPython"
}

$env:PYTHONNOUSERSITE = "1"

Write-Host "==> Using Python: $venvPython"

if ($Clean) {
    Write-Host "==> Cleaning previous build artifacts"
    Remove-Item -Recurse -Force ".\build" -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force ".\dist" -ErrorAction SilentlyContinue
    Remove-Item -Force ".\$Name.spec" -ErrorAction SilentlyContinue
}

if ($SkipDeps) {
    Write-Host "==> Skipping dependency installation (-SkipDeps)"
} else {
    Write-Host "==> Ensuring Python build dependencies"
    Ensure-PipAvailable -PythonExe $venvPython
    Invoke-CheckedCommand -Exe $venvPython -ArgList @("-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel") -Label "upgrade pip/setuptools/wheel"
    Invoke-CheckedCommand -Exe $venvPython -ArgList @("-m", "pip", "install", "--upgrade", "pyinstaller") -Label "install pyinstaller"
    Invoke-CheckedCommand -Exe $venvPython -ArgList @("-m", "pip", "install", "--upgrade", "PyQt6", "PyQt6-WebEngine") -Label "install PyQt6/PyQt6-WebEngine"
    Invoke-CheckedCommand -Exe $venvPython -ArgList @("-m", "pip", "install", "-r", "requirements.txt") -Label "install requirements"
}

Write-Host "==> Validating QtWebEngine availability in current Python"
Invoke-CheckedCommand -Exe $venvPython -ArgList @("-c", "from PyQt6.QtWebEngineCore import QWebEngineProfile; print('QtWebEngine OK')") -Label "validate QtWebEngine import"

$pyiArgs = @(
    "--noconfirm"
    "--clean"
    "--windowed"
    "--name", $Name
    "--collect-submodules", "zapzap"
    "--hidden-import", "PyQt6.QtWebEngineCore"
    "--hidden-import", "PyQt6.QtWebEngineWidgets"
    "--hidden-import", "PyQt6.QtWebEngineQuick"
    "--collect-binaries", "PyQt6"
    "--collect-data", "PyQt6"
    "--collect-all", "PyQt6.QtWebEngineCore"
    "--collect-all", "PyQt6.QtWebEngineWidgets"
    "--collect-all", "PyQt6.QtWebEngineQuick"
    "--add-data", "zapzap\po;zapzap\po"
)

if (Test-Path ".\zapzap\js") {
    $pyiArgs += @("--add-data", "zapzap\js;zapzap\js")
}

if (Test-Path ".\zapzap\extensions") {
    $pyiArgs += @("--add-data", "zapzap\extensions;zapzap\extensions")
}

if ($OneFile) {
    $pyiArgs += "--onefile"
}

$pyiArgs += ".\zapzap\__main__.py"

Write-Host "==> Running PyInstaller"
Invoke-CheckedCommand -Exe $venvPython -ArgList (@("-m", "PyInstaller") + $pyiArgs) -Label "PyInstaller build"

$outputPath = if ($OneFile) {
    Join-Path $repoRoot "dist\$Name.exe"
} else {
    Join-Path $repoRoot "dist\$Name\$Name.exe"
}

Write-Host "==> Build finished"
Write-Host "Output: $outputPath"
