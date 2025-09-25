#!/bin/bash
# BABS10 LaunchD Daemon Installer
# This creates a service that runs completely independently using launchd

echo "🚀 Installing BABS10 as LaunchD Daemon..."
echo "=========================================="

# Get the current user and directory
CURRENT_USER=$(whoami)
CURRENT_DIR=$(pwd)

echo "👤 Current user: $CURRENT_USER"
echo "📁 Current directory: $CURRENT_DIR"

# Stop any existing services first
echo "🔄 Stopping existing services..."
./stop_services.sh 2>/dev/null
launchctl unload "/Users/$CURRENT_USER/Library/LaunchAgents/com.babs10.daemon.plist" 2>/dev/null

# Create individual service files for each component
echo "📝 Creating individual LaunchD services..."

# Keep-Alive Service
KEEP_ALIVE_SERVICE="/Users/$CURRENT_USER/Library/LaunchAgents/com.babs10.keepalive.plist"
cat > "$KEEP_ALIVE_SERVICE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.babs10.keepalive</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$CURRENT_DIR/keep_alive_ultra_aggressive.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$CURRENT_DIR/keep_alive_system.log</string>
    <key>StandardErrorPath</key>
    <string>$CURRENT_DIR/keep_alive_system_error.log</string>
    <key>WorkingDirectory</key>
    <string>$CURRENT_DIR</string>
    <key>ProcessType</key>
    <string>Background</string>
    <key>SessionCreate</key>
    <false/>
    <key>AbandonProcessGroup</key>
    <true/>
</dict>
</plist>
EOF

# Auto-Backup Service
BACKUP_SERVICE="/Users/$CURRENT_USER/Library/LaunchAgents/com.babs10.backup.plist"
cat > "$BACKUP_SERVICE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.babs10.backup</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$CURRENT_DIR/auto_backup_super_aggressive.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$CURRENT_DIR/backup_system.log</string>
    <key>StandardErrorPath</key>
    <string>$CURRENT_DIR/backup_system_error.log</string>
    <key>WorkingDirectory</key>
    <string>$CURRENT_DIR</string>
    <key>ProcessType</key>
    <string>Background</string>
    <key>SessionCreate</key>
    <false/>
    <key>AbandonProcessGroup</key>
    <true/>
</dict>
</plist>
EOF

# Auto-Restore Service
RESTORE_SERVICE="/Users/$CURRENT_USER/Library/LaunchAgents/com.babs10.restore.plist"
cat > "$RESTORE_SERVICE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.babs10.restore</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$CURRENT_DIR/auto_restore_service.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$CURRENT_DIR/restore_system.log</string>
    <key>StandardErrorPath</key>
    <string>$CURRENT_DIR/restore_system_error.log</string>
    <key>WorkingDirectory</key>
    <string>$CURRENT_DIR</string>
    <key>ProcessType</key>
    <string>Background</string>
    <key>SessionCreate</key>
    <false/>
    <key>AbandonProcessGroup</key>
    <true/>
</dict>
</plist>
EOF

echo "✅ Individual service files created"

# Load all services
echo "🔄 Loading LaunchD services..."

launchctl load "$KEEP_ALIVE_SERVICE"
launchctl load "$BACKUP_SERVICE"
launchctl load "$RESTORE_SERVICE"

echo "✅ All services loaded"

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
launchctl list | grep babs10

# Check if processes are running
echo "📊 Checking individual processes..."
ps aux | grep -E "(keep_alive_ultra|auto_backup|auto_restore)" | grep -v grep

echo ""
echo "🎉 BABS10 is now installed as LaunchD Daemons!"
echo "💡 It will:"
echo "   ✅ Run completely independently of your user session"
echo "   ✅ Survive IDE closure"
echo "   ✅ Survive terminal closure"
echo "   ✅ Survive system restarts"
echo "   ✅ Survive WiFi disconnections"
echo "   ✅ Run in true background with process isolation"
echo "   ✅ Auto-restart if any service dies"

echo ""
echo "📋 Service Management Commands:"
echo "   🚀 Start all: launchctl start com.babs10.keepalive && launchctl start com.babs10.backup && launchctl start com.babs10.restore"
echo "   🛑 Stop all: launchctl stop com.babs10.keepalive && launchctl stop com.babs10.backup && launchctl stop com.babs10.restore"
echo "   📊 Status: launchctl list | grep babs10"
echo "   📝 Logs: tail -f *_system.log"

echo ""
echo "=========================================="
echo "🧪 TESTING INSTRUCTIONS:"
echo "   1. Close this terminal completely"
echo "   2. Close your IDE/Cursor"
echo "   3. Wait 2-3 minutes"
echo "   4. Reopen and check: python3 check_status.py"
echo "   5. Check system logs: tail -f *_system.log"
echo ""
echo "🌐 Your data is protected at: https://babs10.vercel.app/"
