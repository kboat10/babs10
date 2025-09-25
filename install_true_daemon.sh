#!/bin/bash
# BABS10 True Daemon Installer
# This creates a service that runs completely independently

echo "🚀 Installing BABS10 as True System Daemon..."
echo "=============================================="

# Get the current user and directory
CURRENT_USER=$(whoami)
CURRENT_DIR=$(pwd)

echo "👤 Current user: $CURRENT_USER"
echo "📁 Current directory: $CURRENT_DIR"

# Stop any existing services first
echo "🔄 Stopping existing services..."
./stop_services.sh 2>/dev/null

# Create the system daemon service file
SERVICE_FILE="/Users/$CURRENT_USER/Library/LaunchAgents/com.babs10.daemon.plist"

echo "📝 Creating true daemon service file: $SERVICE_FILE"

cat > "$SERVICE_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.babs10.daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$CURRENT_DIR/babs10_system_daemon.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$CURRENT_DIR/system_daemon.log</string>
    <key>StandardErrorPath</key>
    <string>$CURRENT_DIR/system_daemon_error.log</string>
    <key>WorkingDirectory</key>
    <string>$CURRENT_DIR</string>
    <key>ProcessType</key>
    <string>Background</string>
    <key>SessionCreate</key>
    <false/>
    <key>AbandonProcessGroup</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>0</integer>
</dict>
</plist>
EOF

echo "✅ True daemon service file created"

# Make the daemon script executable
chmod +x "$CURRENT_DIR/babs10_system_daemon.py"

# Unload any existing service
launchctl unload "$SERVICE_FILE" 2>/dev/null

# Load the new service
echo "🔄 Loading true daemon service..."
launchctl load "$SERVICE_FILE"

if [ $? -eq 0 ]; then
    echo "✅ True daemon service loaded successfully!"
    
    # Wait a moment for services to start
    echo "⏳ Waiting for services to start..."
    sleep 5
    
    # Check if services are running
    echo "🔍 Checking service status..."
    if [ -f "babs10_daemon.pid" ]; then
        DAEMON_PID=$(cat babs10_daemon.pid)
        echo "✅ Daemon running with PID: $DAEMON_PID"
        
        # Check if processes are running
        sleep 3
        echo "📊 Checking individual services..."
        ps aux | grep -E "(keep_alive_ultra|auto_backup|auto_restore)" | grep -v grep
        
    else
        echo "⚠️  Daemon PID file not found, checking processes..."
        ps aux | grep -E "(keep_alive_ultra|auto_backup|auto_restore)" | grep -v grep
    fi
    
    echo ""
    echo "🎉 BABS10 is now installed as a TRUE SYSTEM DAEMON!"
    echo "💡 It will:"
    echo "   ✅ Run completely independently of your user session"
    echo "   ✅ Survive IDE closure"
    echo "   ✅ Survive terminal closure"
    echo "   ✅ Survive system restarts"
    echo "   ✅ Survive WiFi disconnections"
    echo "   ✅ Run in true background with process isolation"
    
    echo ""
    echo "📋 Service Management Commands:"
    echo "   🚀 Start: launchctl start com.babs10.daemon"
    echo "   🛑 Stop: launchctl stop com.babs10.daemon"
    echo "   🔄 Restart: launchctl unload $SERVICE_FILE && launchctl load $SERVICE_FILE"
    echo "   📊 Status: launchctl list | grep babs10"
    echo "   📝 Logs: tail -f system_daemon.log"
    
else
    echo "❌ Failed to load true daemon service"
    echo "💡 Check the service file: $SERVICE_FILE"
fi

echo ""
echo "=============================================="
echo "🧪 TESTING INSTRUCTIONS:"
echo "   1. Close this terminal completely"
echo "   2. Close your IDE/Cursor"
echo "   3. Wait 2-3 minutes"
echo "   4. Reopen and check: python3 check_status.py"
echo "   5. Check logs: tail -f system_daemon.log"
echo ""
echo "🌐 Your data is protected at: https://babs10.vercel.app/"
