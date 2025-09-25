#!/usr/bin/env python3
"""
BABS10 Status Checker
Check the status of all running services
"""

import os
import subprocess
import json
from datetime import datetime

def check_service_status():
    """Check the status of all BABS10 services"""
    print("🔍 BABS10 Service Status Check")
    print("=" * 40)
    
    # Check if PID files exist
    pid_files = {
        "Keep-Alive": ".keep_alive.pid",
        "Auto-Backup": ".backup.pid", 
        "Auto-Restore": ".restore.pid"
    }
    
    services_running = 0
    total_services = len(pid_files)
    
    for service_name, pid_file in pid_files.items():
        if os.path.exists(pid_file):
            try:
                with open(pid_file, 'r') as f:
                    pid = f.read().strip()
                
                # Check if process is actually running
                result = subprocess.run(['ps', '-p', pid], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {service_name}: Running (PID: {pid})")
                    services_running += 1
                else:
                    print(f"❌ {service_name}: PID file exists but process not running")
            except Exception as e:
                print(f"❌ {service_name}: Error reading PID file - {e}")
        else:
            print(f"❌ {service_name}: Not running (no PID file)")
    
    print("\n" + "=" * 40)
    print(f"📊 Status: {services_running}/{total_services} services running")
    
    if services_running == total_services:
        print("🎉 All services are running normally!")
    else:
        print("⚠️  Some services are not running properly")
        print("💡 Run './startup_services.sh' to restart all services")
    
    # Check backup status
    print("\n📁 Backup Status:")
    if os.path.exists("merged_backup_20250824_130946.json"):
        print("✅ Clean merged backup exists")
        try:
            with open("merged_backup_20250824_130946.json", 'r') as f:
                backup_data = json.load(f)
                users = len(backup_data.get('users', []))
                customers = len(backup_data.get('customers', []))
                print(f"   👥 Users: {users}")
                print(f"   🏪 Customers: {customers}")
        except:
            print("   ⚠️  Could not read backup details")
    else:
        print("❌ No merged backup found")
    
    # Check recent log activity
    print("\n📝 Recent Activity:")
    log_files = [
        ("Keep-Alive", "keep_alive_ultra_aggressive.log"),
        ("Auto-Backup", "auto_backup_super_aggressive.log"),
        ("Auto-Restore", "auto_restore.log")
    ]
    
    for service_name, log_file in log_files:
        if os.path.exists(log_file):
            try:
                # Get last line of log
                result = subprocess.run(['tail', '-1', log_file], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    last_line = result.stdout.strip()
                    # Extract timestamp if available
                    if '[' in last_line and ']' in last_line:
                        timestamp = last_line[last_line.find('[')+1:last_line.find(']')]
                        print(f"   {service_name}: {timestamp}")
                    else:
                        print(f"   {service_name}: Active")
                else:
                    print(f"   {service_name}: No recent activity")
            except:
                print(f"   {service_name}: Could not read log")
        else:
            print(f"   {service_name}: No log file")
    
    print("\n" + "=" * 40)
    print("💡 Commands:")
    print("   🚀 Start services: ./startup_services.sh")
    print("   🛑 Stop services: ./stop_services.sh")
    print("   📊 Check status: ./check_status.py")

if __name__ == "__main__":
    check_service_status()
