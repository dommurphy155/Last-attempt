#!/bin/bash

# AI Forex Trading Bot Deployment Script with PM2
# For Ubuntu 20.04+ with Python 3.8+

set -e  # Exit on any error

echo "🤖 AI Forex Trading Bot - PM2 Deployment Script"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

print_status "Starting PM2 deployment..."

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv git curl wget

# Install PM2 globally
print_status "Installing PM2..."
sudo npm install -g pm2

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_status "Python version: $PYTHON_VERSION"

# Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Test installation
print_status "Testing installation..."
python test_installation.py

if [ $? -eq 0 ]; then
    print_success "Installation test passed!"
else
    print_error "Installation test failed!"
    exit 1
fi

# Create necessary directories
print_status "Creating log directories..."
mkdir -p logs
mkdir -p data

# Create PM2 ecosystem file
print_status "Creating PM2 ecosystem file..."
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'forex-bot',
    script: 'trading_bot.py',
    interpreter: './venv/bin/python',
    cwd: process.cwd(),
    env: {
      NODE_ENV: 'production',
      PYTHONPATH: process.cwd()
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    log_file: './logs/combined.log',
    out_file: './logs/out.log',
    error_file: './logs/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    time: true
  }]
}
EOF

# Create startup script
print_status "Creating startup script..."
cat > start_bot.sh << 'EOF'
#!/bin/bash

# AI Forex Trading Bot Startup Script (PM2)

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please ensure .env file exists with your API keys"
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

# Start the bot with PM2
echo "🤖 Starting AI Forex Trading Bot with PM2..."
pm2 start ecosystem.config.js

echo "✅ Bot started with PM2!"
echo "📊 Check status: pm2 status"
echo "📝 View logs: pm2 logs forex-bot"
EOF

chmod +x start_bot.sh

# Create stop script
print_status "Creating stop script..."
cat > stop_bot.sh << 'EOF'
#!/bin/bash

# AI Forex Trading Bot Stop Script (PM2)

echo "🛑 Stopping AI Forex Trading Bot..."

# Stop PM2 process
pm2 stop forex-bot 2>/dev/null || true
pm2 delete forex-bot 2>/dev/null || true

echo "✅ Bot stopped"
EOF

chmod +x stop_bot.sh

# Create status script
print_status "Creating status script..."
cat > status_bot.sh << 'EOF'
#!/bin/bash

# AI Forex Trading Bot Status Script (PM2)

echo "📊 AI Forex Trading Bot Status"
echo "=============================="

# Check PM2 status
pm2 status

echo ""
echo "📝 Recent Logs:"
pm2 logs forex-bot --lines 10 2>/dev/null || echo "No logs found"
EOF

chmod +x status_bot.sh

# Create monitoring script
print_status "Creating monitoring script..."
cat > monitor_bot.sh << 'EOF'
#!/bin/bash

# AI Forex Trading Bot Monitoring Script (PM2)

echo "🔍 AI Forex Trading Bot Monitor"
echo "==============================="

while true; do
    clear
    echo "$(date)"
    echo "==============================="
    
    # Show PM2 status
    pm2 status
    
    # Show recent logs
    echo ""
    echo "📝 Recent Logs:"
    pm2 logs forex-bot --lines 5 2>/dev/null || echo "No logs found"
    
    echo ""
    echo "Press Ctrl+C to exit"
    sleep 5
done
EOF

chmod +x monitor_bot.sh

# Create restart script
print_status "Creating restart script..."
cat > restart_bot.sh << 'EOF'
#!/bin/bash

# AI Forex Trading Bot Restart Script (PM2)

echo "🔄 Restarting AI Forex Trading Bot..."

# Restart PM2 process
pm2 restart forex-bot 2>/dev/null || pm2 start ecosystem.config.js

echo "✅ Bot restarted"
EOF

chmod +x restart_bot.sh

# Create backup script
print_status "Creating backup script..."
cat > backup_bot.sh << 'EOF'
#!/bin/bash

# AI Forex Trading Bot Backup Script

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "💾 Creating backup in $BACKUP_DIR..."

# Backup important files
cp -r *.py "$BACKUP_DIR/"
cp -r *.json "$BACKUP_DIR/" 2>/dev/null || true
cp -r *.log "$BACKUP_DIR/" 2>/dev/null || true
cp requirements.txt "$BACKUP_DIR/"
cp README.md "$BACKUP_DIR/"
cp ecosystem.config.js "$BACKUP_DIR/"

echo "✅ Backup created: $BACKUP_DIR"
EOF

chmod +x backup_bot.sh

# Create PM2 startup script
print_status "Setting up PM2 startup..."
pm2 startup

print_success "PM2 deployment completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Ensure .env file exists with your API keys"
echo "2. Test the installation:"
echo "   python test_installation.py"
echo ""
echo "3. Start the bot:"
echo "   ./start_bot.sh"
echo ""
echo "4. Monitor the bot:"
echo "   ./monitor_bot.sh"
echo ""
echo "5. Check status:"
echo "   ./status_bot.sh"
echo ""
echo "6. Stop the bot:"
echo "   ./stop_bot.sh"
echo ""
echo "7. Restart the bot:"
echo "   ./restart_bot.sh"
echo ""
echo "📚 Available Scripts:"
echo "   start_bot.sh    - Start the trading bot with PM2"
echo "   stop_bot.sh     - Stop the trading bot"
echo "   restart_bot.sh  - Restart the trading bot"
echo "   status_bot.sh   - Check bot status"
echo "   monitor_bot.sh  - Real-time monitoring"
echo "   backup_bot.sh   - Create backup"
echo ""
echo "🔧 PM2 Commands:"
echo "   pm2 status              - Check all processes"
echo "   pm2 logs forex-bot      - View bot logs"
echo "   pm2 restart forex-bot   - Restart bot"
echo "   pm2 stop forex-bot      - Stop bot"
echo "   pm2 delete forex-bot    - Remove bot from PM2"
echo "   pm2 save                - Save current PM2 configuration"
echo "   pm2 startup             - Configure PM2 to start on boot"
echo ""
print_success "🎉 AI Forex Trading Bot is ready to use with PM2!"