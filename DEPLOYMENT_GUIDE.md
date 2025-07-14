# 🤖 AI Forex Trading Bot - Systemd Deployment Guide

## Overview

This guide documents the complete refactoring of the AI Forex Trading Bot from PM2-based deployment to a robust systemd service deployment for Ubuntu 20.04+ servers.

## 🚀 What Was Changed

### Removed PM2 Dependencies
- ✅ Eliminated all PM2-related commands and scripts
- ✅ Removed PM2 configuration files
- ✅ Cleaned up PM2-specific environment variable management
- ✅ Removed PM2 log file parsing and management

### Implemented Systemd Service
- ✅ Created `forex-bot.service` with best practices
- ✅ Configured proper logging via journald
- ✅ Added security settings and resource limits
- ✅ Implemented automatic restart policies
- ✅ Added health monitoring capabilities

### Enhanced Management Scripts
- ✅ `start_bot.sh` - Uses systemctl to start service
- ✅ `stop_bot.sh` - Graceful shutdown via systemctl
- ✅ `status_bot.sh` - Comprehensive status reporting
- ✅ `monitor_bot.sh` - Real-time monitoring with journalctl
- ✅ `setup_env.sh` - Environment variable configuration
- ✅ `cleanup.sh` - Repository optimization

### Improved Bot Code
- ✅ Enhanced signal handling for systemd (SIGTERM, SIGINT, SIGHUP)
- ✅ Optimized logging for journald integration
- ✅ Fixed async Telegram bot polling for main thread
- ✅ Added comprehensive error logging
- ✅ Implemented graceful shutdown procedures

## 📁 File Structure

```
ai-forex-trading-bot/
├── Core Bot Files
│   ├── trading_bot.py          # Main trading bot
│   ├── telegram_bot.py         # Telegram integration
│   ├── oanda_client.py         # OANDA API client
│   ├── technical_analysis.py   # Technical indicators
│   ├── news_sentiment.py       # News sentiment analysis
│   ├── config.py               # Configuration management
│   └── utils.py                # Utility functions
├── Systemd Files
│   ├── forex-bot.service       # Main systemd service
│   └── forex-bot.timer         # Health check timer
├── Management Scripts
│   ├── deploy.sh               # Complete deployment
│   ├── setup_env.sh            # Environment setup
│   ├── start_bot.sh            # Start service
│   ├── stop_bot.sh             # Stop service
│   ├── status_bot.sh           # Status check
│   ├── monitor_bot.sh          # Real-time monitoring
│   ├── backup_bot.sh           # Backup creation
│   ├── cleanup.sh              # Repository cleanup
│   └── health_check.sh         # Health monitoring
├── Configuration
│   ├── requirements.txt        # Python dependencies
│   ├── .env.template           # Environment template
│   └── .gitignore              # Git ignore rules
└── Documentation
    ├── README.md               # Main documentation
    └── DEPLOYMENT_GUIDE.md     # This guide
```

## 🔧 Quick Deployment

### 1. Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd ai-forex-trading-bot

# Run deployment script
./deploy.sh

# Set up environment variables
./setup_env.sh
nano .env  # Fill in your API keys
```

### 2. Start the Bot
```bash
# Start as systemd service
./start_bot.sh

# Or manually
sudo systemctl start forex-bot
sudo systemctl enable forex-bot  # Auto-start on boot
```

### 3. Monitor and Manage
```bash
# Check status
./status_bot.sh

# Real-time monitoring
./monitor_bot.sh

# View logs
sudo journalctl -u forex-bot -f

# Stop bot
./stop_bot.sh
```

## 📊 Systemd Service Features

### Service Configuration
- **Type**: Simple
- **User**: ubuntu (or current user)
- **Working Directory**: Project root
- **Environment**: Virtual environment Python
- **Restart Policy**: Always with exponential backoff
- **Logging**: journald integration
- **Security**: Sandboxed with resource limits

### Health Monitoring
- **Timer**: Runs every 30 minutes
- **Checks**: Service status, memory usage, error count
- **Actions**: Automatic restart on failure
- **Logging**: All health checks logged to journald

### Resource Limits
- **Memory**: 1GB maximum
- **CPU**: 200% quota
- **File Descriptors**: 65,536 limit
- **Security**: No new privileges, private temp

## 🔍 Monitoring and Logging

### Log Management
- All logs go to systemd journald
- No local log files (cleaner deployment)
- Structured logging with timestamps
- Error tracking and alerting

### Monitoring Commands
```bash
# View all logs
sudo journalctl -u forex-bot

