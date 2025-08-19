#!/usr/bin/env python3
"""
Data Restoration Script for BABS10
This script restores all backed up data to ensure nothing is lost during deployment
"""

import json
import requests
import sys
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api"  # Change this to your deployed URL
BACKUP_FILE = "data_backup.json"

def load_backup_data():
    """Load the backup data from file"""
    try:
        with open(BACKUP_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Backup file {BACKUP_FILE} not found!")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error reading backup file {BACKUP_FILE}")
        return None

def restore_users(users_data):
    """Restore all users"""
    print(f"🔄 Restoring {len(users_data)} users...")
    
    for user in users_data:
        try:
            # Create user
            response = requests.post(f"{API_BASE_URL}/users", json={
                "email": user["email"],
                "pin": user["pin"]
            })
            
            if response.status_code == 201:
                print(f"✅ User {user['email']} restored successfully")
            elif response.status_code == 400 and "already exists" in response.text:
                print(f"ℹ️  User {user['email']} already exists, skipping...")
            else:
                print(f"❌ Failed to restore user {user['email']}: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error restoring user {user['email']}: {str(e)}")

def restore_customers(customers_data):
    """Restore all customers"""
    print(f"🔄 Restoring {len(customers_data)} customers...")
    
    for customer in customers_data:
        try:
            # Create customer
            response = requests.post(f"{API_BASE_URL}/customers", json={
                "name": customer["name"],
                "money_given": customer["money_given"],
                "total_spent": customer["total_spent"],
                "orders": customer["orders"]
            }, params={"user_id": customer["user_id"]})
            
            if response.status_code == 201:
                print(f"✅ Customer {customer['name']} restored successfully")
            elif response.status_code == 400 and "already exists" in response.text:
                print(f"ℹ️  Customer {customer['name']} already exists, skipping...")
            else:
                print(f"❌ Failed to restore customer {customer['name']}: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error restoring customer {customer['name']}: {str(e)}")

def main():
    """Main restoration function"""
    print("🚀 BABS10 Data Restoration Script")
    print("=" * 50)
    
    # Load backup data
    backup_data = load_backup_data()
    if not backup_data:
        sys.exit(1)
    
    print(f"📅 Backup created: {backup_data.get('backup_created', 'Unknown')}")
    print(f"👥 Users to restore: {len(backup_data.get('users', []))}")
    print(f"🏪 Customers to restore: {len(backup_data.get('customers', []))}")
    print()
    
    # Test API connection
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API connection successful")
        else:
            print(f"⚠️  API health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to API at {API_BASE_URL}")
        print(f"   Error: {str(e)}")
        print("   Make sure your backend is running!")
        sys.exit(1)
    
    print()
    
    # Restore users first
    restore_users(backup_data.get('users', []))
    print()
    
    # Restore customers
    restore_customers(backup_data.get('customers', []))
    print()
    
    print("🎉 Data restoration completed!")
    print("💡 You can now log in with your existing accounts:")
    for user in backup_data.get('users', []):
        print(f"   📧 {user['email']} (PIN: {user['pin']})")

if __name__ == "__main__":
    main()
