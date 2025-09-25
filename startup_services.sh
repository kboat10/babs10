#!/bin/bash
# BABS10 Startup Services Script
# This script starts all backup and keep-alive services as proper daemons

echo "🚀 BABS10 Services Starting..."
echo "=================================="

# Change to the correct directory
cd /Users/kwakuboateng/Documents/babs10

# Kill any existing services first
echo "🔄 Stopping any existing services..."
pkill -f "keep_alive_ultra_aggressive.py" 2>/dev/null
pkill -f "auto_backup_super_aggressive.py" 2>/dev/null
pkill -f "auto_restore_service.py" 2>/dev/null

# Wait a moment for processes to stop
sleep 2

# Start ULTRA aggressive keep-alive (30 second intervals) - FULLY DAEMONIZED
echo "🛡️ Starting ULTRA aggressive keep-alive..."
nohup python3 keep_alive_ultra_aggressive.py > keep_alive_ultra_aggressive.log 2>&1 &
KEEP_ALIVE_PID=$!
echo "✅ Keep-alive started (PID: $KEEP_ALIVE_PID)"

# Start auto-backup service (2 minute intervals) - FULLY DAEMONIZED
echo "🔄 Starting auto-backup service..."
nohup python3 auto_backup_super_aggressive.py > auto_backup_super_aggressive.log 2>&1 &
BACKUP_PID=$!
echo "✅ Auto-backup started (PID: $BACKUP_PID)"

# Start auto-restore service (1 minute checks) - FULLY DAEMONIZED
echo "🔄 Starting auto-restore service..."
nohup python3 auto_restore_service.py > auto_restore.log 2>&1 &
RESTORE_PID=$!
echo "✅ Auto-restore started (PID: $RESTORE_PID)"

# Start remote backend keep-alive service (10 minute intervals) - FULLY DAEMONIZED
echo "🌐 Starting remote backend keep-alive service..."
nohup python3 remote_backend_keep_alive.py > remote_backend_keep_alive.log 2>&1 &
REMOTE_KEEP_ALIVE_PID=$!
echo "✅ Remote backend keep-alive started (PID: $REMOTE_KEEP_ALIVE_PID)"

# Start data synchronization service (5 minute intervals) - FULLY DAEMONIZED
echo "🔄 Starting data synchronization service..."
nohup python3 data_sync_service.py > data_sync_service.log 2>&1 &
DATA_SYNC_PID=$!
echo "✅ Data synchronization started (PID: $DATA_SYNC_PID)"

# Save PIDs to a file for easy management
echo "$KEEP_ALIVE_PID" > .keep_alive.pid
echo "$BACKUP_PID" > .backup.pid
echo "$RESTORE_PID" > .restore.pid
echo "$REMOTE_KEEP_ALIVE_PID" > .remote_keep_alive.pid
echo "$DATA_SYNC_PID" > .data_sync.pid

echo "=================================="
echo "🎉 All services started successfully!"
echo "💡 Your data is now protected 24/7!"
echo "🌐 Website: https://babs10.vercel.app/"
echo "📡 Backend: https://babs10.onrender.com/"
echo "=================================="
echo "📝 Service PIDs saved to .*.pid files"
echo "🔄 Services will continue running in background"
echo "💡 Use 'ps aux | grep python3' to see running services"
echo "=================================="

# Show running services
sleep 3
echo "🔍 Checking running services..."
ps aux | grep -E "(keep_alive_ultra|auto_backup|auto_restore|remote_backend_keep_alive|data_sync_service)" | grep -v grep

echo ""
echo "✅ Services are now running in background!"
echo "💡 They will continue running even if you close this terminal"
echo "🛑 To stop services: ./stop_services.sh"
echo "📊 To check status: ./check_status.py"
