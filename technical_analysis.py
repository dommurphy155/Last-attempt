import ta
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from config import (
    RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    EMA_FAST, EMA_SLOW, ATR_PERIOD
)

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    def __init__(self):
        self.indicators = {}
        self.patterns = {}
        
    def calculate_rsi(self, prices: List[float], period: int = RSI_PERIOD) -> float:
        """Calculate RSI indicator (lightweight)"""
        try:
            if len(prices) < period + 1:
                return 50.0  # Neutral RSI if insufficient data
            import pandas as pd
            series = pd.Series(prices)
            rsi = ta.momentum.RSIIndicator(series, window=period)
            return float(rsi.rsi().iloc[-1])
        except Exception as e:
            logger.error(f"RSI calculation error: {e}")
            return 50.0
    
    def calculate_macd(self, prices: List[float]) -> Tuple[float, float, float]:
        """Calculate MACD indicator (lightweight)"""
        try:
            if len(prices) < MACD_SLOW + 1:
                return 0.0, 0.0, 0.0
            import pandas as pd
            series = pd.Series(prices)
            macd = ta.trend.MACD(series, window_fast=MACD_FAST, window_slow=MACD_SLOW, window_sign=MACD_SIGNAL)
            macd_line = float(macd.macd().iloc[-1])
            signal_line = float(macd.macd_signal().iloc[-1])
            histogram = float(macd.macd_diff().iloc[-1])
            return macd_line, signal_line, histogram
        except Exception as e:
            logger.error(f"MACD calculation error: {e}")
            return 0.0, 0.0, 0.0
    
    def calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate EMA indicator (lightweight)"""
        try:
            if len(prices) < period:
                return prices[-1] if prices else 0.0
            import pandas as pd
            series = pd.Series(prices)
            ema = ta.trend.EMAIndicator(series, window=period)
            return float(ema.ema_indicator().iloc[-1])
        except Exception as e:
            logger.error(f"EMA calculation error: {e}")
            return prices[-1] if prices else 0.0
    
    def calculate_atr(self, high: List[float], low: List[float], close: List[float], period: int = ATR_PERIOD) -> float:
        """Calculate ATR indicator (lightweight)"""
        try:
            if len(high) < period or len(low) < period or len(close) < period:
                return 0.0
            import pandas as pd
            df = pd.DataFrame({
                'high': high,
                'low': low,
                'close': close
            })
            atr = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=period)
            return float(atr.average_true_range().iloc[-1])
        except Exception as e:
            logger.error(f"ATR calculation error: {e}")
            return 0.0
    
    def detect_rsi_breakout(self, rsi_values: List[float]) -> Dict[str, any]:
        """Detect RSI breakout signals"""
        if len(rsi_values) < 3:
            return {"signal": "neutral", "strength": 0.0}
        
        current_rsi = rsi_values[-1]
        prev_rsi = rsi_values[-2]
        
        # Oversold breakout
        if prev_rsi < RSI_OVERSOLD and current_rsi > RSI_OVERSOLD:
            strength = min((current_rsi - RSI_OVERSOLD) / 20, 1.0)
            return {"signal": "buy", "strength": strength}
        
        # Overbought breakdown
        elif prev_rsi > RSI_OVERBOUGHT and current_rsi < RSI_OVERBOUGHT:
            strength = min((RSI_OVERBOUGHT - current_rsi) / 20, 1.0)
            return {"signal": "sell", "strength": strength}
        
        return {"signal": "neutral", "strength": 0.0}
    
    def detect_macd_divergence(self, prices: List[float], macd_values: List[float]) -> Dict[str, any]:
        """Detect MACD divergence"""
        if len(prices) < 10 or len(macd_values) < 10:
            return {"signal": "neutral", "strength": 0.0}
        
        # Simple divergence detection
        price_trend = prices[-1] - prices[-5]
        macd_trend = macd_values[-1] - macd_values[-5]
        
        # Bullish divergence: price down, MACD up
        if price_trend < 0 and macd_trend > 0:
            strength = min(abs(macd_trend) / 0.01, 1.0)
            return {"signal": "buy", "strength": strength}
        
        # Bearish divergence: price up, MACD down
        elif price_trend > 0 and macd_trend < 0:
            strength = min(abs(macd_trend) / 0.01, 1.0)
            return {"signal": "sell", "strength": strength}
        
        return {"signal": "neutral", "strength": 0.0}
    
    def calculate_fibonacci_levels(self, high: float, low: float) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels"""
        diff = high - low
        return {
            "0.236": high - 0.236 * diff,
            "0.382": high - 0.382 * diff,
            "0.500": high - 0.500 * diff,
            "0.618": high - 0.618 * diff,
            "0.786": high - 0.786 * diff
        }
    
    def detect_support_resistance(self, prices: List[float], window: int = 20) -> Dict[str, List[float]]:
        """Detect support and resistance levels"""
        if len(prices) < window:
            return {"support": [], "resistance": []}
        
        recent_prices = prices[-window:]
        support_levels = []
        resistance_levels = []
        
        for i in range(1, len(recent_prices) - 1):
            if recent_prices[i] < recent_prices[i-1] and recent_prices[i] < recent_prices[i+1]:
                support_levels.append(recent_prices[i])
            elif recent_prices[i] > recent_prices[i-1] and recent_prices[i] > recent_prices[i+1]:
                resistance_levels.append(recent_prices[i])
        
        return {
            "support": sorted(list(set(support_levels))),
            "resistance": sorted(list(set(resistance_levels)))
        }
    
    def detect_candle_patterns(self, open_prices: List[float], high_prices: List[float], 
                             low_prices: List[float], close_prices: List[float]) -> Dict[str, any]:
        """Detect candlestick patterns"""
        if len(open_prices) < 3:
            return {"pattern": "none", "signal": "neutral", "strength": 0.0}
        
        # Get last 3 candles
        o1, o2, o3 = open_prices[-3:]
        h1, h2, h3 = high_prices[-3:]
        l1, l2, l3 = low_prices[-3:]
        c1, c2, c3 = close_prices[-3:]
        
        # Pinbar pattern
        body1 = abs(c1 - o1)
        upper_shadow1 = h1 - max(o1, c1)
        lower_shadow1 = min(o1, c1) - l1
        
        if upper_shadow1 > 2 * body1 and lower_shadow1 < body1:
            return {"pattern": "pinbar", "signal": "sell", "strength": 0.7}
        elif lower_shadow1 > 2 * body1 and upper_shadow1 < body1:
            return {"pattern": "pinbar", "signal": "buy", "strength": 0.7}
        
        # Engulfing pattern
        body2 = abs(c2 - o2)
        body3 = abs(c3 - o3)
        
        if body3 > body2:
            if c2 > o2 and c3 < o3:  # Bullish engulfing
                return {"pattern": "engulfing", "signal": "buy", "strength": 0.8}
            elif c2 < o2 and c3 > o3:  # Bearish engulfing
                return {"pattern": "engulfing", "signal": "sell", "strength": 0.8}
        
        return {"pattern": "none", "signal": "neutral", "strength": 0.0}
    
    def calculate_heikin_ashi(self, open_prices: List[float], high_prices: List[float], 
                             low_prices: List[float], close_prices: List[float]) -> Dict[str, any]:
        """Calculate Heikin-Ashi candles"""
        if len(open_prices) < 2:
            return {"signal": "neutral", "strength": 0.0}
        
        # Heikin-Ashi formula
        ha_close = (open_prices[-1] + high_prices[-1] + low_prices[-1] + close_prices[-1]) / 4
        ha_open = (open_prices[-2] + close_prices[-2]) / 2
        ha_high = max(high_prices[-1], ha_open, ha_close)
        ha_low = min(low_prices[-1], ha_open, ha_close)
        
        # Determine trend
        if ha_close > ha_open:
            return {"signal": "buy", "strength": 0.6}
        else:
            return {"signal": "sell", "strength": 0.6}
    
    def analyze_volume(self, prices: List[float], volumes: List[float]) -> Dict[str, any]:
        """Analyze volume patterns"""
        if len(prices) < 5 or len(volumes) < 5:
            return {"signal": "neutral", "strength": 0.0}
        
        avg_volume = sum(volumes[-5:]) / 5
        current_volume = volumes[-1]
        price_change = prices[-1] - prices[-2]
        
        # Volume confirmation
        if current_volume > avg_volume * 1.5:
            if price_change > 0:
                return {"signal": "buy", "strength": 0.5}
            else:
                return {"signal": "sell", "strength": 0.5}
        
        return {"signal": "neutral", "strength": 0.0}
    
    def calculate_multi_timeframe_signal(self, timeframe_data: Dict[str, List[float]]) -> Dict[str, any]:
        """Calculate multi-timeframe signal"""
        signals = {"buy": 0, "sell": 0, "neutral": 0}
        total_strength = 0
        
        for timeframe, prices in timeframe_data.items():
            if len(prices) < 20:
                continue
            
            # Calculate RSI for this timeframe
            rsi = self.calculate_rsi(prices)
            
            if rsi < RSI_OVERSOLD:
                signals["buy"] += 1
                total_strength += 0.3
            elif rsi > RSI_OVERBOUGHT:
                signals["sell"] += 1
                total_strength += 0.3
            else:
                signals["neutral"] += 1
        
        # Determine overall signal
        if signals["buy"] > signals["sell"] and signals["buy"] > signals["neutral"]:
            return {"signal": "buy", "strength": min(total_strength, 1.0)}
        elif signals["sell"] > signals["buy"] and signals["sell"] > signals["neutral"]:
            return {"signal": "sell", "strength": min(total_strength, 1.0)}
        else:
            return {"signal": "neutral", "strength": 0.0}
    
    def calculate_volatility_score(self, prices: List[float], period: int = 20) -> float:
        """Calculate volatility score"""
        if len(prices) < period:
            return 0.0
        
        import math
        returns = [math.log(prices[i+1] / prices[i]) for i in range(len(prices) - 1)]
        # Calculate standard deviation manually
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = math.sqrt(variance) * math.sqrt(252)  # Annualized
        return min(volatility, 1.0)
    
    def detect_trend_strength(self, prices: List[float], period: int = 20) -> Dict[str, any]:
        """Detect trend strength using ADX-like calculation"""
        if len(prices) < period:
            return {"trend": "neutral", "strength": 0.0}
        
        # Simple trend strength calculation
        price_change = prices[-1] - prices[-period]
        avg_price = sum(prices[-period:]) / period
        strength = abs(price_change) / avg_price
        
        if price_change > 0:
            trend = "uptrend"
        elif price_change < 0:
            trend = "downtrend"
        else:
            trend = "neutral"
        
        return {"trend": trend, "strength": min(strength, 1.0)}
    
    def get_comprehensive_analysis(self, market_data: Dict[str, List[float]]) -> Dict[str, any]:
        """Get comprehensive technical analysis"""
        try:
            prices = market_data.get('close', [])
            highs = market_data.get('high', [])
            lows = market_data.get('low', [])
            opens = market_data.get('open', [])
            volumes = market_data.get('volume', [])
            
            if len(prices) < 50:
                return {"signal": "neutral", "confidence": 0.0, "indicators": {}}
            
            # Calculate indicators
            rsi = self.calculate_rsi(prices)
            macd_line, signal_line, histogram = self.calculate_macd(prices)
            ema_fast = self.calculate_ema(prices, EMA_FAST)
            ema_slow = self.calculate_ema(prices, EMA_SLOW)
            atr = self.calculate_atr(highs, lows, prices)
            
            # Get signals
            rsi_signal = self.detect_rsi_breakout([rsi])
            macd_signal = self.detect_macd_divergence(prices, [macd_line])
            candle_signal = self.detect_candle_patterns(opens, highs, lows, prices)
            ha_signal = self.calculate_heikin_ashi(opens, highs, lows, prices)
            volume_signal = self.analyze_volume(prices, volumes) if volumes else {"signal": "neutral", "strength": 0.0}
            
            # Calculate trend
            trend_analysis = self.detect_trend_strength(prices)
            volatility_score = self.calculate_volatility_score(prices)
            
            # Combine signals
            buy_signals = 0
            sell_signals = 0
            total_strength = 0
            
            signals = [rsi_signal, macd_signal, candle_signal, ha_signal, volume_signal]
            
            for signal in signals:
                if signal["signal"] == "buy":
                    buy_signals += 1
                    total_strength += signal["strength"]
                elif signal["signal"] == "sell":
                    sell_signals += 1
                    total_strength += signal["strength"]
            
            # Determine final signal
            if buy_signals > sell_signals and buy_signals >= 2:
                final_signal = "buy"
                confidence = min(total_strength / len(signals), 1.0)
            elif sell_signals > buy_signals and sell_signals >= 2:
                final_signal = "sell"
                confidence = min(total_strength / len(signals), 1.0)
            else:
                final_signal = "neutral"
                confidence = 0.0
            
            # Adjust confidence based on trend alignment
            if final_signal == "buy" and trend_analysis["trend"] == "uptrend":
                confidence *= 1.2
            elif final_signal == "sell" and trend_analysis["trend"] == "downtrend":
                confidence *= 1.2
            
            return {
                "signal": final_signal,
                "confidence": min(confidence, 1.0),
                "indicators": {
                    "rsi": rsi,
                    "macd": {"line": macd_line, "signal": signal_line, "histogram": histogram},
                    "ema_fast": ema_fast,
                    "ema_slow": ema_slow,
                    "atr": atr,
                    "trend": trend_analysis,
                    "volatility": volatility_score
                },
                "signals": {
                    "rsi": rsi_signal,
                    "macd": macd_signal,
                    "candle": candle_signal,
                    "heikin_ashi": ha_signal,
                    "volume": volume_signal
                }
            }
            
        except Exception as e:
            logger.error(f"Technical analysis error: {e}")
            return {"signal": "neutral", "confidence": 0.0, "indicators": {}}