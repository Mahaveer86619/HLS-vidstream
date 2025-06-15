#!/bin/bash

echo "🚀 Starting startup checks..."

echo "📊 Waiting for PostgreSQL..."
while ! nc -z db 5432; do
    sleep 1
done
echo "✅ PostgreSQL is up and running!"

echo "📝 Waiting for Redis..."
while ! nc -z redis 6379; do
    sleep 1
done
echo "✅ Redis is up and running!"

echo "🌟 Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 7000 --reload
