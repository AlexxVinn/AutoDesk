#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export WORKSPACE_ASSISTANT_CONFIG="${ROOT}/config"
cd "${ROOT}/backend"
PYTHONPATH=src python -m workspace_assistant.main --config "${WORKSPACE_ASSISTANT_CONFIG}"
