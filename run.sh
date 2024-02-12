#!/bin/sh
sleep 10
alembic upgrade head

exec uvicorn --reload --host 0.0.0.0 --port 8002 app.main:app