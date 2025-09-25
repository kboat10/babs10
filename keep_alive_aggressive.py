#!/usr/bin/env python3
"""
Aggressive Keep Alive Script for BABS10
This script pings more frequently and handles connection issues better
"""

import requests
import time
import datetime
import os
import signal
import sys

# Configuration
BACKEND_URL = "https://babs10.onrender.com/api/health"
PING_INTERVAL = 300  # 5 minutes instead of 10
LOG_FILE = "keep_alive_aggressive.log"
MAX_RETRIES = 3

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
    """Ping the backend with retry logic"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(BACKEND_URL, timeout=15)
            if response.status_code == 200:
                log_message(f"✅ Backend pinged successfully - Status: 200 (Attempt {attempt + 1})")
                return True
            else:
                log_message(f"⚠️  Backend responded with status: {response.status_code} (Attempt {attempt + 1})")
        except requests.exceptions.RequestException as e:
            log_message(f"❌ Failed to ping backend (Attempt {attempt + 1}): {str(e)}")
        
        if attempt < MAX_RETRIES - 1:
            log_message(f"🔄 Retrying in 5 seconds...")
            time.sleep(5)
    
    log_message(f"💀 All {MAX_RETRIES} attempts failed!")
    return False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    log_message("🛑 Shutdown signal received. Stopping aggressive keep-alive script...")
    sys.exit(0)

def main():
    """Main function to keep the backend alive aggressively"""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create log file header
    log_message("🚀 BABS10 AGGRESSIVE Keep Alive Script Started!")
    log_message(f"🔗 Backend URL: {BACKEND_URL}")
    log_message(f"⏰ Ping interval: {PING_INTERVAL} seconds ({PING_INTERVAL/60:.1f} minutes)")
    log_message(f"🔄 Max retries per ping: {MAX_RETRIES}")
    log_message(f"📝 Log file: {LOG_FILE}")
    log_message("=" * 70)
    
    ping_count = 0
    successful_pings = 0
    failed_pings = 0
    
    try:
        while True:
            ping_count += 1
            log_message(f"🔄 Ping #{ping_count}...")
            
            if ping_backend():
                successful_pings += 1
                log_message(f"✅ Ping #{ping_count} successful!")
            else:
                failed_pings += 1
                log_message(f"❌ Ping #{ping_count} failed!")
            
            log_message(f"📊 Stats: {successful_pings}/{ping_count} successful pings ({failed_pings} failed)")
            
            if failed_pings > 0:
                log_message(f"⚠️  WARNING: {failed_pings} failed pings! Backend may be sleeping!")
                log_message(f"🚨 Attempting immediate re-ping...")
                
                # Try to ping again immediately if we failed
                if ping_backend():
                    log_message(f"✅ Recovery ping successful!")
                    failed_pings = max(0, failed_pings - 1)
                else:
                    log_message(f"❌ Recovery ping failed! Backend is definitely sleeping!")
            
            log_message(f"⏳ Waiting {PING_INTERVAL} seconds until next ping...")
            
            # Wait for next ping
            time.sleep(PING_INTERVAL)
            
    except KeyboardInterrupt:
        log_message("🛑 Aggressive keep alive script stopped by user")
        log_message(f"📊 Final stats: {successful_pings}/{ping_count} successful pings ({failed_pings} failed)")
        log_message("💡 Your backend may go to sleep now!")

if __name__ == "__main__":
    main()
