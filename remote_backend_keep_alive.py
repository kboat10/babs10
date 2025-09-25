#!/usr/bin/env python3
"""
Remote Backend Keep-Alive Service for BABS10
This service keeps the remote backend on Render alive by pinging it every 10 minutes
"""

import requests
import time
import datetime
import signal
import sys
import os
from pathlib import Path

# Configuration
REMOTE_BACKEND_URL = "https://babs10-backend.vercel.app/api"
KEEP_ALIVE_INTERVAL = 600  # 10 minutes (600 seconds)
LOG_FILE = "remote_backend_keep_alive.log"
MAX_RETRIES = 3
RETRY_DELAY = 30  # 30 seconds

def log_message(message):
    """Log message to file and print to console"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    print(log_entry)
    
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry + '\n')
    except Exception as e:
        print(f"Error writing to log: {e}")

def ping_remote_backend():
    """Ping the remote backend to keep it alive"""
    try:
        log_message("🔄 Pinging remote backend to keep it alive...")
        
        response = requests.get(f"{REMOTE_BACKEND_URL}/", timeout=30)
        
        if response.status_code == 200:
            log_message("✅ Remote backend is alive and responding")
            return True
        else:
            log_message(f"⚠️ Remote backend responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        log_message("⏰ Remote backend request timed out")
        return False
    except requests.exceptions.ConnectionError:
        log_message("🔌 Connection error to remote backend")
        return False
    except Exception as e:
        log_message(f"❌ Error pinging remote backend: {e}")
        return False

def wake_up_remote_backend():
    """Try to wake up the remote backend with multiple attempts"""
    log_message("🛏️ Remote backend appears to be sleeping, attempting to wake it up...")
    
    for attempt in range(MAX_RETRIES):
        try:
            log_message(f"🔄 Wake-up attempt {attempt + 1}/{MAX_RETRIES}")
            
            # Try to ping the backend
            response = requests.get(f"{REMOTE_BACKEND_URL}/", timeout=60)
            
            if response.status_code == 200:
                log_message("🎉 Remote backend successfully woken up!")
                return True
            else:
                log_message(f"⚠️ Wake-up attempt {attempt + 1} failed with status: {response.status_code}")
                
        except Exception as e:
            log_message(f"❌ Wake-up attempt {attempt + 1} failed: {e}")
        
        if attempt < MAX_RETRIES - 1:
            log_message(f"⏳ Waiting {RETRY_DELAY} seconds before next attempt...")
            time.sleep(RETRY_DELAY)
    
    log_message("❌ Failed to wake up remote backend after all attempts")
    return False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    log_message("🛑 Shutdown signal received, stopping remote backend keep-alive service...")
    sys.exit(0)

def main():
    """Main keep-alive loop"""
    log_message("🚀 BABS10 Remote Backend Keep-Alive Service Starting...")
    log_message(f"🌐 Remote backend: {REMOTE_BACKEND_URL}")
    log_message(f"⏰ Keep-alive interval: {KEEP_ALIVE_INTERVAL} seconds ({KEEP_ALIVE_INTERVAL/60:.1f} minutes)")
    log_message("💡 This service prevents your Render backend from sleeping")
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    consecutive_failures = 0
    
    try:
        while True:
            # Try to ping the backend
            if ping_remote_backend():
                consecutive_failures = 0
                log_message(f"✅ Backend alive, next ping in {KEEP_ALIVE_INTERVAL/60:.1f} minutes")
            else:
                consecutive_failures += 1
                log_message(f"⚠️ Backend ping failed ({consecutive_failures} consecutive failures)")
                
                # If we have multiple consecutive failures, try to wake it up
                if consecutive_failures >= 2:
                    if wake_up_remote_backend():
                        consecutive_failures = 0
                        log_message("🎉 Backend successfully woken up!")
                    else:
                        log_message("❌ Failed to wake up backend, will retry on next cycle")
            
            # Wait for next ping cycle
            time.sleep(KEEP_ALIVE_INTERVAL)
            
    except KeyboardInterrupt:
        log_message("🛑 Service stopped by user")
    except Exception as e:
        log_message(f"❌ Unexpected error in main loop: {e}")
        raise

if __name__ == "__main__":
    main()
