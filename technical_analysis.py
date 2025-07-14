import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._prepare()

    def _prepare(self):
        self.df['ema_fast'] = self.df['close'].ewm(span=12, adjust=False).mean()
        self.df['ema_slow'] = self.df['close'].ewm(span=26, adjust=False).mean()
        self.df['macd'] = self.df['ema_fast'] - self.df['ema_slow']
        self.df['signal'] = self.df['macd'].ewm(span=9, adjust=False).mean()
        delta = self.df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        roll_up = gain.rolling(window=14).mean()
        roll_down = loss.rolling(window=14).mean()
        rs = roll_up / roll_down
        self.df['rsi'] = 100 - (100 / (1 + rs))
        self.df['bb_middle'] = self.df['close'].rolling(window=20).mean()
        self.df['bb_std'] = self.df['close'].rolling(window=20).std()
        self.df['bb_upper'] = self.df['bb_middle'] + 2 * self.df['bb_std']
        self.df['bb_lower'] = self.df['bb_middle'] - 2 * self.df['bb_std']
        tr1 = self.df['high'] - self.df['low']
        tr2 = (self.df['high'] - self.df['close'].shift()).abs()
        tr3 = (self.df['low'] - self.df['close'].shift()).abs()
        self.df['tr'] = np.maximum.reduce([tr1, tr2, tr3])
        self.df['atr'] = self.df['tr'].rolling(window=14).mean()

    def last(self):
        return self.df.iloc[-1]

    def check_signals(self):
        row = self.last()
        buy = (
            row['macd'] > row['signal'] and
            row['rsi'] < 30 and
            row['close'] < row['bb_lower']
        )
        sell = (
            row['macd'] < row['signal'] and
            row['rsi'] > 70 and
            row['close'] > row['bb_upper']
        )
        strength = 0
        strength += 1 if row['macd'] > row['signal'] else -1
        strength += 1 if row['rsi'] < 30 else -1 if row['rsi'] > 70 else 0
        strength += 1 if row['close'] < row['bb_lower'] else -1 if row['close'] > row['bb_upper'] else 0

        return {
            'buy_signal': buy,
            'sell_signal': sell,
            'confidence': min(max((strength + 3) / 6, 0), 1)
        }
