#!/bin/bash
# BABS10 Permanent Services Starter
# This starts services and keeps them running in background

echo "🚀 Starting BABS10 Services Permanently..."
echo "=========================================="

# Change to the correct directory
cd /Users/kwakuboateng/Documents/babs10

# Kill any existing services first
echo "🔄 Stopping any existing services..."
pkill -f "keep_alive_ultra_aggressive.py" 2>/dev/null
pkill -f "auto_backup_super_aggressive.py" 2>/dev/null
pkill -f "auto_restore_service.py" 2>/dev/null

# Wait a moment
sleep 2

# Start services with screen (if available) or nohup
echo "🔄 Starting services with maximum isolation..."

# Check if screen is available
if command -v screen &> /dev/null; then
    echo "📺 Using screen for service isolation..."
    
    # Start keep-alive in screen
    screen -dmS babs10_keepalive bash -c "cd $PWD && python3 keep_alive_ultra_aggressive.py"
    echo "✅ Keep-alive started in screen session: babs10_keepalive"
    
    # Start auto-backup in screen
    screen -dmS babs10_backup bash -c "cd $PWD && python3 auto_backup_super_aggressive.py"
    echo "✅ Auto-backup started in screen session: babs10_backup"
    
    # Start auto-restore in screen
    screen -dmS babs10_restore bash -c "cd $PWD && python3 auto_restore_service.py"
    echo "✅ Auto-restore started in screen session: babs10_restore"
    
    echo ""
    echo "📋 Screen Session Management:"
    echo "   📺 List sessions: screen -ls"
    echo "   🔍 Attach to keep-alive: screen -r babs10_keepalive"
    echo "   🔍 Attach to backup: screen -r babs10_backup"
    echo "   🔍 Attach to restore: screen -r babs10_restore"
    echo "   🛑 Kill all sessions: screen -ls | grep babs10 | cut -d. -f1 | xargs -I {} screen -S {} -X quit"
    
else
    echo "📱 Using nohup for service isolation..."
    
    # Start keep-alive with nohup
    nohup python3 keep_alive_ultra_aggressive.py > keep_alive_permanent.log 2>&1 &
    KEEP_ALIVE_PID=$!
    echo "✅ Keep-alive started (PID: $KEEP_ALIVE_PID)"
    
    # Start auto-backup with nohup
    nohup python3 auto_backup_super_aggressive.py > backup_permanent.log 2>&1 &
    BACKUP_PID=$!
    echo "✅ Auto-backup started (PID: $BACKUP_PID)"
    
    # Start auto-restore with nohup
    nohup python3 auto_restore_service.py > restore_permanent.log 2>&1 &
    RESTORE_PID=$!
    echo "✅ Auto-restore started (PID: $RESTORE_PID)"
    
    # Save PIDs
    echo "$KEEP_ALIVE_PID" > .keep_alive_permanent.pid
    echo "$BACKUP_PID" > .backup_permanent.pid
    echo "$RESTORE_PID" > .restore_permanent.pid
    
    echo ""
    echo "📋 Process Management:"
    echo "   📊 Check PIDs: cat .*_permanent.pid"
    echo "   🛑 Stop services: ./stop_services.sh"
fi

echo ""
echo "🎉 Services started with maximum isolation!"
echo "💡 They will:"
echo "   ✅ Run independently of your terminal"
echo "   ✅ Survive IDE closure"
echo "   ✅ Survive WiFi disconnections"
echo "   ✅ Continue running in background"

echo ""
echo "🔍 To verify services are running:"
echo "   python3 check_status.py"
echo "   ps aux | grep python3 | grep -E '(keep_alive|auto_backup|auto_restore)'"

echo ""
echo "🌐 Your data is protected at: https://babs10.vercel.app/"
echo "=========================================="
