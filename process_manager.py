#!/usr/bin/env python3
"""
Process Manager for OpenManus-Youtu Integrated Framework
Python equivalent of PM2 for process management and monitoring
"""

import os
import sys
import time
import signal
import subprocess
import json
import psutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import threading
import logging

class ProcessManager:
    """Process Manager for maintaining stable application state."""
    
    def __init__(self, config_file: str = "process_config.json"):
        self.config_file = config_file
        self.processes: Dict[str, subprocess.Popen] = {}
        self.process_configs: Dict[str, Dict] = {}
        self.monitoring = True
        self.restart_counts: Dict[str, int] = {}
        self.max_restarts = 5
        self.restart_delay = 5
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('process_manager.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.load_config()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self):
        """Load process configuration."""
        default_config = {
            "processes": {
                "ngrok": {
                    "command": ["ngrok", "http", "--url=choice-swine-on.ngrok-free.app", "80"],
                    "cwd": "/workspace/chungtasethanhcong-github",
                    "restart": True,
                    "monitor": True
                },
                "fastapi": {
                    "command": ["python", "start_production_server.py"],
                    "cwd": "/workspace/chungtasethanhcong-github",
                    "restart": True,
                    "monitor": True,
                    "env": {
                        "HOST": "0.0.0.0",
                        "PORT": "80",
                        "DEBUG": "false"
                    }
                }
            },
            "monitoring": {
                "interval": 30,
                "max_restarts": 5,
                "restart_delay": 5
            }
        }
        
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.process_configs = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
                self.process_configs = default_config
        else:
            self.process_configs = default_config
            self.save_config()
    
    def save_config(self):
        """Save process configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.process_configs, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def start_process(self, name: str) -> bool:
        """Start a process."""
        try:
            if name not in self.process_configs["processes"]:
                self.logger.error(f"Process '{name}' not found in configuration")
                return False
            
            config = self.process_configs["processes"][name]
            command = config["command"]
            cwd = config.get("cwd", ".")
            env = os.environ.copy()
            env.update(config.get("env", {}))
            
            self.logger.info(f"Starting process '{name}': {' '.join(command)}")
            
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            self.processes[name] = process
            self.restart_counts[name] = 0
            
            self.logger.info(f"Process '{name}' started with PID {process.pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start process '{name}': {e}")
            return False
    
    def stop_process(self, name: str) -> bool:
        """Stop a process."""
        try:
            if name not in self.processes:
                self.logger.warning(f"Process '{name}' not running")
                return True
            
            process = self.processes[name]
            
            # Try graceful shutdown first
            try:
                process.terminate()
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                self.logger.warning(f"Force killing process '{name}'")
                process.kill()
                process.wait()
            
            del self.processes[name]
            self.logger.info(f"Process '{name}' stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop process '{name}': {e}")
            return False
    
    def restart_process(self, name: str) -> bool:
        """Restart a process."""
        self.logger.info(f"Restarting process '{name}'")
        self.stop_process(name)
        time.sleep(self.restart_delay)
        return self.start_process(name)
    
    def is_process_running(self, name: str) -> bool:
        """Check if a process is running."""
        if name not in self.processes:
            return False
        
        process = self.processes[name]
        return process.poll() is None
    
    def get_process_status(self, name: str) -> Dict:
        """Get process status information."""
        if name not in self.processes:
            return {"status": "not_running", "pid": None}
        
        process = self.processes[name]
        is_running = process.poll() is None
        
        status = {
            "status": "running" if is_running else "stopped",
            "pid": process.pid if is_running else None,
            "restart_count": self.restart_counts.get(name, 0),
            "uptime": time.time() - process._start_time if hasattr(process, '_start_time') else 0
        }
        
        return status
    
    def monitor_processes(self):
        """Monitor all processes and restart if needed."""
        while self.monitoring:
            try:
                for name in list(self.processes.keys()):
                    if not self.is_process_running(name):
                        config = self.process_configs["processes"].get(name, {})
                        
                        if config.get("restart", True):
                            restart_count = self.restart_counts.get(name, 0)
                            
                            if restart_count < self.max_restarts:
                                self.logger.warning(f"Process '{name}' died, restarting... (attempt {restart_count + 1})")
                                self.restart_counts[name] = restart_count + 1
                                
                                if self.start_process(name):
                                    self.logger.info(f"Process '{name}' restarted successfully")
                                else:
                                    self.logger.error(f"Failed to restart process '{name}'")
                            else:
                                self.logger.error(f"Process '{name}' exceeded max restarts, stopping monitoring")
                                del self.processes[name]
                        else:
                            self.logger.info(f"Process '{name}' died and restart disabled")
                            del self.processes[name]
                
                time.sleep(self.process_configs["monitoring"]["interval"])
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def start_all(self):
        """Start all configured processes."""
        self.logger.info("Starting all configured processes...")
        
        for name in self.process_configs["processes"]:
            self.start_process(name)
            time.sleep(2)  # Stagger startup
        
        self.logger.info("All processes started")
    
    def stop_all(self):
        """Stop all processes."""
        self.logger.info("Stopping all processes...")
        
        for name in list(self.processes.keys()):
            self.stop_process(name)
        
        self.logger.info("All processes stopped")
    
    def status(self):
        """Show status of all processes."""
        print("📊 Process Manager Status")
        print("=" * 50)
        
        for name in self.process_configs["processes"]:
            status = self.get_process_status(name)
            print(f"🔧 {name}:")
            print(f"   Status: {status['status']}")
            print(f"   PID: {status['pid'] or 'N/A'}")
            print(f"   Restarts: {status['restart_count']}")
            print(f"   Uptime: {status['uptime']:.1f}s")
            print()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.monitoring = False
        self.stop_all()
        sys.exit(0)
    
    def run(self):
        """Run the process manager."""
        self.logger.info("Starting Process Manager...")
        
        # Start all processes
        self.start_all()
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        monitor_thread.start()
        
        try:
            # Keep main thread alive
            while self.monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        finally:
            self.stop_all()

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process Manager for OpenManus-Youtu Framework")
    parser.add_argument("command", choices=["start", "stop", "restart", "status"], help="Command to execute")
    parser.add_argument("--process", help="Specific process name")
    parser.add_argument("--config", default="process_config.json", help="Configuration file")
    
    args = parser.parse_args()
    
    pm = ProcessManager(args.config)
    
    if args.command == "start":
        if args.process:
            pm.start_process(args.process)
        else:
            pm.run()
    elif args.command == "stop":
        if args.process:
            pm.stop_process(args.process)
        else:
            pm.stop_all()
    elif args.command == "restart":
        if args.process:
            pm.restart_process(args.process)
        else:
            pm.stop_all()
            time.sleep(2)
            pm.start_all()
    elif args.command == "status":
        pm.status()

if __name__ == "__main__":
    main()