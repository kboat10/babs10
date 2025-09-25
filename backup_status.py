#!/usr/bin/env python3
"""
Backup Status Monitor for BABS10
Shows the health and status of all backup systems
"""

import json
import requests
import datetime
import os
from pathlib import Path

# Configuration
BACKEND_URL = "https://babs10.onrender.com/api"

def check_backend_health():
    """Check if backend is healthy"""
    try:
        print("🔍 Checking backend health...")
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend: HEALTHY")
            print(f"   📡 Status: {data.get('status', 'unknown')}")
            print(f"   🗄️ MongoDB: {'Available' if data.get('mongo_available') else 'Not Available'}")
            print(f"   ⏰ Last Update: {data.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"❌ Backend: UNHEALTHY (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend: UNREACHABLE ({e})")
        return False

def check_auto_backup_service():
    """Check if automatic backup service is running"""
    try:
        import psutil
        auto_backup_running = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'auto_backup_service.py' in ' '.join(proc.info['cmdline'] or []):
                    auto_backup_running = True
                    print(f"✅ Auto-backup service: RUNNING (PID: {proc.info['pid']})")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not auto_backup_running:
            print("❌ Auto-backup service: NOT RUNNING")
            return False
        
        # Check log file
        log_file = "auto_backup.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    print(f"   📝 Last log entry: {last_line}")
        
        return True
    except ImportError:
        print("⚠️ Auto-backup service: CANNOT CHECK (psutil not installed)")
        return False
    except Exception as e:
        print(f"❌ Auto-backup service: ERROR ({e})")
        return False

def check_keep_alive_service():
    """Check if keep-alive service is running"""
    try:
        import psutil
        keep_alive_running = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'keep_alive' in ' '.join(proc.info['cmdline'] or []):
                    keep_alive_running = True
                    print(f"✅ Keep-alive service: RUNNING (PID: {proc.info['pid']})")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not keep_alive_running:
            print("❌ Keep-alive service: NOT RUNNING")
            return False
        
        # Check log file
        log_file = "keep_alive_aggressive.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    print(f"   📝 Last log entry: {last_line}")
        
        return True
    except ImportError:
        print("⚠️ Keep-alive service: CANNOT CHECK (psutil not installed)")
        return False
    except Exception as e:
        print(f"❌ Keep-alive service: ERROR ({e})")
        return False

def check_backup_files():
    """Check existing backup files"""
    print("\n📁 Checking backup files...")
    
    # Check auto backups
    auto_backup_dir = "auto_backups"
    if os.path.exists(auto_backup_dir):
        auto_backups = list(Path(auto_backup_dir).glob("auto_backup_*.json"))
        if auto_backups:
            latest_auto = max(auto_backups, key=os.path.getctime)
            size = os.path.getsize(latest_auto)
            modified = datetime.datetime.fromtimestamp(latest_auto.stat().st_mtime)
            print(f"✅ Auto-backups: {len(auto_backups)} files")
            print(f"   📄 Latest: {latest_auto.name}")
            print(f"   📊 Size: {size} bytes")
            print(f"   ⏰ Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("❌ Auto-backups: No files found")
    else:
        print("❌ Auto-backups: Directory not found")
    
    # Check manual backups
    manual_backup_dir = "manual_backups"
    if os.path.exists(manual_backup_dir):
        manual_backups = list(Path(manual_backup_dir).glob("manual_backup_*.json"))
        if manual_backups:
            latest_manual = max(manual_backups, key=os.path.getctime)
            size = os.path.getsize(latest_manual)
            modified = datetime.datetime.fromtimestamp(latest_manual.stat().st_mtime)
            print(f"✅ Manual backups: {len(manual_backups)} files")
            print(f"   📄 Latest: {latest_manual.name}")
            print(f"   📊 Size: {size} bytes")
            print(f"   ⏰ Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("❌ Manual backups: No files found")
    else:
        print("❌ Manual backups: Directory not found")
    
    # Check original backup
    original_backup = "data_backup.json"
    if os.path.exists(original_backup):
        size = os.path.getsize(original_backup)
        modified = datetime.datetime.fromtimestamp(os.path.getmtime(original_backup))
        print(f"✅ Original backup: {original_backup}")
        print(f"   📊 Size: {size} bytes")
        print(f"   ⏰ Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("❌ Original backup: Not found")

def check_data_integrity():
    """Check if data is accessible and complete"""
    print("\n🔍 Checking data integrity...")
    
    try:
        # Check users
        response = requests.get(f"{BACKEND_URL}/users", timeout=10)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Users: {len(users)} found")
            
            # Check customers for each user
            total_customers = 0
            for user in users:
                user_id = user.get('id')
                user_email = user.get('email', 'unknown')
                if user_id:
                    customer_response = requests.get(f"{BACKEND_URL}/customers?user_id={user_id}", timeout=10)
                    if customer_response.status_code == 200:
                        customers = customer_response.json()
                        total_customers += len(customers)
                        print(f"   👤 {user_email}: {len(customers)} customers")
            
            print(f"✅ Total customers: {total_customers}")
            return True
        else:
            print(f"❌ Data integrity: Failed to fetch users (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Data integrity: Error checking data ({e})")
        return False

def main():
    """Main status check function"""
    print("🚀 BABS10 Backup Status Monitor")
    print("=" * 60)
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print(f"⏰ Check time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check all systems
    backend_healthy = check_backend_health()
    print()
    
    auto_backup_ok = check_auto_backup_service()
    print()
    
    keep_alive_ok = check_keep_alive_service()
    print()
    
    check_backup_files()
    
    data_integrity_ok = check_data_integrity()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 BACKUP SYSTEM SUMMARY")
    print("=" * 60)
    print(f"🔧 Backend Health: {'✅ HEALTHY' if backend_healthy else '❌ UNHEALTHY'}")
    print(f"🔄 Auto-backup: {'✅ RUNNING' if auto_backup_ok else '❌ NOT RUNNING'}")
    print(f"🛡️ Keep-alive: {'✅ RUNNING' if keep_alive_ok else '❌ NOT RUNNING'}")
    print(f"📊 Data Integrity: {'✅ GOOD' if data_integrity_ok else '❌ ISSUES'}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if not backend_healthy:
        print("   ❌ Fix backend issues first")
    if not auto_backup_ok:
        print("   🔄 Start auto-backup service: python3 auto_backup_service.py &")
    if not keep_alive_ok:
        print("   🛡️ Start keep-alive service: python3 keep_alive_aggressive.py &")
    if not data_integrity_ok:
        print("   🔍 Investigate data access issues")
    
    if backend_healthy and auto_backup_ok and keep_alive_ok and data_integrity_ok:
        print("   🎉 All systems are healthy! Your data is well protected.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
