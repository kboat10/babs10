#!/bin/bash
# BABS10 Stop Services Script
# This script stops all backup and keep-alive services

echo "🛑 BABS10 Services Stopping..."
echo "=================================="

# Change to the correct directory
cd /Users/kwakuboateng/Documents/babs10

# Stop services using PIDs if available
if [ -f ".keep_alive.pid" ]; then
    KEEP_ALIVE_PID=$(cat .keep_alive.pid)
    echo "🛑 Stopping keep-alive service (PID: $KEEP_ALIVE_PID)..."
    kill $KEEP_ALIVE_PID 2>/dev/null
    rm .keep_alive.pid
else
    echo "🛑 Stopping keep-alive service..."
    pkill -f "keep_alive_ultra_aggressive.py" 2>/dev/null
fi

if [ -f ".backup.pid" ]; then
    BACKUP_PID=$(cat .backup.pid)
    echo "🛑 Stopping auto-backup service (PID: $BACKUP_PID)..."
    kill $BACKUP_PID 2>/dev/null
    rm .backup.pid
else
    echo "🛑 Stopping auto-backup service..."
    pkill -f "auto_backup_super_aggressive.py" 2>/dev/null
fi

if [ -f ".restore.pid" ]; then
    RESTORE_PID=$(cat .restore.pid)
    echo "🛑 Stopping auto-restore service (PID: $RESTORE_PID)..."
    kill $RESTORE_PID 2>/dev/null
    rm .restore.pid
else
    echo "🛑 Stopping auto-restore service..."
    pkill -f "auto_restore_service.py" 2>/dev/null
fi

if [ -f ".remote_keep_alive.pid" ]; then
    REMOTE_KEEP_ALIVE_PID=$(cat .remote_keep_alive.pid)
    echo "🛑 Stopping remote backend keep-alive service (PID: $REMOTE_KEEP_ALIVE_PID)..."
    kill $REMOTE_KEEP_ALIVE_PID 2>/dev/null
    rm .remote_keep_alive.pid
else
    echo "🛑 Stopping remote backend keep-alive service..."
    pkill -f "remote_backend_keep_alive.py" 2>/dev/null
fi

if [ -f ".data_sync.pid" ]; then
    DATA_SYNC_PID=$(cat .data_sync.pid)
    echo "🛑 Stopping data synchronization service (PID: $DATA_SYNC_PID)..."
    kill $DATA_SYNC_PID 2>/dev/null
    rm .data_sync.pid
else
    echo "🛑 Stopping data synchronization service..."
    pkill -f "data_sync_service.py" 2>/dev/null
fi

# Force kill any remaining processes
echo "🔄 Force stopping any remaining processes..."
pkill -f "keep_alive_ultra_aggressive.py" 2>/dev/null
pkill -f "auto_backup_super_aggressive.py" 2>/dev/null
pkill -f "auto_restore_service.py" 2>/dev/null
pkill -f "remote_backend_keep_alive.py" 2>/dev/null
pkill -f "data_sync_service.py" 2>/dev/null

# Wait a moment
sleep 2

echo "=================================="
echo "🔍 Checking if services are stopped..."
ps aux | grep -E "(keep_alive_ultra|auto_backup|auto_restore|remote_backend_keep_alive|data_sync_service)" | grep -v grep

if [ $? -eq 1 ]; then
    echo "✅ All services stopped successfully!"
else
    echo "⚠️  Some services may still be running"
fi

echo "=================================="
echo "💡 To restart services: ./startup_services.sh"
echo "📊 To check status: ./check_status.py"
