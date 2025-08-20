#!/usr/bin/env python3
"""
Keep Alive Script for BABS10 Backend
This script pings the backend every 10 minutes to prevent it from going to sleep
"""

import requests
import time
import datetime

# Configuration
BACKEND_URL = "https://babs10.onrender.com/api/health"
PING_INTERVAL = 600  # 10 minutes in seconds

def ping_backend():
    """Ping the backend to keep it awake"""
    try:
        response = requests.get(BACKEND_URL, timeout=30)
        if response.status_code == 200:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"✅ [{timestamp}] Backend pinged successfully - Status: {response.status_code}")
            return True
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"⚠️  [{timestamp}] Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"❌ [{timestamp}] Failed to ping backend: {str(e)}")
        return False

def main():
    """Main function to keep the backend alive"""
    print("🚀 BABS10 Keep Alive Script Started!")
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print(f"⏰ Ping interval: {PING_INTERVAL} seconds ({PING_INTERVAL/60:.1f} minutes)")
    print("=" * 60)
    
    ping_count = 0
    successful_pings = 0
    
    try:
        while True:
            ping_count += 1
            print(f"\n🔄 Ping #{ping_count}...")
            
            if ping_backend():
                successful_pings += 1
            
            print(f"📊 Stats: {successful_pings}/{ping_count} successful pings")
            print(f"⏳ Waiting {PING_INTERVAL} seconds until next ping...")
            
            # Wait for next ping
            time.sleep(PING_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Keep alive script stopped by user")
        print(f"📊 Final stats: {successful_pings}/{ping_count} successful pings")
        print("💡 Your backend may go to sleep now!")

if __name__ == "__main__":
    main()
