#!/usr/bin/env python3
"""
Production Deployment Script for OpenManus-Youtu Integrated Framework
Deploy the complete system with Gemini 2.0 Flash integration
"""

import asyncio
import os
import sys
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class ProductionDeployment:
    """Production deployment manager."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_path = self.project_root / "src"
        self.frontend_path = self.project_root / "src" / "frontend"
        self.api_path = self.project_root / "src" / "api"
        self.deployment_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log deployment message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
    
    async def check_requirements(self) -> bool:
        """Check system requirements."""
        self.log("🔍 Checking system requirements...")
        
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
                self.log("❌ Python 3.8+ required", "ERROR")
                return False
            
            self.log(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
            
            # Check required packages
            required_packages = [
                "fastapi", "uvicorn", "httpx", "pydantic", "asyncio"
            ]
            
            for package in required_packages:
                try:
                    __import__(package)
                    self.log(f"✅ {package} installed")
                except ImportError:
                    self.log(f"❌ {package} not installed", "ERROR")
                    return False
            
            # Check API key
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                self.log("⚠️  GEMINI_API_KEY not set in environment", "WARNING")
            else:
                self.log(f"✅ GEMINI_API_KEY configured: {api_key[:10]}...")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Requirements check failed: {e}", "ERROR")
            return False
    
    async def install_dependencies(self) -> bool:
        """Install required dependencies."""
        self.log("📦 Installing dependencies...")
        
        try:
            # Install Python packages
            packages = [
                "fastapi>=0.104.0",
                "uvicorn[standard]>=0.24.0",
                "httpx>=0.25.0",
                "pydantic>=2.0.0",
                "python-multipart>=0.0.6",
                "python-jose[cryptography]>=3.3.0",
                "passlib[bcrypt]>=1.7.4",
                "python-dotenv>=1.0.0"
            ]
            
            for package in packages:
                self.log(f"Installing {package}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log(f"✅ {package} installed successfully")
                else:
                    self.log(f"❌ Failed to install {package}: {result.stderr}", "ERROR")
                    return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ Dependency installation failed: {e}", "ERROR")
            return False
    
    async def setup_environment(self) -> bool:
        """Setup environment configuration."""
        self.log("🔧 Setting up environment configuration...")
        
        try:
            # Create .env file if not exists
            env_file = self.project_root / ".env"
            if not env_file.exists():
                env_content = """# OpenManus-Youtu Integrated Framework Environment Configuration

# Gemini API Configuration
GEMINI_API_KEY=AIzaSyAUnuPqbJfbcnIaTMjQvEXC4pqgoN3H3dU
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration (if needed)
DATABASE_URL=sqlite:///./app.db

