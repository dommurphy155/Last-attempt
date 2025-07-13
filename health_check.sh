#!/bin/bash

# AI Forex Trading Bot Health Check Script
# Used by systemd timer to monitor bot health

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Log function for systemd
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log "Starting health check for forex-bot service"

# Check if service is running
if ! sudo systemctl is-active --quiet forex-bot; then
    log "Service is not running, attempting to restart"
    sudo systemctl restart forex-bot
    sleep 5
    
    if sudo systemctl is-active --quiet forex-bot; then
        log "Service restarted successfully"
    else
        log "Failed to restart service"
        exit 1
    fi
else
    log "Service is running normally"
fi

# Check if process is responsive (optional)
if pgrep -f "python.*trading_bot.py" > /dev/null; then
    PID=$(pgrep -f "python.*trading_bot.py")
    
    # Check if process is consuming reasonable resources
    MEMORY_KB=$(ps -o rss= -p $PID 2>/dev/null | awk '{print $1}' || echo "0")
    MEMORY_MB=$((MEMORY_KB / 1024))
    
    if [ $MEMORY_MB -gt 1000 ]; then
        log "Warning: High memory usage detected (${MEMORY_MB}MB)"
    fi
    
    # Check if process has been running for too long (optional restart)
    UPTIME_SECONDS=$(ps -o etimes= -p $PID 2>/dev/null | awk '{print $1}' || echo "0")
    UPTIME_HOURS=$((UPTIME_SECONDS / 3600))
    
    if [ $UPTIME_HOURS -gt 24 ]; then
        log "Service has been running for ${UPTIME_HOURS} hours, considering restart"
        # Only restart if it's been running for more than 24 hours
        sudo systemctl restart forex-bot
        log "Service restarted due to long uptime"
    fi
else
    log "Process not found, restarting service"
    sudo systemctl restart forex-bot
fi

# Check recent error logs
ERROR_COUNT=$(sudo journalctl -u forex-bot -p err --since "1 hour ago" --no-pager | wc -l)

if [ $ERROR_COUNT -gt 10 ]; then
    log "High error count detected (${ERROR_COUNT} errors in last hour), restarting service"
    sudo systemctl restart forex-bot
fi

log "Health check completed successfully"