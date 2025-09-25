#!/usr/bin/env python3
"""
Background Keep Alive Script for BABS10
This script runs in the background and keeps your backend awake 24/7
"""

import requests
import time
import datetime
import os
import signal
import sys

# Configuration
BACKEND_URL = "https://babs10.onrender.com/api/health"
PING_INTERVAL = 600  # 10 minutes in seconds
LOG_FILE = "keep_alive.log"

def log_message(message):
    """Log message to file and print to console"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    # Print to console
    print(log_entry)
    
    # Write to log file
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry + '\n')
    except:
        pass

def ping_backend():
    """Ping the backend to keep it awake"""
    try:
        response = requests.get(BACKEND_URL, timeout=30)
        if response.status_code == 200:
            log_message("✅ Backend pinged successfully - Status: 200")
            return True
        else:
            log_message(f"⚠️  Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        log_message(f"❌ Failed to ping backend: {str(e)}")
        return False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    log_message("🛑 Shutdown signal received. Stopping keep-alive script...")
    sys.exit(0)

def main():
    """Main function to keep the backend alive"""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create log file header
    log_message("🚀 BABS10 Background Keep Alive Script Started!")
    log_message(f"🔗 Backend URL: {BACKEND_URL}")
    log_message(f"⏰ Ping interval: {PING_INTERVAL} seconds ({PING_INTERVAL/60:.1f} minutes)")
    log_message(f"📝 Log file: {LOG_FILE}")
    log_message("=" * 60)
    
    ping_count = 0
    successful_pings = 0
    
    try:
        while True:
            ping_count += 1
            log_message(f"🔄 Ping #{ping_count}...")
            
            if ping_backend():
                successful_pings += 1
            
            log_message(f"📊 Stats: {successful_pings}/{ping_count} successful pings")
            log_message(f"⏳ Waiting {PING_INTERVAL} seconds until next ping...")
            
            # Wait for next ping
            time.sleep(PING_INTERVAL)
            
    except KeyboardInterrupt:
        log_message("🛑 Keep alive script stopped by user")
        log_message(f"📊 Final stats: {successful_pings}/{ping_count} successful pings")
        log_message("💡 Your backend may go to sleep now!")

if __name__ == "__main__":
    main()
