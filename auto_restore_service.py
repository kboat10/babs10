#!/usr/bin/env python3
"""
Auto-Restore Service for BABS10
This service automatically restores data when the backend wakes up from sleep
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
BACKUP_FILE = "data_backup.json"
CHECK_INTERVAL = 60  # Check every minute
LOG_FILE = "auto_restore.log"

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

def check_backend_data():
    """Check if backend has data"""
    try:
        # Check users endpoint
        response = requests.get(f"{BACKEND_URL}/users", timeout=10)
        if response.status_code == 200:
            users = response.json()
            if len(users) > 0:
                # Check if users have customers
                total_customers = 0
                for user in users:
                    user_id = user.get('id')
                    if user_id:
                        customer_response = requests.get(f"{BACKEND_URL}/customers?user_id={user_id}", timeout=10)
                        if customer_response.status_code == 200:
                            customers = customer_response.json()
                            total_customers += len(customers)
                
                log_message(f"✅ Backend has data: {len(users)} users, {total_customers} customers")
                return True, len(users), total_customers
            else:
                log_message("⚠️  Backend has no users")
                return False, 0, 0
        else:
            log_message(f"❌ Backend users endpoint error: {response.status_code}")
            return False, 0, 0
    except Exception as e:
        log_message(f"❌ Error checking backend data: {e}")
        return False, 0, 0

def restore_data():
    """Restore data from backup"""
    try:
        if not os.path.exists(BACKUP_FILE):
            log_message(f"❌ Backup file not found: {BACKUP_FILE}")
            return False
        
        log_message("🔄 Starting automatic data restoration...")
        
        # Load backup data
        with open(BACKUP_FILE, 'r') as f:
            backup_data = json.load(f)
        
        users = backup_data.get('users', [])
        customers = backup_data.get('customers', [])
        
        log_message(f"📊 Backup contains: {len(users)} users, {len(customers)} customers")
        
        # Create users
        user_map = {}  # Map old user IDs to new ones
        for user in users:
            try:
                user_data = {
                    "email": user['email'],
                    "pin": "2222"  # Default PIN
                }
                
                response = requests.post(f"{BACKEND_URL}/users", json=user_data, timeout=30)
                if response.status_code in [200, 201]:
                    new_user = response.json()
                    user_map[user['id']] = new_user['id']
                    log_message(f"✅ Created user: {user['email']} (ID: {new_user['id']})")
                else:
                    log_message(f"❌ Failed to create user {user['email']}: {response.status_code}")
                    return False
            except Exception as e:
                log_message(f"❌ Error creating user {user['email']}: {e}")
                return False
        
        # Create customers
        restored_customers = 0
        for customer in customers:
            try:
                # Find the user ID for this customer
                user_id = None
                for old_id, new_id in user_map.items():
                    if customer.get('user_id') == old_id:
                        user_id = new_id
                        break
                
                if not user_id:
                    # If no user_id in customer, use the first user
                    user_id = list(user_map.values())[0]
                
                customer_data = {
                    "name": customer['name'],
                    "money_given": customer.get('money_given', 0.0),
                    "total_spent": customer.get('total_spent', 0.0),
                    "orders": customer.get('orders', [])
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/customers", 
                    json=customer_data,
                    params={"user_id": user_id},
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    log_message(f"✅ Customer {customer['name']} restored successfully")
                    restored_customers += 1
                else:
                    log_message(f"❌ Failed to restore customer {customer['name']}: {response.status_code}")
                    
            except Exception as e:
                log_message(f"❌ Error restoring customer {customer['name']}: {e}")
        
        log_message(f"🎉 Data restoration completed! Restored {restored_customers}/{len(customers)} customers")
        return True
        
    except Exception as e:
        log_message(f"❌ Error in restore_data: {e}")
        return False

def main():
    """Main service loop"""
    log_message("🚀 BABS10 Auto-Restore Service Starting...")
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        log_message(f"📡 Received signal {signum}, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    check_count = 0
    
    while True:
        try:
            check_count += 1
            log_message(f"🔍 Data check #{check_count}...")
            
            # Check if backend has data
            has_data, user_count, customer_count = check_backend_data()
            
            if has_data and user_count > 0 and customer_count > 0:
                log_message(f"✅ Backend data intact: {user_count} users, {customer_count} customers")
            else:
                log_message("⚠️  Backend missing data, triggering restoration...")
                if restore_data():
                    log_message("✅ Data restoration successful!")
                else:
                    log_message("❌ Data restoration failed")
            
            log_message(f"⏳ Waiting {CHECK_INTERVAL} seconds until next check...")
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            log_message(f"❌ Unexpected error in check loop: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
