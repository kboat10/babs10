# BABS10 Service Management Guide

## 🚀 Quick Start

### Start All Services
```bash
./startup_services.sh
```
This will start all services in the background and they will continue running even if you close the terminal.

### Stop All Services
```bash
./stop_services.sh
```

### Check Service Status
```bash
python3 check_status.py
```

## 📋 What Each Service Does

### 🛡️ Keep-Alive Service
- **Purpose**: Keeps your backend awake 24/7
- **Frequency**: Every 30 seconds
- **Log File**: `keep_alive_ultra_aggressive.log`

### 🔄 Auto-Backup Service
- **Purpose**: Creates automatic backups of all your data
- **Frequency**: Every 2 minutes
- **Log File**: `auto_backup_super_aggressive.log`
- **Backup Location**: `auto_backups_super/` folder

### 🔄 Auto-Restore Service
- **Purpose**: Automatically restores data if needed
- **Frequency**: Every 1 minute
- **Log File**: `auto_restore.log`

## 🔧 How It Works

1. **Background Execution**: Services run using `nohup` to persist in background
2. **PID Tracking**: Each service saves its Process ID to a `.pid` file
3. **Automatic Restart**: If you close the terminal, services keep running
4. **Log Monitoring**: All activity is logged to separate log files

## 📁 Important Files

- **`.keep_alive.pid`** - Keep-alive service Process ID
- **`.backup.pid`** - Auto-backup service Process ID  
- **`.restore.pid`** - Auto-restore service Process ID
- **`merged_backup_20250824_130946.json`** - Clean current backup
- **`data_backup.json`** - Main backup file for restoration

## 🚨 Troubleshooting

### Services Not Running
```bash
# Check if services are running
python3 check_status.py

# Restart all services
./stop_services.sh
./startup_services.sh
```

### Check Individual Service Logs
```bash
# Keep-alive logs
tail -f keep_alive_ultra_aggressive.log

# Auto-backup logs  
tail -f auto_backup_super_aggressive.log

# Auto-restore logs
tail -f auto_restore.log
```

### Force Stop Services
```bash
# Kill all Python processes (use with caution)
pkill -f "keep_alive_ultra_aggressive.py"
pkill -f "auto_backup_super_aggressive.py"
pkill -f "auto_restore_service.py"
```

## 💡 Best Practices

1. **Always use the scripts**: Use `./startup_services.sh` and `./stop_services.sh`
2. **Check status regularly**: Run `python3 check_status.py` to monitor health
3. **Monitor logs**: Check log files if something seems wrong
4. **Don't manually kill processes**: Use the stop script instead

## 🌐 Access Your System

- **Website**: https://babs10.vercel.app/
- **Backend**: https://babs10.onrender.com/

## 📊 Current Data Status

- **Users**: 1 (lynaboateng1@gmail.com)
- **Customers**: 6 (Grandma, Kwasi, Theresa/Kwaku, Sheila, Titi School, Uncle K)
- **Total Orders**: 26+
- **Backup Frequency**: Every 2 minutes
- **Protection Level**: 24/7 Ultra Protection

Your data is now fully protected and automatically managed! 🛡️✨
