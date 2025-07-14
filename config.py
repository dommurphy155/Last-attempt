import os
import json
from datetime import datetime, timedelta

# API Keys and Tokens
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")

# Trading Configuration
TRADING_PAIRS = [
    "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD", 
    "USD_CAD", "NZD_USD", "EUR_GBP", "EUR_JPY", "GBP_JPY"
]

# Risk Management
MAX_TRADES_PER_DAY = 15
MIN_TRADES_PER_DAY = 5
MAX_LOSS_STREAK = 3
MIN_WIN_RATE = 0.60
MAX_POSITION_SIZE = 0.1  # 10% of account
STOP_LOSS_PIPS = 50
TAKE_PROFIT_PIPS = 100
TRAILING_STOP = True

# Technical Analysis
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
EMA_FAST = 12
EMA_SLOW = 26
ATR_PERIOD = 14

# News and Sentiment
NEWS_SOURCES = [
    "https://www.reuters.com/markets/currencies",
    "https://www.bloomberg.com/markets/currencies",
    "https://www.investing.com/news/forex-news",
    "https://www.fxstreet.com/news",
    "https://www.dailyfx.com/news",
    "https://tradingeconomics.com/calendar",
    "https://www.forexfactory.com/forum",
    "https://www.babypips.com/forum",
    "https://www.reddit.com/r/Forex",
    "https://finance.yahoo.com/currencies",
    "https://www.marketwatch.com/investing/currency",
    "https://seekingalpha.com/symbol/FX",
    "https://www.cnbc.com/forex",
    "https://www.zacks.com/forex",
    "https://www.investingcube.com",
    "https://www.benzinga.com/forex",
    "https://www.forexlive.com",
    "https://www.ig.com/uk/forex/news",
    "https://www.ft.com/currencies"
]

SENTIMENT_MODELS = [
    "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "ProsusAI/finbert",
    "microsoft/DialoGPT-medium",
    "distilbert-base-uncased",
    "bert-base-uncased"
]

# Time Intervals
NEWS_SCRAPE_INTERVAL = 12 * 60  # 12 minutes
PRICE_SCAN_INTERVAL = 7  # 7 seconds
HEARTBEAT_INTERVAL = 5 * 60  # 5 minutes
LOG_CLEANUP_INTERVAL = 60 * 60  # 1 hour

# Market Sessions (UTC)
ASIA_SESSION = {"start": "00:00", "end": "08:00"}
LONDON_SESSION = {"start": "08:00", "end": "16:00"}
NY_SESSION = {"start": "13:00", "end": "21:00"}

# Telegram Commands
TELEGRAM_COMMANDS = {
    "/status": "Full diagnostic: trades, win/loss, P&L, open positions, news impact, predictions",
    "/maketrade": "Places a real-time, ROI-optimized trade and schedules exit automatically",
    "/whatyoudoin": "Shows current action: scraping, scanning, idle, trading, etc.",
    "/canceltrade": "Instantly closes all open positions and halts trading",
    "/showlog": "Sends the last 20 actions (trades, signals, scrapes, errors)",
    "/togglemode": "Switch between aggressive/safe trading logic",
    "/resetbot": "Fully resets state, restarts AI models and loops",
    "/pnl": "Instantly return profit/loss",
    "/openpositions": "Show all open positions",
    "/strategystats": "Strategy performance summary"
}

# File Paths
STATE_FILE = "bot_state.json"
LOG_FILE = "trading_log.json"
ERROR_LOG_FILE = "error_log.json"

# Performance Thresholds
MAX_LATENCY_MS = 1000
EMERGENCY_SHUTDOWN_LOSS = -0.10  # -10% P&L
MIN_CONFIDENCE_SCORE = 0.60
ULTRA_SAFE_CONFIDENCE = 0.80

# News Keywords for Volatility Detection
VOLATILITY_KEYWORDS = [
    "fed", "ecb", "boe", "boj", "rba", "boc", "nzd",
    "interest rate", "inflation", "gdp", "employment",
    "trade war", "brexit", "election", "crisis", "recession"
]

# Economic Calendar High-Impact Events
HIGH_IMPACT_EVENTS = [
    "Non-Farm Payrolls", "CPI", "GDP", "Interest Rate Decision",
    "FOMC", "ECB Meeting", "BOE Meeting", "Employment Report"
]

def load_state():
    """Load bot state from JSON file"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return get_default_state()

def save_state(state):
    """Save bot state to JSON file"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, default=str)

def get_default_state():
    """Get default bot state"""
    return {
        "trades": [],
        "open_positions": [],
        "total_pnl": 0.0,
        "win_count": 0,
        "loss_count": 0,
        "current_mode": "aggressive",
        "last_news_scrape": None,
        "last_price_scan": None,
        "last_heartbeat": None,
        "is_trading": True,
        "strategy_performance": {},
        "sentiment_scores": {},
        "error_count": 0,
        "start_time": datetime.now().isoformat(),
        "session_trades": 0,
        "daily_pnl": 0.0
    }

def validate_config():
    """Validate all required environment variables are set"""
    required_vars = [
        "TELEGRAM_BOT_TOKEN", 
        "TELEGRAM_CHAT_ID",
        "OANDA_API_KEY",
        "OANDA_ACCOUNT_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    return True