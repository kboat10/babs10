#!/usr/bin/env python3
"""
Manual Backup Script for BABS10
Run this script anytime to create a manual backup of your current data
"""

import json
import requests
import datetime
import os
from pathlib import Path

# Configuration
BACKEND_URL = "https://babs10.onrender.com/api"
BACKUP_DIR = "manual_backups"

def create_backup_directory():
    """Create backup directory if it doesn't exist"""
    Path(BACKUP_DIR).mkdir(exist_ok=True)
    print(f"📁 Backup directory: {BACKUP_DIR}")

def get_all_users():
    """Fetch all users from backend"""
    try:
        print("🔍 Fetching users...")
        response = requests.get(f"{BACKEND_URL}/users", timeout=30)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Found {len(users)} users")
            return users
        else:
            print(f"❌ Failed to fetch users: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return []

def get_customers_for_user(user_id, user_email):
    """Fetch customers for a specific user"""
    try:
        print(f"🔍 Fetching customers for {user_email}...")
        response = requests.get(f"{BACKEND_URL}/customers?user_id={user_id}", timeout=30)
        if response.status_code == 200:
            customers = response.json()
            print(f"✅ Found {len(customers)} customers for {user_email}")
            return customers
        else:
            print(f"❌ Failed to fetch customers for {user_email}: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching customers for {user_email}: {e}")
        return []

def create_manual_backup():
    """Create a complete manual backup of all data"""
    try:
        print("🚀 Starting manual backup...")
        print("=" * 60)
        
        # Get all users
        users = get_all_users()
        if not users:
            print("⚠️ No users found, cannot create backup")
            return False
        
        # Get customers for each user
        all_data = {
            "backup_created": datetime.datetime.now().isoformat(),
            "backup_type": "manual",
            "backup_triggered_by": "user_request",
            "users": users,
            "customers": []
        }
        
        total_customers = 0
        for user in users:
            user_id = user.get('id')
            user_email = user.get('email', 'unknown')
            if user_id:
                customers = get_customers_for_user(user_id, user_email)
                all_data["customers"].extend(customers)
                total_customers += len(customers)
        
        # Create timestamped backup file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{BACKUP_DIR}/manual_backup_{timestamp}.json"
        
        with open(backup_filename, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        print("=" * 60)
        print(f"✅ Manual backup created successfully!")
        print(f"📁 File: {backup_filename}")
        print(f"👥 Users backed up: {len(users)}")
        print(f"🏪 Customers backed up: {total_customers}")
        print(f"📊 Total data size: {os.path.getsize(backup_filename)} bytes")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating manual backup: {e}")
        return False

def list_existing_backups():
    """List all existing manual backups"""
    try:
        backup_files = list(Path(BACKUP_DIR).glob("manual_backup_*.json"))
        if backup_files:
            print(f"\n📚 Existing manual backups ({len(backup_files)}):")
            for file in sorted(backup_files, reverse=True):
                size = os.path.getsize(file)
                modified = datetime.datetime.fromtimestamp(file.stat().st_mtime)
                print(f"  📄 {file.name} ({size} bytes) - {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"\n📚 No existing manual backups found in {BACKUP_DIR}")
    except Exception as e:
        print(f"❌ Error listing backups: {e}")

def main():
    """Main backup function"""
    print("🚀 BABS10 Manual Backup Tool")
    print("=" * 60)
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print(f"📁 Backup directory: {BACKUP_DIR}")
    print("=" * 60)
    
    # Create backup directory
    create_backup_directory()
    
    # Create backup
    success = create_manual_backup()
    
    if success:
        # List existing backups
        list_existing_backups()
        
        print(f"\n🎉 Manual backup completed successfully!")
        print(f"💡 You can run this script anytime to create a new backup")
        print(f"💡 Your data is now protected locally and on the backend")
    else:
        print(f"\n❌ Manual backup failed!")
        print(f"💡 Check the error messages above and try again")

if __name__ == "__main__":
    main()
