# 🤖 AI Forex Trading Bot

A fully automated AI-powered forex trading bot built for Ubuntu 20.04 with Python 3.8.10. This bot combines advanced technical analysis, real-time news sentiment analysis, and intelligent risk management to execute profitable trades.

## 🚀 Features

### Core Intelligence
- **Advanced Technical Analysis**: RSI, MACD, EMA, ATR, Fibonacci levels, candlestick patterns
- **Real-time News Sentiment**: Scrapes 20+ financial sources with AI-powered sentiment analysis
- **Multi-timeframe Analysis**: Combines signals from different timeframes
- **Risk Management**: Dynamic position sizing, stop-loss, take-profit, and volatility filters

### Trading Capabilities
- **Automated Trading**: Places 5-15 ROI-positive trades per day
- **High Win Rate**: Targets 60%+ win rate with adaptive strategies
- **Real-time Monitoring**: Continuous market scanning every 7 seconds
- **News Integration**: Scrapes financial news every 12 minutes

### Telegram Integration
- **Full Control**: 10+ commands for complete bot management
- **Real-time Alerts**: Trade notifications and status updates
- **Performance Tracking**: P&L, win rate, and strategy statistics
- **Emergency Controls**: Instant position closure and trading halt

## 📋 Requirements

- **OS**: Ubuntu 20.04 or higher
- **Python**: 3.8.10 or higher
- **Memory**: 2GB RAM minimum
- **Storage**: 1GB free space
- **Internet**: Stable connection for API calls

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-forex-trading-bot
```

### 2. Run Deployment Script
```bash
./deploy.sh
```

### 3. Set Up Environment Variables
```bash
./setup_env.sh
nano .env  # Fill in your API keys
```

### 4. Validate Configuration
```bash
python -c "from config import validate_config; validate_config(); print('✅ Configuration valid')"
```

## 🚀 Usage

### Deploy and Start the Bot
```bash
# 1. Run the deployment script
./deploy.sh

# 2. Set up environment variables
cp .env.template .env
nano .env  # Fill in your API keys

# 3. Start the bot as a systemd service
./start_bot.sh

# 4. Monitor the bot
./monitor_bot.sh
```

### Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot and show available commands |
| `/status` | Full diagnostic: trades, P&L, positions, sentiment |
| `/maketrade` | Place a real-time, ROI-optimized trade |
| `/whatyoudoin` | Show current bot activity |
| `/canceltrade` | Close all positions and halt trading |
| `/showlog` | Display last 20 bot actions |
| `/togglemode` | Switch between aggressive/safe trading |
| `/resetbot` | Reset bot state and restart |
| `/pnl` | Show profit/loss summary |
| `/openpositions` | Display all open positions |
| `/strategystats` | Show strategy performance |
| `/help` | Display help information |

## 📊 Trading Strategy

### Technical Analysis
- **RSI Breakout Detection**: Identifies oversold/overbought conditions
- **MACD Divergence**: Detects price/momentum divergences
- **EMA Crossovers**: Fast/slow EMA signal generation
- **Candlestick Patterns**: Pinbar, engulfing, and other patterns
- **Support/Resistance**: Dynamic level detection
- **Volume Analysis**: Volume confirmation for breakouts

### Sentiment Analysis
- **Multi-Source Scraping**: 20+ financial news sources
- **AI-Powered Analysis**: Multiple Hugging Face models
- **Volatility Detection**: Keyword-based volatility scoring
- **Currency Pair Impact**: Forex-specific sentiment analysis

### Risk Management
- **Dynamic Position Sizing**: Based on account balance and volatility
- **Spread Filtering**: Avoids trades with excessive spreads
- **Time-based Restrictions**: Avoids low-liquidity hours
- **Consecutive Loss Protection**: Pauses trading after 3 losses
- **News Blackout**: Avoids trading during high-impact news

## 🔐 Security

- **API Key Protection**: Environment variables only
- **Demo Account**: Uses OANDA demo for testing
- **Error Handling**: Comprehensive error logging and recovery
- **State Persistence**: JSON-based state management
- **Graceful Shutdown**: Proper cleanup on exit

## 📈 Performance Features

### 30 Profit-Maximizing Upgrades
- RSI breakout detector
- MACD divergence + convergence
- Fibonacci retracement filter
- EMA cross with candle confirm
- Heikin-Ashi momentum alignment
- ATR-based SL/TP calibration
- Dynamic lot sizing
- Multi-timeframe confluence
- Time-of-day optimization
- Entry delay for breakout validation

### 20 Stability & Self-Learning Features
- Win-rate live tracking
- Loss-streak auto-throttle
- Crash-proof loops
- Fallback model rotation
- Heartbeat monitoring
- Time-weighted strategy scoring
- Market condition classifier
- Auto-reset on latency issues
- Trade rationale logging
- JSON flat state file

## 🛠️ Configuration

### Trading Parameters
```python
# config.py
MAX_TRADES_PER_DAY = 15
MIN_TRADES_PER_DAY = 5
MAX_LOSS_STREAK = 3
MIN_WIN_RATE = 0.60
MAX_POSITION_SIZE = 0.1  # 10% of account
STOP_LOSS_PIPS = 50
TAKE_PROFIT_PIPS = 100
```

### Technical Analysis
```python
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
```

### Time Intervals
```python
NEWS_SCRAPE_INTERVAL = 12 * 60  # 12 minutes
PRICE_SCAN_INTERVAL = 7  # 7 seconds
HEARTBEAT_INTERVAL = 5 * 60  # 5 minutes
```

## 📝 Logging

The bot uses systemd journald for comprehensive logging:
- All logs are captured by systemd and can be viewed with `journalctl`
- `trading_log.json`: Structured action log
- `error_log.json`: Error tracking
- `bot_state.json`: Persistent state

### Viewing Logs
```bash
# View all bot logs
sudo journalctl -u forex-bot

