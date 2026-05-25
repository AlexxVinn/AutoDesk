# Start Workspace Assistant Python backend (Windows)
$Root = Split-Path -Parent $PSScriptRoot
$env:WORKSPACE_ASSISTANT_CONFIG = Join-Path $Root "config"
Set-Location (Join-Path $Root "backend")
python -m workspace_assistant.main --config $env:WORKSPACE_ASSISTANT_CONFIG
