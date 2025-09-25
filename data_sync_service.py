#!/usr/bin/env python3
"""
Data Synchronization Service for BABS10
This service ensures data integrity between local backups and remote backend
"""

import json
import requests
import time
import datetime
import signal
import sys
import os
from pathlib import Path

# Configuration
REMOTE_API = "https://babs10-backend.vercel.app/api"
SYNC_INTERVAL = 300  # 5 minutes
LOG_FILE = "data_sync_service.log"
BACKUP_DIR = "auto_backups_super"
MAIN_BACKUP_FILE = "data_backup.json"

def log_message(message):
    """Log message to file and print to console"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    print(log_entry)
    
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry + '\n')
    except Exception as e:
        print(f"Error writing to log: {e}")

def get_remote_data():
    """Get all data from remote backend"""
    try:
        # Get users
        users_response = requests.get(f"{REMOTE_API}/users", timeout=30)
        if users_response.status_code != 200:
            log_message(f"❌ Failed to get users from remote: {users_response.status_code}")
            return None
        
        users = users_response.json()
        log_message(f"👥 Found {len(users)} users in remote backend")
        
        # Get customers for each user
        all_customers = []
        for user in users:
            user_id = user.get('id')
            if user_id:
                customers_response = requests.get(f"{REMOTE_API}/customers?user_id={user_id}", timeout=30)
                if customers_response.status_code == 200:
                    customers = customers_response.json()
                    all_customers.extend(customers)
                    log_message(f"📊 User {user['email']}: {len(customers)} customers")
                else:
                    log_message(f"⚠️ Failed to get customers for user {user['email']}: {customers_response.status_code}")
        
        return {
            "users": users,
            "customers": all_customers
        }
        
    except Exception as e:
        log_message(f"❌ Error getting remote data: {e}")
        return None

def get_local_backup_data():
    """Get data from local backup files"""
    try:
        # Try to get from main backup file first
        if os.path.exists(MAIN_BACKUP_FILE):
            with open(MAIN_BACKUP_FILE, 'r') as f:
                data = json.load(f)
                log_message(f"📁 Loaded local backup: {len(data.get('users', []))} users, {len(data.get('customers', []))} customers")
                return data
        
        # Fallback to latest backup file
        backup_files = list(Path(BACKUP_DIR).glob("super_backup_*.json"))
        if backup_files:
            latest_backup = max(backup_files, key=os.path.getctime)
            with open(latest_backup, 'r') as f:
                data = json.load(f)
                log_message(f"📁 Loaded latest backup: {len(data.get('users', []))} users, {len(data.get('customers', []))} customers")
                return data
        
        log_message("⚠️ No local backup files found")
        return None
        
    except Exception as e:
        log_message(f"❌ Error loading local backup: {e}")
        return None

def sync_data():
    """Synchronize data between local and remote"""
    try:
        log_message("🔄 Starting data synchronization...")
        
        # Get remote data
        remote_data = get_remote_data()
        if not remote_data:
            log_message("❌ Could not get remote data, skipping sync")
            return False
        
        # Get local data
        local_data = get_local_backup_data()
        if not local_data:
            log_message("⚠️ No local data to compare with")
            return False
        
        # Compare data
        remote_user_count = len(remote_data.get('users', []))
        remote_customer_count = len(remote_data.get('customers', []))
        local_user_count = len(local_data.get('users', []))
        local_customer_count = len(local_data.get('customers', []))
        
        log_message(f"📊 Data comparison:")
        log_message(f"   Remote: {remote_user_count} users, {remote_customer_count} customers")
        log_message(f"   Local:  {local_user_count} users, {local_customer_count} customers")
        
        # Check for discrepancies
        if remote_user_count != local_user_count:
            log_message(f"⚠️ User count mismatch: Remote {remote_user_count} vs Local {local_user_count}")
        
        if remote_customer_count != local_customer_count:
            log_message(f"⚠️ Customer count mismatch: Remote {remote_customer_count} vs Local {local_customer_count}")
        
        # Create a new backup with current remote data
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{BACKUP_DIR}/super_backup_{timestamp}.json"
        
        backup_data = {
            "backup_created": datetime.datetime.now().isoformat(),
            "backup_type": "data_sync_backup",
            "backup_interval_minutes": SYNC_INTERVAL / 60,
            "users": remote_data["users"],
            "customers": remote_data["customers"]
        }
        
        # Save to backup file
        with open(backup_filename, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        # Update main backup file
        with open(MAIN_BACKUP_FILE, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        log_message(f"✅ Data sync completed, backup saved: {backup_filename}")
        log_message(f"✅ Main backup file updated: {MAIN_BACKUP_FILE}")
        
        return True
        
    except Exception as e:
        log_message(f"❌ Error during data sync: {e}")
        return False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    log_message("🛑 Shutdown signal received, stopping data sync service...")
    sys.exit(0)

def main():
    """Main sync loop"""
    log_message("🚀 BABS10 Data Synchronization Service Starting...")
    log_message(f"🌐 Remote API: {REMOTE_API}")
    log_message(f"⏰ Sync interval: {SYNC_INTERVAL} seconds ({SYNC_INTERVAL/60:.1f} minutes)")
    log_message("💡 This service ensures data integrity between local and remote")
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            # Perform data sync
            sync_data()
            
            # Wait for next sync cycle
            log_message(f"⏳ Next sync in {SYNC_INTERVAL/60:.1f} minutes...")
            time.sleep(SYNC_INTERVAL)
            
    except KeyboardInterrupt:
        log_message("🛑 Service stopped by user")
    except Exception as e:
        log_message(f"❌ Unexpected error in main loop: {e}")
        raise

if __name__ == "__main__":
    main()
