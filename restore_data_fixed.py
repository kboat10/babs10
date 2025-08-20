#!/usr/bin/env python3
"""
Fixed Data Restoration Script for BABS10
This script properly restores data by mapping old user IDs to new ones
"""

import json
import requests
import sys
from datetime import datetime

# Configuration
API_BASE_URL = "https://babs10.onrender.com/api"
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

def get_user_id_mapping(users_data):
    """Get mapping of email to user ID from the deployed backend"""
    print("🔄 Getting user ID mapping from deployed backend...")
    
    email_to_id = {}
    for user in users_data:
        try:
            # Get user by email from backend
            response = requests.get(f"{API_BASE_URL}/users/{user['email']}")
            if response.status_code == 200:
                user_data = response.json()
                email_to_id[user['email']] = user_data['id']
                print(f"✅ Mapped {user['email']} -> {user_data['id']}")
            else:
                print(f"⚠️  Could not get user ID for {user['email']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting user ID for {user['email']}: {str(e)}")
    
    return email_to_id

def restore_customers_with_mapping(customers_data, email_to_id):
    """Restore customers using email-to-ID mapping"""
    print(f"\n🔄 Restoring {len(customers_data)} customers...")
    
    restored_count = 0
    for customer in customers_data:
        try:
            # Find the user email for this customer
            # We need to get the user email from the backup
            user_id = customer.get("user_id")
            
            # Find which user this customer belongs to
            user_email = None
            for user in backup_data.get('users', []):
                if user.get('id') == user_id:
                    user_email = user.get('email')
                    break
            
            if not user_email:
                print(f"⚠️  Could not find user email for customer {customer['name']}, skipping")
                continue
            
            # Get the new user ID
            new_user_id = email_to_id.get(user_email)
            if not new_user_id:
                print(f"⚠️  No new user ID found for {user_email}, skipping customer {customer['name']}")
                continue
            
            # Create customer with new user ID
            customer_data = {
                "name": customer["name"],
                "money_given": customer.get("money_given", 0.0),
                "total_spent": customer.get("total_spent", 0.0),
                "orders": customer.get("orders", [])
            }
            
            response = requests.post(
                f"{API_BASE_URL}/customers",
                json=customer_data,
                params={"user_id": new_user_id}
            )
            
            if response.status_code == 201:
                print(f"✅ Customer {customer['name']} restored successfully")
                restored_count += 1
            elif response.status_code == 400 and "already exists" in response.text:
                print(f"ℹ️  Customer {customer['name']} already exists, skipping...")
            else:
                print(f"❌ Failed to restore customer {customer['name']}: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error restoring customer {customer['name']}: {str(e)}")
    
    return restored_count

def main():
    """Main restoration function"""
    print("🚀 BABS10 Fixed Data Restoration Script")
    print("=" * 50)
    
    global backup_data
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
    
    # Get user ID mapping
    email_to_id = get_user_id_mapping(backup_data.get('users', []))
    
    if not email_to_id:
        print("❌ No user ID mapping found. Cannot restore customers.")
        sys.exit(1)
    
    # Restore customers with proper mapping
    restored_count = restore_customers_with_mapping(backup_data.get('customers', []), email_to_id)
    
    print()
    print("🎉 Data restoration completed!")
    print(f"✅ Restored {restored_count} customers")
    print("💡 You can now log in with your existing accounts:")
    for user in backup_data.get('users', []):
        print(f"   📧 {user['email']} (PIN: {user['pin']})")

if __name__ == "__main__":
    main()
