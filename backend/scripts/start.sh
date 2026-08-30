#!/usr/bin/env sh
# Container entrypoint: apply migrations, then serve.
# Safe for a single Render instance. If we scale to multiple instances, move the
# migration step to a Render "release command" (or a render.yaml preDeploy) instead.
set -e

alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-10000}"
