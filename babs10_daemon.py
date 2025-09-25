#!/usr/bin/env python3
"""
BABS10 Daemon Service
This runs as a true system daemon, independent of terminals or IDEs
"""

import os
import sys
import time
import signal
import subprocess
import logging
from pathlib import Path

# Setup logging
log_file = "babs10_daemon.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

class BABS10Daemon:
    def __init__(self):
        self.running = True
        self.processes = {}
        self.script_dir = Path(__file__).parent
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        logging.info("🚀 BABS10 Daemon starting...")
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logging.info(f"📡 Received signal {signum}, shutting down...")
        self.running = False
        self.stop_all_services()
        
    def start_service(self, name, script_path):
        """Start a service and track its process"""
        try:
            if name in self.processes and self.processes[name].poll() is None:
                logging.info(f"✅ {name} already running")
                return True
                
            logging.info(f"🔄 Starting {name}...")
            
            # Start the service
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.Popen.DEVNULL,
                stderr=subprocess.Popen.DEVNULL,
                cwd=self.script_dir,
                start_new_session=True  # This makes it truly independent
            )
            
            self.processes[name] = process
            logging.info(f"✅ {name} started with PID {process.pid}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to start {name}: {e}")
            return False
    
    def stop_service(self, name):
        """Stop a specific service"""
        if name in self.processes:
            process = self.processes[name]
            if process.poll() is None:  # Still running
                logging.info(f"🛑 Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    logging.info(f"✅ {name} stopped")
                except subprocess.TimeoutExpired:
                    logging.warning(f"⚠️ {name} didn't stop gracefully, force killing...")
                    process.kill()
            del self.processes[name]
    
    def stop_all_services(self):
        """Stop all running services"""
        logging.info("🛑 Stopping all services...")
        for name in list(self.processes.keys()):
            self.stop_service(name)
    
    def check_services(self):
        """Check if all services are still running"""
        for name, process in list(self.processes.items()):
            if process.poll() is not None:  # Process died
                logging.warning(f"⚠️ {name} died unexpectedly, restarting...")
                del self.processes[name]
                self.start_service(name, self.get_script_path(name))
    
    def get_script_path(self, service_name):
        """Get the script path for a service"""
        script_map = {
            "keep_alive": "keep_alive_ultra_aggressive.py",
            "auto_backup": "auto_backup_super_aggressive.py",
            "auto_restore": "auto_restore_service.py"
        }
        return self.script_dir / script_map.get(service_name, f"{service_name}.py")
    
    def run(self):
        """Main daemon loop"""
        logging.info("🎯 Daemon entering main loop...")
        
        # Start all services
        services = [
            ("keep_alive", "keep_alive_ultra_aggressive.py"),
            ("auto_backup", "auto_backup_super_aggressive.py"),
            ("auto_restore", "auto_restore_service.py")
        ]
        
        for name, script in services:
            self.start_service(name, self.script_dir / script)
        
        # Main monitoring loop
        while self.running:
            try:
                # Check service health every 30 seconds
                self.check_services()
                
                # Log status every 5 minutes
                if int(time.time()) % 300 == 0:
                    active_services = len([p for p in self.processes.values() if p.poll() is None])
                    logging.info(f"📊 Status: {active_services}/{len(services)} services active")
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                logging.info("📡 Keyboard interrupt received")
                break
            except Exception as e:
                logging.error(f"❌ Error in main loop: {e}")
                time.sleep(10)
        
        logging.info("🔄 Daemon shutting down...")
        self.stop_all_services()
        logging.info("✅ Daemon shutdown complete")

def main():
    """Main entry point"""
    daemon = BABS10Daemon()
    daemon.run()

if __name__ == "__main__":
    main()
