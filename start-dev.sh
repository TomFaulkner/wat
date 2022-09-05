#!/bin/bash
poetry run uvicorn wat.asgi:app --reload --port 8000 --host 0.0.0.0
