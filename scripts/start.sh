#!/bin/bash
# OpenManus-Youtu Integrated Framework Startup Script
# Production deployment script

set -e

echo "🚀 Starting OpenManus-Youtu Integrated Framework..."

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "📦 Running in Docker container"
    ENVIRONMENT="production"
else
    echo "🖥️ Running on host system"
    ENVIRONMENT=${ENVIRONMENT:-development}
fi

# Set environment variables
export PYTHONPATH="/app:$PYTHONPATH"
export ENVIRONMENT=$ENVIRONMENT
export LOG_LEVEL=${LOG_LEVEL:-info}

# Create necessary directories
mkdir -p /app/logs /app/data /app/configs

# Check database connection
echo "🔍 Checking database connection..."
python -c "
import asyncio
import asyncpg
import os

async def check_db():
    try:
        conn = await asyncpg.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            user=os.getenv('POSTGRES_USER', 'openmanus'),
            password=os.getenv('POSTGRES_PASSWORD', 'secure_password'),
            database=os.getenv('POSTGRES_DB', 'openmanus_youtu')
        )
        await conn.close()
        print('✅ Database connection successful')
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        exit(1)

asyncio.run(check_db())
"

# Check Redis connection
echo "🔍 Checking Redis connection..."
python -c "
import redis
import os

try:
    r = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=os.getenv('REDIS_PORT', '6379'),
        decode_responses=True
    )
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
    exit(1)
"

# Run database migrations
echo "🔄 Running database migrations..."
python -c "
import asyncio
from alembic.config import Config
from alembic import command

async def run_migrations():
    try:
        alembic_cfg = Config('alembic.ini')
        command.upgrade(alembic_cfg, 'head')
        print('✅ Database migrations completed')
    except Exception as e:
        print(f'❌ Database migrations failed: {e}')
        exit(1)

asyncio.run(run_migrations())
"

# Install Playwright browsers if not already installed
echo "🌐 Installing Playwright browsers..."
playwright install --with-deps

# Start the application
echo "🎯 Starting FastAPI server..."

if [ "$ENVIRONMENT" = "production" ]; then
    echo "🏭 Production mode"
    exec uvicorn src.api.server:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 4 \
        --log-level info \
        --access-log \
        --no-use-colors
else
    echo "🔧 Development mode"
    exec uvicorn src.api.server:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-level debug \
        --access-log \
        --use-colors
fi