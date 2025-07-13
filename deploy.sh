#!/bin/bash

# AI Forex Trading Bot Deployment Script
# For Ubuntu 20.04 with Python 3.8.10

set -e  # Exit on any error

echo "🤖 AI Forex Trading Bot - Deployment Script"
echo "=========================================="

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

# Check Ubuntu version
UBUNTU_VERSION=$(lsb_release -rs)
if [[ "$UBUNTU_VERSION" != "20.04" && "$UBUNTU_VERSION" != "22.04" ]]; then
    print_warning "This script is designed for Ubuntu 20.04/22.04. You're running Ubuntu $UBUNTU_VERSION"
fi

print_status "Starting deployment..."

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv git curl wget

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

# Set up environment variables template
print_status "Creating environment variables template..."
cat > .env.template << EOF
# AI Forex Trading Bot Environment Variables
# Copy this file to .env and fill in your actual values

# Hugging Face API Key for sentiment analysis
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# OANDA API Configuration
OANDA_API_KEY=your_oanda_api_key_here
OANDA_ACCOUNT_ID=your_oanda_account_id_here
EOF

# Create systemd service file
print_status "Creating systemd service file..."
sudo tee /etc/systemd/system/forex-bot.service > /dev/null << EOF
[Unit]
Description=AI Forex Trading Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python trading_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create startup script
print_status "Creating startup script..."
cat > start_bot.sh << 'EOF'
#!/bin/bash

# AI Forex Trading Bot Startup Script

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.template to .env and fill in your API keys"
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

# Start the bot
echo "🤖 Starting AI Forex Trading Bot..."
python trading_bot.py
EOF

chmod +x start_bot.sh

# Create stop script
print_status "Creating stop script..."
cat > stop_bot.sh << 'EOF'
#!/bin/bash

# AI Forex Trading Bot Stop Script

echo "🛑 Stopping AI Forex Trading Bot..."

# Stop systemd service if running
sudo systemctl stop forex-bot 2>/dev/null || true

# Kill any running bot processes
pkill -f "python trading_bot.py" 2>/dev/null || true

echo "✅ Bot stopped"
EOF

chmod +x stop_bot.sh

# Create status script
print_status "Creating status script..."
cat > status_bot.sh << 'EOF'
#!/bin/bash

# AI Forex Trading Bot Status Script

echo "📊 AI Forex Trading Bot Status"
echo "=============================="

# Check if service is running
if systemctl is-active --quiet forex-bot; then
    echo "✅ Service: RUNNING"
else
    echo "❌ Service: STOPPED"
fi

# Check if process is running
if pgrep -f "python trading_bot.py" > /dev/null; then
    echo "✅ Process: RUNNING"
else
    echo "❌ Process: STOPPED"
fi

# Show recent logs
echo ""
echo "📝 Recent Logs:"
tail -n 10 trading_bot.log 2>/dev/null || echo "No logs found"
EOF

chmod +x status_bot.sh

# Create monitoring script
print_status "Creating monitoring script..."
cat > monitor_bot.sh << 'EOF'
#!/bin/bash

# AI Forex Trading Bot Monitoring Script

echo "🔍 AI Forex Trading Bot Monitor"
echo "==============================="

while true; do
    clear
    echo "$(date)"
    echo "==============================="
    
    # Check service status
    if systemctl is-active --quiet forex-bot; then
        echo "✅ Service: RUNNING"
    else
        echo "❌ Service: STOPPED"
    fi
    
    # Check process
    if pgrep -f "python trading_bot.py" > /dev/null; then
        echo "✅ Process: RUNNING"
        PID=$(pgrep -f "python trading_bot.py")
        echo "📊 PID: $PID"
        
        # Show memory usage
        MEMORY=$(ps -o rss= -p $PID 2>/dev/null | awk '{print $1/1024 " MB"}' || echo "N/A")
        echo "💾 Memory: $MEMORY"
    else
        echo "❌ Process: STOPPED"
    fi
    
    # Show recent logs
    echo ""
    echo "📝 Recent Logs:"
    tail -n 5 trading_bot.log 2>/dev/null || echo "No logs found"
    
    echo ""
    echo "Press Ctrl+C to exit"
    sleep 5
done
EOF

chmod +x monitor_bot.sh

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

echo "✅ Backup created: $BACKUP_DIR"
EOF

chmod +x backup_bot.sh

print_success "Deployment completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy .env.template to .env and fill in your API keys:"
echo "   cp .env.template .env"
echo "   nano .env"
echo ""
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
echo "📚 Available Scripts:"
echo "   start_bot.sh    - Start the trading bot"
echo "   stop_bot.sh     - Stop the trading bot"
echo "   status_bot.sh   - Check bot status"
echo "   monitor_bot.sh  - Real-time monitoring"
echo "   backup_bot.sh   - Create backup"
echo ""
echo "🔧 Systemd Service:"
echo "   sudo systemctl start forex-bot    - Start as service"
echo "   sudo systemctl stop forex-bot     - Stop service"
echo "   sudo systemctl status forex-bot   - Check service status"
echo "   sudo systemctl enable forex-bot   - Enable auto-start"
echo ""
print_success "🎉 AI Forex Trading Bot is ready to use!"