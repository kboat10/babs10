#!/usr/bin/env python3
"""
Simple Data Restoration Script for BABS10
This script creates users and customers from scratch in the deployed backend
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

def create_user(email, pin):
    """Create a user in the deployed backend"""
    try:
        response = requests.post(f"{API_BASE_URL}/users", json={
            "email": email,
            "pin": pin
        })
        
        if response.status_code == 201:
            user_data = response.json()
            print(f"✅ Created user: {email} (ID: {user_data['id']})")
            return user_data['id']
        else:
            print(f"⚠️  User {email} might already exist: {response.status_code}")
            # Try to get existing user ID
            encoded_email = requests.utils.quote(email)
            user_response = requests.get(f"{API_BASE_URL}/users/{encoded_email}")
            if user_response.status_code == 200:
                user_data = user_response.json()
                print(f"✅ Found existing user: {email} (ID: {user_data['id']})")
                return user_data['id']
            else:
                print(f"❌ Could not create or find user {email}")
                return None
    except Exception as e:
        print(f"❌ Error creating user {email}: {str(e)}")
        return None

def create_customer(customer_data, user_id):
    """Create a customer in the deployed backend"""
    try:
        response = requests.post(f"{API_BASE_URL}/customers", 
                               params={"user_id": user_id},
                               json={
                                   "name": customer_data["name"],
                                   "money_given": customer_data.get("money_given", 0.0),
                                   "total_spent": customer_data.get("total_spent", 0.0),
                                   "orders": customer_data.get("orders", [])
                               })
        
        if response.status_code == 201:
            customer_response = response.json()
            print(f"✅ Created customer: {customer_data['name']} (ID: {customer_response['id']})")
            return True
        else:
            print(f"❌ Failed to create customer {customer_data['name']}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating customer {customer_data['name']}: {str(e)}")
        return False

def main():
    """Main restoration function"""
    print("🚀 BABS10 Simple Data Restoration Script")
    print("=" * 50)
    
    # Load backup data
    backup_data = load_backup_data()
    if not backup_data:
        print("❌ Cannot proceed without backup data")
        return
    
    print(f"📅 Backup created: {backup_data['backup_created']}")
    print(f"👥 Users to restore: {len(backup_data['users'])}")
    print(f"🏪 Customers to restore: {len(backup_data['customers'])}")
    print()
    
    # Test API connection
    try:
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ API connection successful")
        else:
            print("❌ API connection failed")
            return
    except Exception as e:
        print(f"❌ API connection error: {str(e)}")
        return
    
    print()
    
    # Create users first
    user_id_mapping = {}
    for user in backup_data['users']:
        user_id = create_user(user['email'], user['pin'])
        if user_id:
            user_id_mapping[user['email']] = user_id
        print()
    
    if not user_id_mapping:
        print("❌ No users were created. Cannot proceed.")
        return
    
    print("🔄 Creating customers...")
    print()
    
    # Create customers
    customers_created = 0
    for customer in backup_data['customers']:
        user_email = None
        # Find which user this customer belongs to
        for user in backup_data['users']:
            if user['id'] == customer['user_id']:
                user_email = user['email']
                break
        
        if user_email and user_email in user_id_mapping:
            if create_customer(customer, user_id_mapping[user_email]):
                customers_created += 1
        else:
            print(f"⚠️  Could not find user for customer {customer['name']}")
        print()
    
    print("🎉 Restoration Complete!")
    print(f"✅ Users created: {len(user_id_mapping)}")
    print(f"✅ Customers created: {customers_created}")
    print()
    print("🔗 Your app should now work at: https://babs10.vercel.app/")

if __name__ == "__main__":
    main()
