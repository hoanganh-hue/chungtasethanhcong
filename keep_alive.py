#!/usr/bin/env python3
"""
Keep Alive Script for OpenManus-Youtu Integrated Framework
Simple process monitoring and auto-restart
"""

import os
import sys
import time
import subprocess
import signal
import psutil
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keep_alive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KeepAlive:
    """Simple keep alive manager."""
    
    def __init__(self):
        self.processes = {}
        self.running = True
        self.restart_counts = {}
        self.max_restarts = 5
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.stop_all()
        sys.exit(0)
    
    def start_server(self):
        """Start the simple server."""
        try:
            logger.info("Starting simple server...")
            
            process = subprocess.Popen(
                ["python3", "simple_server.py"],
                cwd="/workspace/chungtasethanhcong-github",
                env={**os.environ, "PORT": "8000"},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes["server"] = process
            self.restart_counts["server"] = 0
            
            logger.info(f"Server started with PID {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def start_ngrok(self):
        """Start ngrok tunnel."""
        try:
            logger.info("Starting ngrok tunnel...")
            
            process = subprocess.Popen(
                ["ngrok", "http", "8000"],
                cwd="/workspace/chungtasethanhcong-github",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes["ngrok"] = process
            self.restart_counts["ngrok"] = 0
            
            logger.info(f"ngrok started with PID {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start ngrok: {e}")
            return False
    
    def is_running(self, name):
        """Check if process is running."""
        if name not in self.processes:
            return False
        
        process = self.processes[name]
        return process.poll() is None
    
    def stop_process(self, name):
        """Stop a process."""
        if name not in self.processes:
            return True
        
        try:
            process = self.processes[name]
            process.terminate()
            process.wait(timeout=10)
            del self.processes[name]
            logger.info(f"Process '{name}' stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop process '{name}': {e}")
            return False
    
    def restart_process(self, name):
        """Restart a process."""
        logger.info(f"Restarting process '{name}'...")
        
        self.stop_process(name)
        time.sleep(2)
        
        if name == "server":
            return self.start_server()
        elif name == "ngrok":
            return self.start_ngrok()
        
        return False
    
    def stop_all(self):
        """Stop all processes."""
        logger.info("Stopping all processes...")
        
        for name in list(self.processes.keys()):
            self.stop_process(name)
    
    def monitor(self):
        """Monitor processes and restart if needed."""
        logger.info("Starting process monitoring...")
        
        while self.running:
            try:
                for name in list(self.processes.keys()):
                    if not self.is_running(name):
                        restart_count = self.restart_counts.get(name, 0)
                        
                        if restart_count < self.max_restarts:
                            logger.warning(f"Process '{name}' died, restarting... (attempt {restart_count + 1})")
                            self.restart_counts[name] = restart_count + 1
                            
                            if self.restart_process(name):
                                logger.info(f"Process '{name}' restarted successfully")
                            else:
                                logger.error(f"Failed to restart process '{name}'")
                        else:
                            logger.error(f"Process '{name}' exceeded max restarts")
                            del self.processes[name]
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def status(self):
        """Show status of all processes."""
        print("📊 Keep Alive Status")
        print("=" * 40)
        
        for name in ["server", "ngrok"]:
            if name in self.processes:
                process = self.processes[name]
                is_running = process.poll() is None
                status = "running" if is_running else "stopped"
                pid = process.pid if is_running else "N/A"
                restart_count = self.restart_counts.get(name, 0)
                
                print(f"🔧 {name}:")
                print(f"   Status: {status}")
                print(f"   PID: {pid}")
                print(f"   Restarts: {restart_count}")
            else:
                print(f"🔧 {name}: not_started")
            print()
    
    def run(self):
        """Run the keep alive system."""
        logger.info("Starting Keep Alive System...")
        
        # Start processes
        self.start_server()
        time.sleep(3)
        self.start_ngrok()
        time.sleep(3)
        
        # Show initial status
        self.status()
        
        # Start monitoring
        self.monitor()

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Keep Alive System for OpenManus-Youtu Framework")
    parser.add_argument("command", choices=["start", "stop", "status"], help="Command to execute")
    
    args = parser.parse_args()
    
    ka = KeepAlive()
    
    if args.command == "start":
        ka.run()
    elif args.command == "stop":
        ka.stop_all()
    elif args.command == "status":
        ka.status()

if __name__ == "__main__":
    main()