#!/bin/bash

# AI Forex Trading Bot Environment Setup Script
# Helps configure environment variables for systemd service

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

echo "🔐 AI Forex Trading Bot - Environment Setup"
echo "=========================================="

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

print_status "Setting up environment variables for systemd service..."

# Method 1: Create .env file for local development
if [ ! -f .env ]; then
    print_status "Creating .env file from template..."
    if [ -f .env.template ]; then
        cp .env.template .env
        print_success ".env file created from template"
        print_warning "Please edit .env file with your actual API keys"
    else
        print_error ".env.template not found"
        exit 1
    fi
else
    print_success ".env file already exists"
fi

# Method 2: Set environment variables in systemd service
print_status "Setting up systemd environment variables..."

# Create a drop-in directory for environment variables
sudo mkdir -p /etc/systemd/system/forex-bot.service.d

# Create environment file
sudo tee /etc/systemd/system/forex-bot.service.d/env.conf > /dev/null << EOF
[Service]
# Environment variables will be loaded from .env file
EnvironmentFile=$(pwd)/.env
EOF

print_success "Systemd environment configuration created"

# Reload systemd daemon
sudo systemctl daemon-reload

print_success "Environment setup completed!"
echo ""
print_status "Next steps:"
echo "1. Edit the .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Start the bot:"
echo "   ./start_bot.sh"
echo ""
print_warning "Note: The systemd service will automatically load environment variables from the .env file"