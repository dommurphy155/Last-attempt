#!/bin/bash

# AI Forex Trading Bot Status Script
# Uses systemctl and journalctl for comprehensive status reporting

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_header() {
    echo -e "${CYAN}$1${NC}"
}

echo "📊 AI Forex Trading Bot - Status Report"
echo "======================================"

# Check if service file exists
if [ ! -f /etc/systemd/system/forex-bot.service ]; then
    print_error "Systemd service file not found. Please run deploy.sh first."
    exit 1
fi

# Service Status
echo ""
print_header "🔧 SYSTEMD SERVICE STATUS"
echo "=============================="

if sudo systemctl is-active --quiet forex-bot; then
    print_success "Service: RUNNING"
    SERVICE_STATUS="running"
else
    print_error "Service: STOPPED"
    SERVICE_STATUS="stopped"
fi

# Show detailed service status
echo ""
print_status "Detailed Service Status:"
sudo systemctl status forex-bot --no-pager -l

# Process Status
echo ""
print_header "🔄 PROCESS STATUS"
echo "=================="

if pgrep -f "python.*trading_bot.py" > /dev/null; then
    print_success "Process: RUNNING"
    PID=$(pgrep -f "python.*trading_bot.py")
    echo "📊 PID: $PID"
    
    # Show memory usage
    if [ -n "$PID" ]; then
        MEMORY=$(ps -o rss= -p $PID 2>/dev/null | awk '{print $1/1024 " MB"}' || echo "N/A")
        CPU=$(ps -o %cpu= -p $PID 2>/dev/null | awk '{print $1 "%"}' || echo "N/A")
        UPTIME=$(ps -o etime= -p $PID 2>/dev/null || echo "N/A")
        
        echo "💾 Memory: $MEMORY"
        echo "⚡ CPU: $CPU"
        echo "⏱️  Uptime: $UPTIME"
    fi
else
    print_error "Process: STOPPED"
fi

# File Status
echo ""
print_header "📁 FILE STATUS"
echo "==============="

# Check important files
FILES=(".env" "bot_state.json" "trading_log.json" "error_log.json" "venv/bin/python")
for file in "${FILES[@]}"; do
    if [ -f "$file" ] || [ -d "$file" ]; then
        print_success "$file: EXISTS"
    else
        print_error "$file: MISSING"
    fi
done

# Environment Variables
echo ""
print_header "🔐 ENVIRONMENT VARIABLES"
echo "============================"

ENV_VARS=("HUGGINGFACE_API_KEY" "TELEGRAM_BOT_TOKEN" "TELEGRAM_CHAT_ID" "OANDA_API_KEY" "OANDA_ACCOUNT_ID")
for var in "${ENV_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        print_success "$var: SET"
    else
        print_error "$var: NOT SET"
    fi
done

# Recent Logs
echo ""
print_header "📝 RECENT LOGS (Last 10 entries)"
echo "====================================="

if [ "$SERVICE_STATUS" = "running" ]; then
    sudo journalctl -u forex-bot -n 10 --no-pager --no-hostname
else
    print_warning "Service not running - no recent logs available"
fi

# Error Logs
echo ""
print_header "❌ RECENT ERRORS (Last 5 entries)"
echo "======================================"

if [ "$SERVICE_STATUS" = "running" ]; then
    sudo journalctl -u forex-bot -p err -n 5 --no-pager --no-hostname
else
    print_warning "Service not running - no error logs available"
fi

# Performance Summary
echo ""
print_header "📈 PERFORMANCE SUMMARY"
echo "=========================="

# Check if state file exists and show basic stats
if [ -f "bot_state.json" ]; then
    echo "📊 State file exists with trading data"
    
    # Try to extract some basic stats (if jq is available)
    if command -v jq &> /dev/null; then
        TOTAL_PNL=$(jq -r '.total_pnl // 0' bot_state.json 2>/dev/null || echo "N/A")
        WIN_COUNT=$(jq -r '.win_count // 0' bot_state.json 2>/dev/null || echo "N/A")
        LOSS_COUNT=$(jq -r '.loss_count // 0' bot_state.json 2>/dev/null || echo "N/A")
        
        echo "💰 Total P&L: $TOTAL_PNL"
        echo "✅ Wins: $WIN_COUNT"
        echo "❌ Losses: $LOSS_COUNT"
        
        if [ "$WIN_COUNT" != "N/A" ] && [ "$LOSS_COUNT" != "N/A" ] && [ "$WIN_COUNT" -gt 0 ] || [ "$LOSS_COUNT" -gt 0 ]; then
            TOTAL_TRADES=$((WIN_COUNT + LOSS_COUNT))
            if [ $TOTAL_TRADES -gt 0 ]; then
                WIN_RATE=$(echo "scale=1; $WIN_COUNT * 100 / $TOTAL_TRADES" | bc 2>/dev/null || echo "N/A")
                echo "🎯 Win Rate: ${WIN_RATE}%"
            fi
        fi
    fi
else
    print_warning "No state file found - bot may not have run yet"
fi

# System Resources
echo ""
print_header "💻 SYSTEM RESOURCES"
echo "======================"

# Memory usage
MEMORY_USAGE=$(free -h | grep Mem | awk '{print $3 "/" $2}')
echo "💾 Memory Usage: $MEMORY_USAGE"

# Disk usage
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}')
echo "💿 Disk Usage: $DISK_USAGE"

# Load average
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}')
echo "⚡ Load Average: $LOAD_AVG"

echo ""
print_success "Status report completed!"
echo ""
print_status "Quick Commands:"
echo "  ./start_bot.sh    - Start the bot"
echo "  ./stop_bot.sh     - Stop the bot"
echo "  ./monitor_bot.sh  - Real-time monitoring"
echo "  ./backup_bot.sh   - Create backup"