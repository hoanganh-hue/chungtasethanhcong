#!/usr/bin/env python3
"""
Production Server Startup Script for OpenManus-Youtu Integrated Framework
Includes Telegram Bot, Web Interface, and ngrok integration
"""

import asyncio
import os
import sys
import subprocess
import time
import signal
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def setup_environment():
    """Setup environment variables."""
    # Load .env file
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    # Set defaults
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "80")
    os.environ.setdefault("DEBUG", "false")
    os.environ.setdefault("LOG_LEVEL", "info")

def start_ngrok():
    """Start ngrok tunnel."""
    try:
        print("🌐 Starting ngrok tunnel...")
        
        # Start ngrok in background
        ngrok_process = subprocess.Popen([
            "ngrok", "http", 
            "--url=choice-swine-on.ngrok-free.app", 
            "80"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for ngrok to start
        time.sleep(3)
        
        print("✅ ngrok tunnel started successfully")
        print("🔗 Public URL: https://choice-swine-on.ngrok-free.app")
        
        return ngrok_process
        
    except Exception as e:
        print(f"❌ Failed to start ngrok: {e}")
        return None

def start_fastapi_server():
    """Start FastAPI server."""
    try:
        print("🚀 Starting FastAPI server...")
        
        # Import and create app
        from src.api.server import create_app
        
        app = create_app(
            title="OpenManus-Youtu Integrated Framework",
            description="Complete AI Agent System with Telegram Bot Integration",
            version="1.0.0",
            debug=False
        )
        
        # Start server
        import uvicorn
        
        uvicorn.run(
            app,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "80")),
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            access_log=True,
            workers=1
        )
        
    except Exception as e:
        print(f"❌ Failed to start FastAPI server: {e}")
        raise

def print_startup_info():
    """Print startup information."""
    print("🎉 OpenManus-Youtu Integrated Framework - Production Server")
    print("=" * 60)
    print(f"🌐 Server: http://{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '80')}")
    print(f"🔗 Public URL: https://choice-swine-on.ngrok-free.app")
    print(f"📚 API Docs: https://choice-swine-on.ngrok-free.app/docs")
    print(f"🤖 Telegram Bot: Active with webhook")
    print(f"🧠 Gemini AI: {os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')}")
    print(f"🔧 Environment: Production")
    print("=" * 60)

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print("\n🛑 Shutting down production server...")
    sys.exit(0)

def main():
    """Main function."""
    print("🚀 Starting OpenManus-Youtu Integrated Framework Production Server...")
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Setup environment
    setup_environment()
    
    # Print startup info
    print_startup_info()
    
    # Start ngrok tunnel
    ngrok_process = start_ngrok()
    if not ngrok_process:
        print("❌ Cannot start without ngrok tunnel")
        sys.exit(1)
    
    try:
        # Start FastAPI server
        start_fastapi_server()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        # Cleanup
        if ngrok_process:
            ngrok_process.terminate()
            print("🔌 ngrok tunnel stopped")

if __name__ == "__main__":
    main()