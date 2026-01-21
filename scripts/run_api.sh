#!/bin/bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
export ENV_FOR_DYNACONF="${ENV_FOR_DYNACONF:-development}"

exec uvicorn ms_invoicer.api:api --reload --app-dir "$APP_DIR"
