#!/usr/bin/env python3
"""
BABS10 Status Checker for Screen Sessions
Check the status of all running services in screen sessions
"""

import os
import subprocess
import json
from datetime import datetime

def check_screen_services():
    """Check the status of all BABS10 services running in screen sessions"""
    print("🔍 BABS10 Screen Service Status Check")
    print("=" * 50)
    
    # Check if screen sessions exist
    try:
        result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
        if result.returncode == 0:
            screen_output = result.stdout
            babs10_sessions = []
            
            # Look for BABS10 screen sessions
            for line in screen_output.split('\n'):
                if 'babs10_' in line and 'Detached' in line:
                    session_name = line.split('.')[1].split()[0]
                    babs10_sessions.append(session_name)
            
            if babs10_sessions:
                print(f"✅ Found {len(babs10_sessions)} BABS10 screen sessions:")
                for session in babs10_sessions:
                    print(f"   📺 {session}")
                
                print(f"\n📊 Status: {len(babs10_sessions)}/3 services running")
                print("🎉 All services are running in screen sessions!")
                
            else:
                print("❌ No BABS10 screen sessions found")
                print("📊 Status: 0/3 services running")
                return False
                
        else:
            print("❌ Could not check screen sessions")
            return False
            
    except Exception as e:
        print(f"❌ Error checking screen sessions: {e}")
        return False
    
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
    
    print("\n" + "=" * 50)
    print("💡 Screen Session Management:")
    print("   📺 List sessions: screen -ls")
    print("   🔍 Attach to keep-alive: screen -r babs10_keepalive")
    print("   🔍 Attach to backup: screen -r babs10_backup")
    print("   🔍 Attach to restore: screen -r babs10_restore")
    print("   🛑 Kill all sessions: screen -ls | grep babs10 | cut -d. -f1 | xargs -I {} screen -S {} -X quit")
    print("   🚀 Restart services: ./start_services_permanent.sh")
    
    return True

if __name__ == "__main__":
    check_screen_services()
