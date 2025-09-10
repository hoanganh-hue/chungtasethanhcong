#!/usr/bin/env python3
"""
Production Startup Script for OpenManus-Youtu Integrated Framework
"""

import uvicorn
import os
from src.api.server import create_app

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Create app
    app = create_app(
        title="OpenManus-Youtu Integrated Framework",
        description="Production deployment with Gemini 2.0 Flash",
        version="1.0.0",
        debug=False
    )
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"🚀 Starting OpenManus-Youtu Integrated Framework")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🤖 Gemini API: http://{host}:{port}/api/v1/agents")
    
    # Start server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level,
        access_log=True,
        reload=False
    )
