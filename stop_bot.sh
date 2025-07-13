#!/bin/bash

# AI Forex Trading Bot Stop Script
# Uses systemd service for graceful shutdown

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

echo "🛑 AI Forex Trading Bot - Stop Script"
echo "====================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if service file exists
if [ ! -f /etc/systemd/system/forex-bot.service ]; then
    print_error "Systemd service file not found. Please run deploy.sh first."
    exit 1
fi

print_status "Stopping AI Forex Trading Bot..."

# Check if service is running
if sudo systemctl is-active --quiet forex-bot; then
    print_status "Service is running, stopping gracefully..."
    
    # Stop the service
    if sudo systemctl stop forex-bot; then
        print_success "Bot service stopped successfully!"
        
        # Wait a moment for graceful shutdown
        sleep 2
        
        # Verify service is stopped
        if sudo systemctl is-active --quiet forex-bot; then
            print_warning "Service is still running, forcing stop..."
            sudo systemctl kill forex-bot
            sleep 1
        fi
        
        # Final status check
        if sudo systemctl is-active --quiet forex-bot; then
            print_error "Failed to stop service completely"
            echo ""
            print_status "Service Status:"
            sudo systemctl status forex-bot --no-pager -l
            exit 1
        else
            print_success "Service stopped completely"
        fi
        
    else
        print_error "Failed to stop bot service"
        echo ""
        print_status "Service Status:"
        sudo systemctl status forex-bot --no-pager -l
        exit 1
    fi
    
else
    print_warning "Service is not running"
    
    # Check if there are any orphaned processes
    if pgrep -f "python.*trading_bot.py" > /dev/null; then
        print_warning "Found orphaned bot processes, cleaning up..."
        pkill -f "python.*trading_bot.py"
        sleep 1
        
        if pgrep -f "python.*trading_bot.py" > /dev/null; then
            print_warning "Some processes still running, forcing kill..."
            pkill -9 -f "python.*trading_bot.py"
        fi
    fi
fi

# Show final status
echo ""
print_status "Final Service Status:"
sudo systemctl status forex-bot --no-pager -l

echo ""
print_success "✅ Bot stopped successfully!"