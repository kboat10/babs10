#!/usr/bin/env python3
"""
Automatic Backup Service for BABS10
This service continuously monitors the backend and creates local backups
"""

import json
import requests
import time
import datetime
import os
import signal
import sys
from pathlib import Path

# Configuration
BACKEND_URL = "https://babs10.onrender.com/api"
BACKUP_DIR = "auto_backups"
BACKUP_INTERVAL = 300  # 5 minutes
LOG_FILE = "auto_backup.log"

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

def create_backup_directory():
    """Create backup directory if it doesn't exist"""
    Path(BACKUP_DIR).mkdir(exist_ok=True)
    log_message(f"📁 Backup directory: {BACKUP_DIR}")

def get_all_users():
    """Fetch all users from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/users", timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            log_message(f"❌ Failed to fetch users: {response.status_code}")
            return []
    except Exception as e:
        log_message(f"❌ Error fetching users: {e}")
        return []

def get_customers_for_user(user_id):
    """Fetch customers for a specific user"""
    try:
        response = requests.get(f"{BACKEND_URL}/customers?user_id={user_id}", timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            log_message(f"❌ Failed to fetch customers for user {user_id}: {response.status_code}")
            return []
    except Exception as e:
        log_message(f"❌ Error fetching customers for user {user_id}: {e}")
        return []

def create_backup():
    """Create a complete backup of all data"""
    try:
        log_message("🔄 Starting automatic backup...")
        
        # Get all users
        users = get_all_users()
        if not users:
            log_message("⚠️ No users found, skipping backup")
            return False
        
        log_message(f"👥 Found {len(users)} users")
        
        # Get customers for each user
        all_data = {
            "backup_created": datetime.datetime.now().isoformat(),
            "backup_type": "automatic",
            "users": users,
            "customers": []
        }
        
        for user in users:
            user_id = user.get('id')
            if user_id:
                customers = get_customers_for_user(user_id)
                all_data["customers"].extend(customers)
                log_message(f"📊 User {user['email']}: {len(customers)} customers")
        
        # Create timestamped backup file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{BACKUP_DIR}/auto_backup_{timestamp}.json"
        
        with open(backup_filename, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        log_message(f"✅ Backup created: {backup_filename}")
        log_message(f"📊 Total customers backed up: {len(all_data['customers'])}")
        
        # Keep only last 10 backups to save space
        cleanup_old_backups()
        
        return True
        
    except Exception as e:
        log_message(f"❌ Error creating backup: {e}")
        return False

def cleanup_old_backups():
    """Keep only the last 10 backup files"""
    try:
        backup_files = sorted(Path(BACKUP_DIR).glob("auto_backup_*.json"))
        if len(backup_files) > 10:
            files_to_delete = backup_files[:-10]
            for file in files_to_delete:
                file.unlink()
                log_message(f"🗑️ Deleted old backup: {file.name}")
    except Exception as e:
        log_message(f"⚠️ Error cleaning up old backups: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    log_message("🛑 Shutdown signal received, stopping backup service...")
    sys.exit(0)

def main():
    """Main backup service loop"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    log_message("🚀 BABS10 Automatic Backup Service Started")
    log_message("=" * 60)
    log_message(f"🔗 Backend URL: {BACKEND_URL}")
    log_message(f"⏰ Backup interval: {BACKUP_INTERVAL} seconds ({BACKUP_INTERVAL/60:.1f} minutes)")
    log_message(f"📁 Backup directory: {BACKUP_DIR}")
    log_message(f"📝 Log file: {LOG_FILE}")
    log_message("=" * 60)
    
    # Create backup directory
    create_backup_directory()
    
    # Initial backup
    log_message("🔄 Creating initial backup...")
    create_backup()
    
    # Main backup loop
    backup_count = 1
    while True:
        try:
            log_message(f"⏳ Waiting {BACKUP_INTERVAL} seconds until next backup...")
            time.sleep(BACKUP_INTERVAL)
            
            backup_count += 1
            log_message(f"🔄 Backup #{backup_count}...")
            
            success = create_backup()
            if success:
                log_message(f"✅ Backup #{backup_count} completed successfully")
            else:
                log_message(f"❌ Backup #{backup_count} failed")
                
        except KeyboardInterrupt:
            log_message("🛑 Manual stop requested")
            break
        except Exception as e:
            log_message(f"❌ Unexpected error in backup loop: {e}")
            time.sleep(60)  # Wait a minute before retrying
    
    log_message("🛑 Backup service stopped")

if __name__ == "__main__":
    main()
