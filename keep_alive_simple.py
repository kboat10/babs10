#!/usr/bin/env python3
"""
Super Simple Keep Alive Script for BABS10
Just run this and your backend will never go to sleep!
"""

import requests
import time

print("🚀 Starting BABS10 Keep Alive...")
print("✅ This will keep your app working for your auntie!")
print("⏰ Pinging every 10 minutes...")
print("=" * 50)

while True:
    try:
        # Ping the backend
        response = requests.get("https://babs10.onrender.com/api/health")
        print(f"✅ Backend is awake! ({time.strftime('%H:%M:%S')})")
        
        # Wait 10 minutes
        print("😴 Sleeping for 10 minutes...")
        time.sleep(600)  # 10 minutes
        
    except:
        print(f"❌ Backend might be sleeping... ({time.strftime('%H:%M:%S')})")
        time.sleep(60)  # Wait 1 minute and try again
