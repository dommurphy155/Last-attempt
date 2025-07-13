#!/bin/bash

# AI Forex Trading Bot Monitoring Script
# Uses journalctl for real-time log monitoring

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

echo "🔍 AI Forex Trading Bot - Real-time Monitor"
echo "=========================================="

# Check if service file exists
if [ ! -f /etc/systemd/system/forex-bot.service ]; then
    print_error "Systemd service file not found. Please run deploy.sh first."
    exit 1
fi

# Function to show current status
show_status() {
    clear
    echo "$(date)"
    echo "==============================="
    
    # Check service status
    if sudo systemctl is-active --quiet forex-bot; then
        print_success "✅ Service: RUNNING"
    else
        print_error "❌ Service: STOPPED"
    fi
    
    # Check process
    if pgrep -f "python.*trading_bot.py" > /dev/null; then
        print_success "✅ Process: RUNNING"
        PID=$(pgrep -f "python.*trading_bot.py")
        echo "📊 PID: $PID"
        
        # Show memory usage
        if [ -n "$PID" ]; then
            MEMORY=$(ps -o rss= -p $PID 2>/dev/null | awk '{print $1/1024 " MB"}' || echo "N/A")
            CPU=$(ps -o %cpu= -p $PID 2>/dev/null | awk '{print $1 "%"}' || echo "N/A")
            echo "💾 Memory: $MEMORY"
            echo "⚡ CPU: $CPU"
        fi
    else
        print_error "❌ Process: STOPPED"
    fi
    
    echo ""
}

# Function to show recent logs
show_logs() {
    echo "📝 Recent Logs (Last 5 entries):"
    echo "================================"
    
    if sudo systemctl is-active --quiet forex-bot; then
        sudo journalctl -u forex-bot -n 5 --no-pager --no-hostname
    else
        print_warning "Service not running - no logs available"
    fi
    
    echo ""
}

# Function to show errors
show_errors() {
    echo "❌ Recent Errors (Last 3 entries):"
    echo "=================================="
    
    if sudo systemctl is-active --quiet forex-bot; then
        sudo journalctl -u forex-bot -p err -n 3 --no-pager --no-hostname
    else
        print_warning "Service not running - no error logs available"
    fi
    
    echo ""
}

# Function to show performance stats
show_performance() {
    echo "📈 Performance Summary:"
    echo "======================"
    
    if [ -f "bot_state.json" ]; then
        # Try to extract basic stats (if jq is available)
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
        else
            echo "📊 State file exists (install jq for detailed stats)"
        fi
    else
        print_warning "No state file found"
    fi
    
    echo ""
}

# Function to show system resources
show_resources() {
    echo "💻 System Resources:"
    echo "==================="
    
    # Memory usage
    MEMORY_USAGE=$(free -h | grep Mem | awk '{print $3 "/" $2}')
    echo "💾 Memory: $MEMORY_USAGE"
    
    # Disk usage
    DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}')
    echo "💿 Disk: $DISK_USAGE"
    
    # Load average
    LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}')
    echo "⚡ Load: $LOAD_AVG"
    
    echo ""
}

# Function to show help
show_help() {
    echo "🔧 Available Commands:"
    echo "====================="
    echo "  q - Quit monitoring"
    echo "  r - Refresh status"
    echo "  l - Show live logs (journalctl -f)"
    echo "  e - Show errors only"
    echo "  s - Show service status"
    echo "  h - Show this help"
    echo ""
}

# Main monitoring loop
echo "Starting real-time monitoring..."
echo "Press 'q' to quit, 'h' for help"
echo ""

# Initial status display
show_status
show_logs
show_errors
show_performance
show_resources
show_help

# Check if user wants to follow logs
echo "Choose monitoring mode:"
echo "1. Status monitoring (refresh every 5 seconds)"
echo "2. Live log following (journalctl -f)"
echo "3. Error monitoring only"
echo "4. Exit"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        # Status monitoring mode
        echo "Starting status monitoring (refresh every 5 seconds)..."
        echo "Press Ctrl+C to exit"
        echo ""
        
        while true; do
            show_status
            show_logs
            show_errors
            show_performance
            show_resources
            sleep 5
        done
        ;;
    2)
        # Live log following mode
        echo "Starting live log following..."
        echo "Press Ctrl+C to exit"
        echo ""
        
        if sudo systemctl is-active --quiet forex-bot; then
            sudo journalctl -u forex-bot -f --no-hostname
        else
            print_error "Service not running - cannot follow logs"
            exit 1
        fi
        ;;
    3)
        # Error monitoring mode
        echo "Starting error monitoring..."
        echo "Press Ctrl+C to exit"
        echo ""
        
        while true; do
            clear
            echo "$(date) - Error Monitor"
            echo "======================="
            show_errors
            sleep 10
        done
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac