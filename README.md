# AI Forex Trading Bot

A sophisticated AI-powered forex trading bot that combines technical analysis, news sentiment analysis, and machine learning to make automated trading decisions.

## Features

- 🤖 **AI-Powered Analysis**: Combines technical indicators with news sentiment analysis
- 📊 **Technical Analysis**: RSI, MACD, EMA, ATR, Fibonacci levels, support/resistance
- 📰 **News Sentiment**: Real-time news scraping and sentiment analysis
- 💬 **Telegram Integration**: Full bot control and monitoring via Telegram
- 🔄 **Async Architecture**: High-performance async/await implementation
- 🛡️ **Risk Management**: Comprehensive risk controls and position sizing
- 📈 **Performance Tracking**: Detailed trade history and performance metrics
- 🔧 **Health Monitoring**: Built-in health checks and automatic recovery

## Quick Start

### 1. Prerequisites

- Python 3.8+
- Ubuntu 20.04+ (recommended)
- OANDA demo account
- Telegram bot token

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-forex-trading-bot

# Create & activate venv
python3 -m venv venv
source venv/bin/activate

# Upgrade pip & install pinned deps
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuration

Set your credentials in the shell (no .env file):

```bash
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token_here"
export TELEGRAM_CHAT_ID="your_telegram_chat_id_here"
export OANDA_API_KEY="your_oanda_api_key_here"
export OANDA_ACCOUNT_ID="your_oanda_account_id_here"
```

### 4. Test Installation

```bash
# Syntax check all .py files
for f in *.py; do python3 -m py_compile "$f" || { echo "❌ Syntax error in $f"; exit 1; }; done

# Import test all modules
for f in *.py; do mod="${f%.py}"; python3 -c "import $mod" || { echo "❌ Import error in $mod"; exit 1; }; done
```

### 5. Start the Bot

```bash
# Start via systemd (recommended)
sudo systemctl start forex-bot.service

# Or run directly
python3 bot_runner.py
```

## Architecture

### Core Components

- **`bot_runner.py`**: Main entry point with health monitoring and error recovery
- **`trading_bot.py`**: Core trading logic and strategy implementation
- **`oanda_client.py`**: OANDA API integration for trading operations
- **`technical_analysis.py`**: Technical indicators and pattern recognition
- **`news_sentiment.py`**: News scraping and sentiment analysis
- **`telegram_bot.py`**: Telegram bot interface for monitoring and control
- **`config.py`**: Configuration management and validation
- **`utils.py`**: Utility functions and logging

### Async Architecture

The bot uses Python's asyncio for high-performance concurrent operations:

- **Independent Tasks**: News scraping, price monitoring, and trading run concurrently
- **Health Monitoring**: Continuous health checks with automatic recovery
- **Graceful Shutdown**: Proper cleanup and position management on exit

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize the bot |
| `/status` | Full diagnostic report |
| `/maketrade` | Execute a real-time trade |
| `/whatyoudoin` | Show current bot activity |
| `/canceltrade` | Close all positions |
| `/showlog` | Recent activity log |
| `/togglemode` | Switch trading modes |
| `/resetbot` | Reset bot state |
| `/pnl` | Profit/Loss summary |
| `/openpositions` | Show open positions |
| `/strategystats` | Strategy performance |

## Risk Management

- **Position Sizing**: Maximum 10% of account per trade
- **Stop Loss**: Automatic 50-pip stop loss
- **Take Profit**: 100-pip take profit targets
- **Daily Limits**: Maximum 15 trades per day
- **Loss Streak Protection**: Pause trading after 3 consecutive losses
- **Emergency Shutdown**: Auto-stop at -10% P&L

## Monitoring & Maintenance

### Health Checks

The bot includes comprehensive health monitoring:

- **Connection Monitoring**: OANDA API and Telegram connectivity
- **Performance Tracking**: Trade success rates and P&L
- **Error Recovery**: Automatic restart on critical failures
- **Resource Monitoring**: Memory and CPU usage

### Logs

- **Trading Log**: All trades and decisions
- **Error Log**: Error tracking and debugging
- **System Log**: System-level events

### Backup

```bash
# Create backup
./backup_bot.sh

# Restore from backup
cp -r backups/YYYYMMDD_HHMMSS/* .
```

## Deployment

### Systemd Service

The bot runs as a systemd service for reliability:

```bash
# Service management
sudo systemctl start forex-bot
sudo systemctl stop forex-bot
sudo systemctl status forex-bot
sudo systemctl enable forex-bot  # Auto-start on boot
```

### Docker (Alternative)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "bot_runner.py"]
```

## Configuration

### Trading Parameters

Edit `config.py` to customize:

- **Trading Pairs**: Default forex pairs to trade
- **Risk Settings**: Position sizes and stop losses
- **Technical Indicators**: RSI, MACD, EMA periods
- **News Sources**: Sources for sentiment analysis
- **Time Intervals**: Scraping and monitoring frequencies

### Performance Tuning

- **Aggressive Mode**: Higher risk, more frequent trades
- **Safe Mode**: Conservative approach with higher confidence thresholds
- **Custom Strategies**: Implement your own trading logic

## Troubleshooting

### Common Issues

1. **Import Errors**: Run `pip install -r requirements.txt`
2. **API Connection**: Verify API keys in `.env`
3. **Permission Errors**: Check file permissions and user access
4. **Service Won't Start**: Check logs with `journalctl -u forex-bot`

### Debug Mode

```bash
# Run with debug logging
python3 bot_runner.py --debug

# Check specific component
python3 -c "import oanda_client; print('OANDA client OK')"
```

## Security

- **API Key Protection**: Store keys in environment variables (never in code or .env files)
- **Network Security**: Use HTTPS for all API communications
- **Access Control**: Restrict bot access to authorized users
- **Audit Logging**: Complete audit trail of all actions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Trading forex involves substantial risk of loss. Use at your own risk. The authors are not responsible for any financial losses incurred through the use of this software.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details