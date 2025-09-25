#!/bin/bash
# BABS10 System Service Installer
# This creates a proper system service that survives everything

echo "🚀 Installing BABS10 as System Service..."
echo "=========================================="

# Get the current user and directory
CURRENT_USER=$(whoami)
CURRENT_DIR=$(pwd)

echo "👤 Current user: $CURRENT_USER"
echo "📁 Current directory: $CURRENT_DIR"

# Create the service file
SERVICE_FILE="/Users/$CURRENT_USER/Library/LaunchAgents/com.babs10.services.plist"

echo "📝 Creating service file: $SERVICE_FILE"

cat > "$SERVICE_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.babs10.services</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$CURRENT_DIR/startup_services.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$CURRENT_DIR/system_service.log</string>
    <key>StandardErrorPath</key>
    <string>$CURRENT_DIR/system_service_error.log</string>
    <key>WorkingDirectory</key>
    <string>$CURRENT_DIR</string>
    <key>ProcessType</key>
    <string>Background</string>
</dict>
</plist>
EOF

echo "✅ Service file created"

# Make the startup script executable
chmod +x "$CURRENT_DIR/startup_services.sh"

# Load the service
echo "🔄 Loading system service..."
launchctl load "$SERVICE_FILE"

if [ $? -eq 0 ]; then
    echo "✅ System service loaded successfully!"
    echo "🔄 Starting services..."
    
    # Start the services
    cd "$CURRENT_DIR"
    ./startup_services.sh
    
    echo ""
    echo "🎉 BABS10 is now installed as a SYSTEM SERVICE!"
    echo "💡 It will:"
    echo "   ✅ Start automatically when you log in"
    echo "   ✅ Survive IDE closure"
    echo "   ✅ Survive terminal closure"
    echo "   ✅ Survive system restarts"
    echo "   ✅ Run in true background"
    
    echo ""
    echo "📋 Service Management Commands:"
    echo "   🚀 Start: launchctl start com.babs10.services"
    echo "   🛑 Stop: launchctl stop com.babs10.services"
    echo "   🔄 Restart: launchctl unload $SERVICE_FILE && launchctl load $SERVICE_FILE"
    echo "   📊 Status: launchctl list | grep babs10"
    
else
    echo "❌ Failed to load system service"
    echo "💡 Check the service file: $SERVICE_FILE"
fi

echo ""
echo "=========================================="
echo "🔍 To verify it's working:"
echo "   1. Close this terminal"
echo "   2. Close your IDE"
echo "   3. Wait 2 minutes"
echo "   4. Reopen and check: python3 check_status.py"
