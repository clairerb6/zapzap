# ZapZap Windows Branch Guide

This branch is focused on running ZapZap on Windows, without full Linux-specific integrations.

## Requirements

- Windows 10/11 (64-bit)
- Python 3.11+ installed and available as `python`

## Build EXE

Run from repository root:

```powershell
.\_scripts\build-windows.ps1 -Clean -OneFile
```

Output:

- `dist\ZapZap.exe`

## Faster Rebuild (skip dependency reinstall)

If `.venv` is already healthy and dependencies are installed:

```powershell
.\_scripts\build-windows.ps1 -OneFile -SkipDeps
```

## Optional Flags

- `-Clean`: remove old `build/`, `dist/`, and generated `.spec`
- `-OneFile`: generate a single executable
- `-Name "CustomName"`: change output executable name

Example:

```powershell
.\_scripts\build-windows.ps1 -Clean -OneFile -Name "ZapZapWin"
```

## Run in development mode (without EXE)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt
python -m zapzap
```

## Troubleshooting

- If build opens Python REPL unexpectedly: ensure you are using the latest `_scripts/build-windows.ps1`.
- If `QtWebEngineCore` fails to load: rebuild using a clean venv:

```powershell
Remove-Item -Recurse -Force .\.venv -ErrorAction SilentlyContinue
.\_scripts\build-windows.ps1 -Clean -OneFile
```

- If PyInstaller fails, inspect:
  - `build\ZapZap\warn-ZapZap.txt`
  - `build\ZapZap\xref-ZapZap.html`
