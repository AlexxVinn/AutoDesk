# Install backend dependencies on Windows
$Root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $Root "backend")
python -m pip install -e ".[windows]"
