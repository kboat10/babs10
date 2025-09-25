#!/usr/bin/env python3
"""
Super Aggressive Keep Alive Script for BABS10
This script pings every 2 minutes to prevent Render from sleeping
"""

import requests
import time
import datetime
import os
import signal
import sys

# Configuration
BACKEND_URL = "https://babs10.onrender.com/api/health"
PING_INTERVAL = 120  # 2 minutes instead of 5
LOG_FILE = "keep_alive_super_aggressive.log"
MAX_RETRIES = 5
RETRY_DELAY = 3

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
    except Exception as e:
        print(f"Error writing to log: {e}")

def ping_backend():
    """Ping the backend with retry logic"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log_message(f"🔄 Ping attempt {attempt}/{MAX_RETRIES}...")
            
            response = requests.get(BACKEND_URL, timeout=10)
            
            if response.status_code == 200:
                log_message(f"✅ Backend pinged successfully - Status: {response.status_code}")
                return True
            else:
                log_message(f"❌ Backend responded with status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            log_message(f"⏰ Timeout on attempt {attempt}")
        except requests.exceptions.ConnectionError as e:
            log_message(f"🔌 Connection error on attempt {attempt}: {e}")
        except Exception as e:
            log_message(f"❌ Unexpected error on attempt {attempt}: {e}")
        
        # Wait before retry (except on last attempt)
        if attempt < MAX_RETRIES:
            log_message(f"🔄 Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
    
    log_message(f"❌ All {MAX_RETRIES} attempts failed")
    return False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    log_message("🛑 Shutdown signal received, stopping keep-alive service...")
    sys.exit(0)

def main():
    """Main keep-alive loop"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    log_message("🚀 BABS10 Super Aggressive Keep-Alive Service Started")
    log_message("=" * 70)
    log_message(f"🔗 Backend URL: {BACKEND_URL}")
    log_message(f"⏰ Ping interval: {PING_INTERVAL} seconds ({PING_INTERVAL/60:.1f} minutes)")
    log_message(f"📝 Log file: {LOG_FILE}")
    log_message(f"🔄 Max retries: {MAX_RETRIES}")
    log_message(f"⏳ Retry delay: {RETRY_DELAY} seconds")
    log_message("=" * 70)
    
    # Initial ping
    log_message("🔄 Initial ping to wake up backend...")
    if ping_backend():
        log_message("✅ Initial ping successful!")
    else:
        log_message("⚠️ Initial ping failed, but continuing...")
    
    # Main ping loop
    ping_count = 1
    successful_pings = 0
    failed_pings = 0
    
    while True:
        try:
            log_message(f"⏳ Waiting {PING_INTERVAL} seconds until next ping...")
            time.sleep(PING_INTERVAL)
            
            ping_count += 1
            log_message(f"🔄 Ping #{ping_count}...")
            
            if ping_backend():
                successful_pings += 1
                log_message(f"✅ Ping #{ping_count} successful!")
            else:
                failed_pings += 1
                log_message(f"❌ Ping #{ping_count} failed!")
            
            # Log statistics
            total_pings = successful_pings + failed_pings
            success_rate = (successful_pings / total_pings * 100) if total_pings > 0 else 0
            log_message(f"📊 Stats: {successful_pings}/{total_pings} successful pings ({success_rate:.1f}% success rate)")
            
        except KeyboardInterrupt:
            log_message("🛑 Manual stop requested")
            break
        except Exception as e:
            log_message(f"❌ Unexpected error in ping loop: {e}")
            time.sleep(30)  # Wait 30 seconds before retrying
    
    log_message("🛑 Keep-alive service stopped")

if __name__ == "__main__":
    main()
