#!/usr/bin/env sh

cd dummy/dummy
poetry install
poetry run uvicorn dummy.asgi:app --port 8001 --host 0.0.0.0 --reload