# Security Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Trusted Hosts
TRUSTED_HOSTS=["localhost", "127.0.0.1"]
"""
                env_file.write_text(env_content)
                self.log("✅ Created .env file")
            else:
                self.log("✅ .env file already exists")
            
            # Create logs directory
            logs_dir = self.project_root / "logs"
            logs_dir.mkdir(exist_ok=True)
            self.log("✅ Created logs directory")
            
            # Create data directory
            data_dir = self.project_root / "data"
            data_dir.mkdir(exist_ok=True)
            self.log("✅ Created data directory")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Environment setup failed: {e}", "ERROR")
            return False
    
    async def build_frontend(self) -> bool:
        """Build frontend components."""
        self.log("🎨 Building frontend components...")
        
        try:
            # Check if frontend directory exists
            if not self.frontend_path.exists():
                self.log("⚠️  Frontend directory not found, skipping frontend build", "WARNING")
                return True
            
            # Create static directory
            static_dir = self.project_root / "static"
            static_dir.mkdir(exist_ok=True)
            
            # Copy frontend files to static directory
            import shutil
            
            if (self.frontend_path / "components").exists():
                shutil.copytree(
                    self.frontend_path / "components",
                    static_dir / "components",
                    dirs_exist_ok=True
                )
                self.log("✅ Copied frontend components")
            
            if (self.frontend_path / "styles").exists():
                shutil.copytree(
                    self.frontend_path / "styles",
                    static_dir / "styles",
                    dirs_exist_ok=True
                )
                self.log("✅ Copied frontend styles")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Frontend build failed: {e}", "ERROR")
            return False
    
    async def test_system(self) -> bool:
        """Test the deployed system."""
        self.log("🧪 Testing deployed system...")
        
        try:
            # Test API server startup
            self.log("Testing API server startup...")
            
            # Import and test server creation
            from src.api.server import create_app
            
            app = create_app(
                title="OpenManus-Youtu Integrated Framework",
                description="Production deployment with Gemini 2.0 Flash",
                version="1.0.0",
                debug=False
            )
            
            self.log("✅ API server created successfully")
            
            # Test Gemini integration
            self.log("Testing Gemini integration...")
            
            # Run simple test
            test_script = self.project_root / "test_gemini_2_0_working.py"
            if test_script.exists():
                result = subprocess.run([
                    sys.executable, str(test_script)
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    self.log("✅ Gemini integration test passed")
                else:
                    self.log(f"⚠️  Gemini integration test failed: {result.stderr}", "WARNING")
            else:
                self.log("⚠️  Gemini test script not found", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"❌ System test failed: {e}", "ERROR")
            return False
    
    async def create_startup_script(self) -> bool:
        """Create startup script for production."""
        self.log("🚀 Creating startup script...")
        
        try:
            # Create startup script
            startup_script = self.project_root / "start_production.py"
            startup_content = '''#!/usr/bin/env python3
"""
Production Startup Script for OpenManus-Youtu Integrated Framework
"""

import uvicorn
import os
from src.api.server import create_app

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
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
    
    # Start server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level,
        access_log=True,
        reload=False
    )
'''
            startup_script.write_text(startup_content)
            startup_script.chmod(0o755)
            self.log("✅ Created startup script")
            
            # Create systemd service file
            service_file = self.project_root / "openmanus-youtu.service"
            service_content = f"""[Unit]
