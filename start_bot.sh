#!/bin/bash

# AI Forex Trading Bot Start Script
# Uses systemd service for reliable operation

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

echo "🤖 AI Forex Trading Bot - Start Script"
echo "======================================"

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

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run deploy.sh first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found!"
    echo "Please copy .env.template to .env and fill in your API keys:"
    echo "   cp .env.template .env"
    echo "   nano .env"
    exit 1
fi

print_status "Starting AI Forex Trading Bot via systemd..."

# Reload systemd daemon to pick up any changes
sudo systemctl daemon-reload

# Start the service
if sudo systemctl start forex-bot; then
    print_success "Bot service started successfully!"
    
    # Wait a moment for the service to fully start
    sleep 2
    
    # Check service status
    if sudo systemctl is-active --quiet forex-bot; then
        print_success "Service is running and active"
        
        # Show service status
        echo ""
        print_status "Service Status:"
        sudo systemctl status forex-bot --no-pager -l
        
        echo ""
        print_status "Recent Logs:"
        sudo journalctl -u forex-bot -n 10 --no-pager
        
        echo ""
        print_success "🎉 Bot is now running! Monitor with: ./monitor_bot.sh"
        
    else
        print_error "Service failed to start properly"
        echo ""
        print_status "Service Status:"
        sudo systemctl status forex-bot --no-pager -l
        exit 1
    fi
    
else
    print_error "Failed to start bot service"
    echo ""
    print_status "Service Status:"
    sudo systemctl status forex-bot --no-pager -l
    exit 1
fi