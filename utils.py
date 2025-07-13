import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from config import LOG_FILE, ERROR_LOG_FILE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_action(action: str, details: Dict[str, Any] = None, level: str = "INFO"):
    """Log an action with details"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details or {},
        "level": level
    }
    
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        logger.error(f"Failed to log action: {e}")

def log_error(error: str, context: Dict[str, Any] = None):
    """Log an error with context"""
    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "error": error,
        "context": context or {}
    }
    
    try:
        with open(ERROR_LOG_FILE, 'a') as f:
            f.write(json.dumps(error_entry) + '\n')
    except Exception as e:
        logger.error(f"Failed to log error: {e}")

def get_recent_logs(count: int = 20) -> List[Dict[str, Any]]:
    """Get recent log entries"""
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            recent_logs = []
            for line in lines[-count:]:
                try:
                    recent_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
            return recent_logs
    except FileNotFoundError:
        return []

def calculate_win_rate(wins: int, losses: int) -> float:
    """Calculate win rate percentage"""
    total = wins + losses
    return round((wins / total * 100), 2) if total > 0 else 0.0

def calculate_pnl_percentage(initial_balance: float, current_balance: float) -> float:
    """Calculate P&L percentage"""
    if initial_balance == 0:
        return 0.0
    return ((current_balance - initial_balance) / initial_balance) * 100

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    return f"{amount:.2f} {currency}"

def format_percentage(value: float) -> str:
    """Format percentage value"""
    return f"{value:.2f}%"

def get_current_session() -> str:
    """Get current market session"""
    now = datetime.utcnow()
    hour = now.hour
    
    if 0 <= hour < 8:
        return "Asia"
    elif 8 <= hour < 16:
        return "London"
    elif 13 <= hour < 21:
        return "New York"
    else:
        return "Off Hours"

def is_high_impact_time() -> bool:
    """Check if current time is during high-impact news events"""
    now = datetime.utcnow()
    # Avoid trading during major news releases (simplified)
    return False  # Placeholder - implement actual logic

def calculate_position_size(account_balance: float, risk_percentage: float, stop_loss_pips: int, pip_value: float) -> float:
    """Calculate position size based on risk management"""
    risk_amount = account_balance * (risk_percentage / 100)
    position_size = risk_amount / (stop_loss_pips * pip_value)
    return max(0.01, min(position_size, account_balance * 0.1))  # Min 0.01, max 10% of balance

def validate_api_response(response: requests.Response) -> bool:
    """Validate API response"""
    if response.status_code == 200:
        return True
    elif response.status_code == 429:
        log_error("Rate limit exceeded", {"status_code": 429})
        time.sleep(60)  # Wait 1 minute
        return False
    elif response.status_code >= 500:
        log_error("Server error", {"status_code": response.status_code})
        time.sleep(30)  # Wait 30 seconds
        return False
    else:
        log_error(f"API error: {response.status_code}", {"response": response.text})
        return False

def retry_on_failure(func, max_retries: int = 3, delay: float = 1.0):
    """Retry function on failure with exponential backoff"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    log_error(f"Function {func.__name__} failed after {max_retries} attempts", {"error": str(e)})
                    raise
                time.sleep(delay * (2 ** attempt))
        return None
    return wrapper

def sanitize_text(text: str) -> str:
    """Sanitize text for processing"""
    if not text:
        return ""
    # Remove HTML tags and special characters
    import re
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
    return text.strip()

def extract_currency_pairs(text: str) -> List[str]:
    """Extract currency pairs from text"""
    import re
    pairs = re.findall(r'[A-Z]{3}/[A-Z]{3}|[A-Z]{3}_[A-Z]{3}', text.upper())
    return list(set(pairs))

def calculate_confidence_score(technical_score: float, sentiment_score: float, volatility_score: float) -> float:
    """Calculate overall confidence score"""
    # Weighted average of different factors
    weights = {
        "technical": 0.4,
        "sentiment": 0.3,
        "volatility": 0.3
    }
    
    confidence = (
        technical_score * weights["technical"] +
        sentiment_score * weights["sentiment"] +
        volatility_score * weights["volatility"]
    )
    
    return max(0.0, min(1.0, confidence))

def format_trade_summary(trade: Dict[str, Any]) -> str:
    """Format trade summary for Telegram"""
    emoji_map = {
        "buy": "🟢",
        "sell": "🔴",
        "profit": "💰",
        "loss": "💸",
        "neutral": "⚪"
    }
    
    direction_emoji = emoji_map.get(trade.get("direction", "").lower(), "⚪")
    result_emoji = emoji_map.get("profit" if trade.get("pnl", 0) > 0 else "loss", "⚪")
    
    summary = f"{direction_emoji} {trade.get('pair', 'N/A')} {trade.get('direction', 'N/A').upper()}\n"
    summary += f"Entry: {trade.get('entry_price', 'N/A')}\n"
    summary += f"Exit: {trade.get('exit_price', 'N/A')}\n"
    summary += f"P&L: {result_emoji} {format_currency(trade.get('pnl', 0))}\n"
    summary += f"Confidence: {format_percentage(trade.get('confidence', 0) * 100)}"
    
    return summary

def cleanup_old_logs(max_age_hours: int = 24):
    """Clean up old log entries"""
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    
    # Clean up main log
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
        
        recent_lines = []
        for line in lines:
            try:
                log_entry = json.loads(line.strip())
                log_time = datetime.fromisoformat(log_entry.get("timestamp", ""))
                if log_time > cutoff_time:
                    recent_lines.append(line)
            except (json.JSONDecodeError, ValueError):
                continue
        
        with open(LOG_FILE, 'w') as f:
            f.writelines(recent_lines)
    except FileNotFoundError:
        pass
    
    # Clean up error log
    try:
        with open(ERROR_LOG_FILE, 'r') as f:
            lines = f.readlines()
        
        recent_lines = []
        for line in lines:
            try:
                log_entry = json.loads(line.strip())
                log_time = datetime.fromisoformat(log_entry.get("timestamp", ""))
                if log_time > cutoff_time:
                    recent_lines.append(line)
            except (json.JSONDecodeError, ValueError):
                continue
        
        with open(ERROR_LOG_FILE, 'w') as f:
            f.writelines(recent_lines)
    except FileNotFoundError:
        pass