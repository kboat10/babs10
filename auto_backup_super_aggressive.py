#!/usr/bin/env python3
"""
Super Aggressive Auto-Backup Service for BABS10
This service creates backups every 2 minutes to ensure maximum data protection
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
BACKEND_URL = "https://babs10-backend.vercel.app/api"  # Use Vercel backend (more reliable)
BACKUP_DIR = "auto_backups_super"
BACKUP_INTERVAL = 120  # 2 minutes instead of 5
LOG_FILE = "auto_backup_super_aggressive.log"
MAIN_BACKUP_FILE = "data_backup.json"  # Main backup file for auto-restore

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
        log_message("🔄 Starting super aggressive backup...")
        
        # Get all users
        users = get_all_users()
        if not users:
            log_message("⚠️ No users found, skipping backup")
            return False
        
        log_message(f"👥 Found {len(users)} users")
        
        # Get customers for each user
        all_data = {
            "backup_created": datetime.datetime.now().isoformat(),
            "backup_type": "super_aggressive_auto",
            "backup_interval_minutes": BACKUP_INTERVAL / 60,
            "users": users,
            "customers": []
        }
        
        total_customers = 0
        for user in users:
            user_id = user.get('id')
            if user_id:
                customers = get_customers_for_user(user_id)
                all_data["customers"].extend(customers)
                total_customers += len(customers)
                log_message(f"📊 User {user['email']}: {len(customers)} customers")
        
        log_message(f"🏪 Total customers across all users: {total_customers}")
        
        # Create timestamped backup file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{BACKUP_DIR}/super_backup_{timestamp}.json"
        
        with open(backup_filename, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        log_message(f"✅ Super backup created: {backup_filename}")
        
        # ALSO update the main backup file for auto-restore service
        with open(MAIN_BACKUP_FILE, 'w') as f:
            json.dump(all_data, f, indent=2)
        log_message(f"✅ Main backup file updated: {MAIN_BACKUP_FILE}")
        
        # Count total customers
        total_customers = len(all_data["customers"])
        log_message(f"📊 Total customers backed up: {total_customers}")
        
        # Clean up old backups (keep only last 10)
        cleanup_old_backups()
        
        return True
        
    except Exception as e:
        log_message(f"❌ Error creating backup: {e}")
        return False

def cleanup_old_backups():
    """Clean up old backup files, keeping only the last 10"""
    try:
        backup_files = []
        for file in os.listdir(BACKUP_DIR):
            if file.startswith("super_backup_") and file.endswith(".json"):
                file_path = os.path.join(BACKUP_DIR, file)
                backup_files.append((file_path, os.path.getmtime(file_path)))
        
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        # Keep only the last 10 backups
        if len(backup_files) > 10:
            for file_path, _ in backup_files[10:]:
                os.remove(file_path)
                log_message(f"🗑️ Deleted old backup: {os.path.basename(file_path)}")
                
    except Exception as e:
        log_message(f"⚠️ Error cleaning up old backups: {e}")

def main():
    """Main backup service loop"""
    log_message("🚀 BABS10 Super Aggressive Auto-Backup Service Starting...")
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        log_message(f"📡 Received signal {signum}, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create backup directory
    create_backup_directory()
    
    # Create initial backup
    log_message("🔄 Creating initial super backup...")
    if create_backup():
        log_message("✅ Initial backup completed successfully")
    else:
        log_message("❌ Initial backup failed")
    
    backup_count = 0
    
    # Main backup loop
    while True:
        try:
            time.sleep(BACKUP_INTERVAL)
            backup_count += 1
            
            log_message(f"🔄 Super backup #{backup_count}...")
            
            if create_backup():
                log_message(f"✅ Super backup #{backup_count} completed successfully")
            else:
                log_message(f"❌ Super backup #{backup_count} failed")
            
            log_message(f"⏳ Waiting {BACKUP_INTERVAL} seconds until next backup...")
            
        except KeyboardInterrupt:
            log_message("🛑 Manual stop requested")
            break
        except Exception as e:
            log_message(f"❌ Unexpected error in backup loop: {e}")
            time.sleep(60)  # Wait a minute before retrying
    
    log_message("🛑 Auto-backup service stopped")

if __name__ == "__main__":
    main()