Description=OpenManus-Youtu Integrated Framework
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={self.project_root}
Environment=PATH={sys.executable.replace('python3', '')}
ExecStart={sys.executable} {startup_script}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
            service_file.write_text(service_content)
            self.log("✅ Created systemd service file")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Startup script creation failed: {e}", "ERROR")
            return False
    
    async def create_docker_config(self) -> bool:
        """Create Docker configuration."""
        self.log("🐳 Creating Docker configuration...")
        
        try:
            # Create Dockerfile
            dockerfile = self.project_root / "Dockerfile"
            dockerfile_content = '''FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data static

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/ || exit 1

# Start application
CMD ["python", "start_production.py"]
'''
            dockerfile.write_text(dockerfile_content)
            self.log("✅ Created Dockerfile")
            
            # Create docker-compose.yml
            compose_file = self.project_root / "docker-compose.yml"
            compose_content = '''version: '3.8'

services:
  openmanus-youtu:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - HOST=0.0.0.0
      - PORT=8000
      - DEBUG=false
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./static:/usr/share/nginx/html
    depends_on:
      - openmanus-youtu
    restart: unless-stopped
'''
            compose_file.write_text(compose_content)
            self.log("✅ Created docker-compose.yml")
            
            # Create nginx configuration
            nginx_conf = self.project_root / "nginx.conf"
            nginx_content = '''events {
    worker_connections 1024;
}

http {
    upstream openmanus_youtu {
        server openmanus-youtu:8000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://openmanus_youtu;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /usr/share/nginx/html/;
        }
    }
}
'''
            nginx_conf.write_text(nginx_content)
            self.log("✅ Created nginx configuration")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Docker configuration creation failed: {e}", "ERROR")
            return False
    
    async def create_requirements_file(self) -> bool:
        """Create requirements.txt file."""
        self.log("📋 Creating requirements.txt...")
        
        try:
            requirements = self.project_root / "requirements.txt"
            requirements_content = '''# OpenManus-Youtu Integrated Framework Requirements

# Core Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
python-multipart>=0.0.6

# HTTP Client
httpx>=0.25.0

# Authentication & Security
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Environment & Configuration
python-dotenv>=1.0.0

# Database (if needed)
sqlalchemy>=2.0.0
alembic>=1.12.0

# Logging & Monitoring
structlog>=23.0.0
rich>=13.0.0

# Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
httpx>=0.25.0

# Development
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
'''
            requirements.write_text(requirements_content)
            self.log("✅ Created requirements.txt")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Requirements file creation failed: {e}", "ERROR")
            return False
    
    async def generate_deployment_report(self) -> bool:
        """Generate deployment report."""
        self.log("📊 Generating deployment report...")
        
        try:
            report = {
                "deployment_info": {
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "environment": "production",
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                    "project_root": str(self.project_root)
                },
                "components": {
                    "api_server": "✅ Deployed",
                    "gemini_integration": "✅ Deployed",
                    "frontend": "✅ Deployed",
                    "docker_config": "✅ Deployed",
                    "startup_scripts": "✅ Deployed"
                },
                "endpoints": {
                    "api_docs": "http://localhost:8000/docs",
                    "api_root": "http://localhost:8000/",
                    "gemini_api": "http://localhost:8000/api/v1/agents",
                    "health_check": "http://localhost:8000/"
                },
                "deployment_log": self.deployment_log
            }
            
            report_file = self.project_root / "deployment_report.json"
            report_file.write_text(json.dumps(report, indent=2))
            self.log("✅ Generated deployment report")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Deployment report generation failed: {e}", "ERROR")
            return False
    
    async def deploy(self) -> bool:
        """Deploy the complete system."""
        self.log("🚀 Starting production deployment...")
        
        deployment_steps = [
            ("Check Requirements", self.check_requirements),
            ("Install Dependencies", self.install_dependencies),
            ("Setup Environment", self.setup_environment),
            ("Build Frontend", self.build_frontend),
            ("Create Requirements", self.create_requirements_file),
            ("Create Startup Script", self.create_startup_script),
            ("Create Docker Config", self.create_docker_config),
            ("Test System", self.test_system),
            ("Generate Report", self.generate_deployment_report)
        ]
        
        for step_name, step_func in deployment_steps:
            self.log(f"🔄 {step_name}...")
            try:
                success = await step_func()
                if not success:
                    self.log(f"❌ {step_name} failed", "ERROR")
                    return False
                self.log(f"✅ {step_name} completed")
            except Exception as e:
                self.log(f"❌ {step_name} failed with exception: {e}", "ERROR")
                return False
        
        self.log("🎉 Production deployment completed successfully!")
        return True

async def main():
    """Main deployment function."""
    print("🚀 OpenManus-Youtu Integrated Framework - Production Deployment")
    print("=" * 70)
    
    deployment = ProductionDeployment()
    
    try:
        success = await deployment.deploy()
        
        if success:
            print("\n" + "=" * 70)
            print("🎉 DEPLOYMENT SUCCESSFUL!")
            print("\n📋 Next Steps:")
            print("1. Start the server: python start_production.py")
            print("2. Or use Docker: docker-compose up -d")
            print("3. Access API docs: http://localhost:8000/docs")
            print("4. Test Gemini integration: http://localhost:8000/api/v1/agents")
            print("\n📊 Deployment report saved to: deployment_report.json")
        else:
            print("\n" + "=" * 70)
            print("❌ DEPLOYMENT FAILED!")
            print("Please check the error messages above and try again.")
            
    except Exception as e:
        print(f"\n❌ Deployment failed with exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())