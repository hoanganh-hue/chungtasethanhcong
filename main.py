#!/usr/bin/env python3
"""
Main Application Entry Point for OpenManus-Youtu Integrated Framework
Complete system with Gemini 2.0 Flash integration
"""

import asyncio
import os
import sys
import uvicorn
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def setup_environment():
    """Setup environment variables and configuration."""
    # Set default environment variables
    os.environ.setdefault("GEMINI_API_KEY", "AIzaSyAUnuPqbJfbcnIaTMjQvEXC4pqgoN3H3dU")
    os.environ.setdefault("GEMINI_MODEL", "gemini-2.0-flash")
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8000")
    os.environ.setdefault("DEBUG", "false")
    os.environ.setdefault("LOG_LEVEL", "info")
    
    # Load .env file if exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

def create_app():
    """Create and configure the FastAPI application."""
    try:
        from src.api.server import create_app as create_fastapi_app
        
        app = create_fastapi_app(
            title="OpenManus-Youtu Integrated Framework",
            description="Complete AI Agent System with Gemini 2.0 Flash Integration",
            version="1.0.0",
            debug=os.getenv("DEBUG", "false").lower() == "true"
        )
        
        return app
    except Exception as e:
        print(f"❌ Failed to create FastAPI app: {e}")
        return None

def print_startup_info():
    """Print startup information."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print("🚀 OpenManus-Youtu Integrated Framework")
    print("=" * 50)
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🤖 Gemini API: http://{host}:{port}/api/v1/agents")
    print(f"🔧 Debug Mode: {'ON' if debug else 'OFF'}")
    print(f"🔑 Gemini Model: {os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')}")
    print("=" * 50)

def main():
    """Main application entry point."""
    print("🚀 Starting OpenManus-Youtu Integrated Framework...")
    
    # Setup environment
    setup_environment()
    
    # Create application
    app = create_app()
    if not app:
        print("❌ Failed to create application")
        sys.exit(1)
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    # Print startup info
    print_startup_info()
    
    # Start server
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=log_level,
            access_log=True,
            reload=debug
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()