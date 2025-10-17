#!/usr/bin/env bash
set -euo pipefail
( cd services/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 ) &
sleep 1
( cd apps/web && npm i && npm run dev ) &
wait
