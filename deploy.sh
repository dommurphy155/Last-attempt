#!/bin/bash

# AI Forex Trading Bot Deployment Script
# For Ubuntu 20.04+ with Python 3.8.10+ and systemd

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

# Check Ubuntu version (if lsb_release is available)
if command -v lsb_release &> /dev/null; then
    UBUNTU_VERSION=$(lsb_release -rs)
    if [[ "$UBUNTU_VERSION" != "20.04" && "$UBUNTU_VERSION" != "22.04" && "$UBUNTU_VERSION" != "24.04" ]]; then
        print_warning "This script is designed for Ubuntu 20.04/22.04/24.04. You're running Ubuntu $UBUNTU_VERSION"
    fi
else
    print_warning "lsb_release not available, skipping Ubuntu version check"
fi

print_status "Starting deployment..."

# Update system packages (skip in container environment)
if [ -f /.dockerenv ] || [ -f /run/.containerenv ]; then
    print_warning "Running in container environment, skipping system package updates"
else
    # Update system packages
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y

    # Install system dependencies
    print_status "Installing system dependencies..."
    sudo apt install -y python3 python3-pip python3-venv git curl wget jq bc
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_status "Python version: $PYTHON_VERSION"

# Create virtual environment (or use system Python in container)
if [ -f /.dockerenv ] || [ -f /run/.containerenv ]; then
    print_warning "Running in container environment, using system Python"
    # Use system Python directly
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    # Create virtual environment
    print_status "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

# Upgrade pip
print_status "Upgrading pip..."
$PIP_CMD install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
$PIP_CMD install -r requirements.txt

# Test installation
print_status "Testing installation..."
$PYTHON_CMD -c "import config; print('✅ Configuration module loaded successfully')"
$PYTHON_CMD -c "import oanda_client; print('✅ OANDA client module loaded successfully')"
$PYTHON_CMD -c "import technical_analysis; print('✅ Technical analysis module loaded successfully')"
$PYTHON_CMD -c "import news_sentiment; print('✅ News sentiment module loaded successfully')"
$PYTHON_CMD -c "import telegram_bot; print('✅ Telegram bot module loaded successfully')"
$PYTHON_CMD -c "import trading_bot; print('✅ Trading bot module loaded successfully')"

print_success "Installation test passed!"

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

# Create systemd service file (skip in container environment)
if [ -f /.dockerenv ] || [ -f /run/.containerenv ]; then
    print_warning "Running in container environment, skipping systemd service creation"
else
    # Create systemd service file
    print_status "Creating systemd service file..."
    sudo tee /etc/systemd/system/forex-bot.service > /dev/null << EOF
[Unit]
Description=AI Forex Trading Bot
Documentation=https://github.com/your-repo/ai-forex-trading-bot
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
Environment=PYTHONPATH=$(pwd)
Environment=PYTHONUNBUFFERED=1
ExecStart=$(pwd)/venv/bin/$PYTHON_CMD trading_bot.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StartLimitBurst=5
StartLimitInterval=60

# Logging configuration
StandardOutput=journal
StandardError=journal
SyslogIdentifier=forex-bot

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$(pwd)/logs $(pwd)/data $(pwd)/bot_state.json $(pwd)/trading_log.json $(pwd)/error_log.json

# Resource limits
LimitNOFILE=65536
MemoryMax=1G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd daemon
    sudo systemctl daemon-reload
    print_success "Systemd service file created and daemon reloaded"
fi

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
echo "   $PYTHON_CMD -c \"import config, oanda_client, technical_analysis, news_sentiment, telegram_bot, trading_bot; print('All modules loaded successfully')\""
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
echo "   start_bot.sh    - Start the trading bot (systemd)"
echo "   stop_bot.sh     - Stop the trading bot (systemd)"
echo "   status_bot.sh   - Check bot status and logs"
echo "   monitor_bot.sh  - Real-time monitoring"
echo "   backup_bot.sh   - Create backup"
echo ""
echo "🔧 Systemd Service:"
echo "   sudo systemctl start forex-bot    - Start as service"
echo "   sudo systemctl stop forex-bot     - Stop service"
echo "   sudo systemctl status forex-bot   - Check service status"
echo "   sudo systemctl enable forex-bot   - Enable auto-start"
echo "   sudo journalctl -u forex-bot -f   - Follow logs"
echo ""
print_success "🎉 AI Forex Trading Bot is ready to use!"