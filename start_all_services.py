#!/usr/bin/env python3
"""
Start All Services for BABS10
This script starts all backup and keep-alive services
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
    """Start all services"""
    print("🚀 BABS10 Service Manager")
    print("=" * 60)
    print("Starting all backup and keep-alive services...")
    print("=" * 60)
    
    services = [
        ("keep_alive_aggressive.py", "Keep-Alive Service"),
        ("auto_backup_service.py", "Auto-Backup Service")
    ]
    
    started_services = []
    
    for script, description in services:
        if os.path.exists(script):
            pid = start_service(script, description)
            if pid:
                started_services.append((description, pid))
        else:
            print(f"⚠️ Script not found: {script}")
    
    print("\n" + "=" * 60)
    print("📊 SERVICE STATUS SUMMARY")
    print("=" * 60)
    
    if started_services:
        print("✅ Successfully started services:")
        for description, pid in started_services:
            print(f"   🔧 {description} (PID: {pid})")
        
        print(f"\n💡 Total services running: {len(started_services)}")
        print("💡 Your data is now protected by:")
        print("   🛡️ Keep-alive service (prevents backend sleep)")
        print("   🔄 Auto-backup service (creates backups every 5 minutes)")
        print("   📱 Website (accessible at https://babs10.vercel.app/)")
        print("   📡 Backend (running at https://babs10.onrender.com/)")
        
    else:
        print("❌ No services were started successfully")
        print("💡 Check the error messages above and try again")
    
    print("\n💡 To check service status, run: python3 backup_status.py")
    print("💡 To create manual backup, run: python3 manual_backup.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
