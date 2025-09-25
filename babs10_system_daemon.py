#!/usr/bin/env python3
"""
BABS10 True System Daemon
This runs completely independently of any user session, IDE, or terminal
"""

import os
import sys
import time
import signal
import subprocess
import logging
import atexit
from pathlib import Path
import daemon
import daemon.pidfile

# Setup logging
log_file = "babs10_system_daemon.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

class BABS10SystemDaemon:
    def __init__(self):
        self.running = True
        self.processes = {}
        self.script_dir = Path(__file__).parent
        self.pid_file = self.script_dir / "babs10_daemon.pid"
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        logging.info("🚀 BABS10 System Daemon initializing...")
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logging.info(f"📡 Received signal {signum}, shutting down gracefully...")
        self.running = False
        self.stop_all_services()
        
    def start_service(self, name, script_path):
        """Start a service with complete isolation"""
        try:
            if name in self.processes and self.processes[name].poll() is None:
                logging.info(f"✅ {name} already running")
                return True
                
            logging.info(f"🔄 Starting {name}...")
            
            # Start the service with complete isolation
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.Popen.DEVNULL,
                stderr=subprocess.Popen.DEVNULL,
                cwd=self.script_dir,
                start_new_session=True,  # New session
                preexec_fn=os.setsid,    # New process group
                close_fds=True           # Close all file descriptors
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
                try:
                    # Try graceful shutdown
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    process.wait(timeout=10)
                    logging.info(f"✅ {name} stopped gracefully")
                except (subprocess.TimeoutExpired, ProcessLookupError):
                    logging.warning(f"⚠️ {name} didn't stop gracefully, force killing...")
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            del self.processes[name]
    
    def stop_all_services(self):
        """Stop all running services"""
        logging.info("🛑 Stopping all services...")
        for name in list(self.processes.keys()):
            self.stop_service(name)
    
    def check_services(self):
        """Check if all services are still running and restart if needed"""
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
    
    def run_daemon(self):
        """Run as a true system daemon"""
        logging.info("🎯 Entering daemon mode...")
        
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
                
            except Exception as e:
                logging.error(f"❌ Error in main loop: {e}")
                time.sleep(10)
        
        logging.info("🔄 Daemon shutting down...")
        self.stop_all_services()
        logging.info("✅ Daemon shutdown complete")
    
    def run(self):
        """Main entry point with daemon context"""
        # Create daemon context
        context = daemon.DaemonContext(
            working_directory=self.script_dir,
            umask=0o002,
            pidfile=daemon.pidfile.PIDLockFile(str(self.pid_file)),
            files_preserve=[logging.getLogger().handlers[0].stream],
            signal_map={
                signal.SIGTERM: self.signal_handler,
                signal.SIGINT: self.signal_handler,
            }
        )
        
        with context:
            self.run_daemon()

def main():
    """Main entry point"""
    daemon = BABS10SystemDaemon()
    daemon.run()

if __name__ == "__main__":
    main()