# Follow logs in real-time
sudo journalctl -u forex-bot -f

# View recent logs
sudo journalctl -u forex-bot -n 50

# View error logs only
sudo journalctl -u forex-bot -p err
```

## 🔍 Monitoring

### Real-time Monitoring
- Systemd service monitoring with automatic restarts
- Telegram notifications for all trades
- Heartbeat messages every 5 minutes
- Performance metrics tracking
- Error alerting and recovery
- Comprehensive logging via journald

### Service Management
```bash
# Start the service
sudo systemctl start forex-bot

# Stop the service
sudo systemctl stop forex-bot

# Check service status
sudo systemctl status forex-bot

# Enable auto-start on boot
sudo systemctl enable forex-bot

# View real-time logs
sudo journalctl -u forex-bot -f
```

### Performance Metrics
- Win rate calculation
- P&L tracking
- Strategy performance ranking
- Risk-adjusted returns

## 🚨 Troubleshooting

### Common Issues

1. **Service Not Starting**
   ```bash
   # Check service status
   sudo systemctl status forex-bot
   
   # View error logs
   sudo journalctl -u forex-bot -p err
   
   # Check environment variables
   ./status_bot.sh
   ```

2. **API Connection Errors**
   - Verify API keys in `.env` file
   - Check internet connection
   - Ensure OANDA account is active

3. **Telegram Bot Issues**
   - Verify bot token and chat ID
   - Check bot permissions
   - Ensure bot is not blocked

4. **Service Crashes**
   ```bash
   # Check recent logs
   sudo journalctl -u forex-bot -n 50
   
   # Restart service
   sudo systemctl restart forex-bot
   
   # Check for memory issues
   free -h
   ```

5. **Environment Variable Issues**
   ```bash
   # Re-run environment setup
   ./setup_env.sh
   
   # Check if .env file exists
   ls -la .env
   ```

### Debug Mode
```bash
# Run bot directly for debugging
source venv/bin/activate
python trading_bot.py
```

### Health Monitoring
```bash
# Enable health check timer
sudo systemctl enable forex-bot.timer
sudo systemctl start forex-bot.timer

# Check timer status
sudo systemctl status forex-bot.timer
```

## � Available Scripts

| Script | Description |
|--------|-------------|
| `deploy.sh` | Complete deployment script for Ubuntu |
| `setup_env.sh` | Set up environment variables for systemd |
| `start_bot.sh` | Start the bot as systemd service |
| `stop_bot.sh` | Stop the bot service gracefully |
| `status_bot.sh` | Comprehensive status and health check |
| `monitor_bot.sh` | Real-time monitoring with journalctl |
| `backup_bot.sh` | Create backup of bot files |
| `cleanup.sh` | Clean up unnecessary files |

## �📞 Support

For issues and support:
1. Check the logs: `sudo journalctl -u forex-bot`
2. Verify environment variables: `./status_bot.sh`
3. Test API connections individually
4. Review configuration parameters
5. Check service status: `sudo systemctl status forex-bot`

## ⚠️ Disclaimer

This bot is for educational and testing purposes. Trading forex involves substantial risk of loss. Always:
- Test thoroughly on demo accounts
- Start with small position sizes
- Monitor performance closely
- Never risk more than you can afford to lose

## 📄 License

This project is for educational purposes. Use at your own risk.

---

**Built with ❤️ for automated forex trading**