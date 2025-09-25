#!/usr/bin/env python3
"""
Ultra Aggressive Keep-Alive for Render Free Tier
This service pings the backend every 2 minutes to prevent sleep
"""

import requests
import time
import datetime
import signal
import sys

# Configuration
BACKEND_URL = "https://babs10.onrender.com/api"
PING_INTERVAL = 120  # 2 minutes
LOG_FILE = "ultra_keep_alive.log"

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

def ping_backend():
    """Ping the backend to keep it awake"""
    try:
        # Ping multiple endpoints to ensure backend stays awake
        endpoints = [
            "/",
            "/health", 
            "/users"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=30)
                if response.status_code == 200:
                    log_message(f"✅ {endpoint}: {response.status_code}")
                else:
                    log_message(f"⚠️ {endpoint}: {response.status_code}")
            except Exception as e:
                log_message(f"❌ {endpoint}: {e}")
            
            time.sleep(1)  # Small delay between pings
        
        return True
        
    except Exception as e:
        log_message(f"❌ Backend ping failed: {e}")
        return False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    log_message("🛑 Shutdown signal received, stopping ultra keep-alive...")
    sys.exit(0)

def main():
    """Main keep-alive loop"""
    log_message("🚀 BABS10 Ultra Keep-Alive Service Starting...")
    log_message(f"🌐 Backend: {BACKEND_URL}")
    log_message(f"⏰ Ping interval: {PING_INTERVAL} seconds ({PING_INTERVAL/60:.1f} minutes)")
    log_message("💡 This prevents Render free tier from sleeping")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    consecutive_failures = 0
    
    try:
        while True:
            if ping_backend():
                consecutive_failures = 0
                log_message(f"✅ Backend alive, next ping in {PING_INTERVAL/60:.1f} minutes")
            else:
                consecutive_failures += 1
                log_message(f"⚠️ Backend ping failed ({consecutive_failures} consecutive failures)")
                
                if consecutive_failures >= 3:
                    log_message("🚨 Multiple consecutive failures - backend may be down")
            
            time.sleep(PING_INTERVAL)
            
    except KeyboardInterrupt:
        log_message("🛑 Service stopped by user")
    except Exception as e:
        log_message(f"❌ Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main()
