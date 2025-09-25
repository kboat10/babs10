#!/usr/bin/env python3
"""
Start All Super Aggressive Services for BABS10
This script starts all super aggressive backup and keep-alive services
"""

import subprocess
import time
import os

def start_service(script_name, description):
    """Start a service and return the process info"""
    try:
        print(f"🚀 Starting {description}...")
        process = subprocess.Popen(['python3', script_name], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait a moment to see if it starts successfully
        time.sleep(2)
        
        if process.poll() is None:  # Still running
            print(f"✅ {description} started successfully (PID: {process.pid})")
            return process.pid
        else:
            print(f"❌ {description} failed to start")
            return None
    except Exception as e:
        print(f"❌ Error starting {description}: {e}")
        return None

def main():
    """Start all super aggressive services"""
    print("🚀 BABS10 Super Aggressive Service Manager")
    print("=" * 70)
    print("Starting all SUPER AGGRESSIVE backup and keep-alive services...")
    print("=" * 70)
    
    services = [
        ("keep_alive_super_aggressive.py", "Super Aggressive Keep-Alive Service (2 min intervals)"),
        ("auto_backup_super_aggressive.py", "Super Aggressive Auto-Backup Service (2 min intervals)")
    ]
    
    started_services = []
    
    for script, description in services:
        if os.path.exists(script):
            pid = start_service(script, description)
            if pid:
                started_services.append((description, pid))
        else:
            print(f"⚠️ Script not found: {script}")
    
    print("\n" + "=" * 70)
    print("📊 SUPER AGGRESSIVE SERVICE STATUS SUMMARY")
    print("=" * 70)
    
    if started_services:
        print("✅ Successfully started SUPER AGGRESSIVE services:")
        for description, pid in started_services:
            print(f"   🔧 {description} (PID: {pid})")
        
        print(f"\n💡 Total services running: {len(started_services)}")
        print("💡 Your data is now PROTECTED by SUPER AGGRESSIVE services:")
        print("   🛡️ Keep-alive service (pings every 2 minutes)")
        print("   🔄 Auto-backup service (backups every 2 minutes)")
        print("   📱 Website (accessible at https://babs10.vercel.app/)")
        print("   📡 Backend (running at https://babs10.onrender.com/)")
        print("\n🚨 This should PREVENT Render from sleeping!")
        
    else:
        print("❌ No services were started successfully")
        print("💡 Check the error messages above and try again")
    
    print("\n💡 To check service status, run: python3 backup_status.py")
    print("💡 To create manual backup, run: python3 manual_backup.py")
    print("💡 To start all services again, run: python3 start_super_services.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