# Follow logs in real-time
sudo journalctl -u forex-bot -f

# View recent logs
sudo journalctl -u forex-bot -n 50

# View error logs only
sudo journalctl -u forex-bot -p err

# View logs since specific time
sudo journalctl -u forex-bot --since "1 hour ago"
```

### Status Monitoring
```bash
# Comprehensive status check
./status_bot.sh

# Real-time monitoring
./monitor_bot.sh

# Service status
sudo systemctl status forex-bot
```

## 🛠️ Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   sudo systemctl status forex-bot
   sudo journalctl -u forex-bot -p err
   ./status_bot.sh
   ```

2. **Environment Variables**
   ```bash
   ./setup_env.sh
   cat .env
   sudo systemctl show forex-bot --property=Environment
   ```

3. **Permission Issues**
   ```bash
   sudo chown -R $USER:$USER /workspace
   chmod +x *.sh
   ```

4. **Memory Issues**
   ```bash
   free -h
   sudo journalctl -u forex-bot | grep "memory"
   ```

### Debug Mode
```bash
# Run directly for debugging
source venv/bin/activate
python trading_bot.py
```

## 🔄 Maintenance

### Regular Tasks
```bash
# Check service health
./status_bot.sh

# Create backups
./backup_bot.sh

# Clean up repository
./cleanup.sh

# Update dependencies
pip install -r requirements.txt --upgrade
```

### Service Management
```bash
# Restart service
sudo systemctl restart forex-bot

# Reload configuration
sudo systemctl reload forex-bot

# Check service health
sudo systemctl is-active forex-bot
```

## 📈 Performance Optimizations

### Implemented Features
- ✅ Async Telegram bot polling in main thread
- ✅ Comprehensive error logging to journald
- ✅ Graceful shutdown with signal handling
- ✅ Automatic restart with exponential backoff
- ✅ Resource monitoring and limits
- ✅ Health check timer for reliability
- ✅ Clean environment variable management

### Monitoring Capabilities
- ✅ Real-time log following
- ✅ Performance metrics tracking
- ✅ Error rate monitoring
- ✅ Memory and CPU usage tracking
- ✅ Service uptime monitoring
- ✅ Automatic failure recovery

## 🎯 Production Readiness

### Security Features
- ✅ Sandboxed service execution
- ✅ No privilege escalation
- ✅ Resource limits enforced
- ✅ Secure environment variable handling
- ✅ Private temporary directories

### Reliability Features
- ✅ Automatic restart on failure
- ✅ Health monitoring timer
- ✅ Graceful shutdown handling
- ✅ Comprehensive error logging
- ✅ State persistence
- ✅ Backup and recovery procedures

### Monitoring Features
- ✅ Systemd journald integration
- ✅ Real-time status monitoring
- ✅ Performance metrics tracking
- ✅ Error alerting and recovery
- ✅ Service health checks

## 🚀 Deployment Checklist

- [ ] Run `./deploy.sh` for initial setup
- [ ] Configure environment variables with `./setup_env.sh`
- [ ] Edit `.env` file with API keys
- [ ] Test configuration validation
- [ ] Start service with `./start_bot.sh`
- [ ] Verify service is running with `./status_bot.sh`
- [ ] Enable auto-start: `sudo systemctl enable forex-bot`
- [ ] Enable health monitoring: `sudo systemctl enable forex-bot.timer`
- [ ] Test monitoring with `./monitor_bot.sh`
- [ ] Create initial backup with `./backup_bot.sh`

## 📞 Support

For issues and support:
1. Check logs: `sudo journalctl -u forex-bot`
2. Verify status: `./status_bot.sh`
3. Review configuration: `cat .env`
4. Check service: `sudo systemctl status forex-bot`
5. Monitor resources: `free -h && df -h`

---

**The bot is now 100% compatible with systemd and ready for production Linux deployment! 🎉**