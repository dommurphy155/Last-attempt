#!/bin/bash

# AI Forex Trading Bot Cleanup Script
# Removes unnecessary files and optimizes for production

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

echo "🧹 AI Forex Trading Bot - Cleanup Script"
echo "======================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

print_status "Starting cleanup process..."

# Remove any existing log files (they'll be handled by journald)
print_status "Cleaning up log files..."
rm -f *.log 2>/dev/null || true
rm -f logs/*.log 2>/dev/null || true

# Remove any temporary files
print_status "Cleaning up temporary files..."
rm -f *.tmp 2>/dev/null || true
rm -f *.bak 2>/dev/null || true
rm -f *.swp 2>/dev/null || true

# Remove any Python cache files
print_status "Cleaning up Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Remove any backup directories (keep only the latest)
print_status "Cleaning up old backups..."
if [ -d "backups" ]; then
    # Keep only the 5 most recent backups
    cd backups
    ls -t | tail -n +6 | xargs rm -rf 2>/dev/null || true
    cd ..
fi

# Clean up any orphaned state files (optional)
print_status "Checking state files..."
if [ -f "bot_state.json" ]; then
    SIZE=$(stat -c%s "bot_state.json" 2>/dev/null || echo "0")
    if [ $SIZE -gt 1048576 ]; then  # 1MB
        print_warning "bot_state.json is large (${SIZE} bytes), consider backing up and resetting"
    fi
fi

# Optimize git repository
print_status "Optimizing git repository..."
if [ -d ".git" ]; then
    git gc --aggressive --prune=now 2>/dev/null || true
fi

# Set proper permissions
print_status "Setting proper permissions..."
chmod +x *.sh 2>/dev/null || true
chmod 644 *.py 2>/dev/null || true
chmod 644 *.md 2>/dev/null || true
chmod 644 *.txt 2>/dev/null || true

# Create necessary directories if they don't exist
print_status "Creating necessary directories..."
mkdir -p logs 2>/dev/null || true
mkdir -p data 2>/dev/null || true
mkdir -p backups 2>/dev/null || true

print_success "Cleanup completed successfully!"
echo ""
print_status "Repository is now optimized for production deployment"
print_status "All unnecessary files have been removed"
print_status "Logs will be handled by systemd journald"