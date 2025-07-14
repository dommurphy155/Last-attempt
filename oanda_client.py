import requests
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from config import OANDA_API_KEY, OANDA_ACCOUNT_ID
from telegram_bot import log_error, log_action

logger = logging.getLogger(__name__)

class OandaClient:
    def __init__(self):
        self.api_key = OANDA_API_KEY
        self.account_id = OANDA_ACCOUNT_ID
        self.base_url = "https://api-fxpractice.oanda.com"  # Demo account
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
        # Validate connection
        self._validate_connection()
    
    def _validate_connection(self):
        """Validate OANDA API connection"""
        try:
            response = self.session.get(f"{self.base_url}/v3/accounts/{self.account_id}")
            if response.status_code == 200:
                logger.info("OANDA API connection validated")
                log_action("OANDA API connection established")
            else:
                logger.error(f"OANDA API validation failed: {response.status_code}")
                log_error("OANDA API validation failed", {"status_code": response.status_code})
        except Exception as e:
            logger.error(f"OANDA API connection error: {e}")
            log_error("OANDA API connection error", {"error": str(e)})
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            response = self.session.get(f"{self.base_url}/v3/accounts/{self.account_id}")
            if validate_api_response(response):
                data = response.json()
                return {
                    "balance": float(data['account']['balance']),
                    "currency": data['account']['currency'],
                    "margin_rate": float(data['account']['marginRate']),
                    "unrealized_pnl": float(data['account']['unrealizedPL']),
                    "realized_pnl": float(data['account']['realizedPL'])
                }
            return {}
        except Exception as e:
            log_error("Failed to get account info", {"error": str(e)})
            return {}
    
    def get_instruments(self) -> List[str]:
        """Get available instruments"""
        try:
            response = self.session.get(f"{self.base_url}/v3/accounts/{self.account_id}/instruments")
            if validate_api_response(response):
                data = response.json()
                return [instrument['name'] for instrument in data['instruments']]
            return []
        except Exception as e:
            log_error("Failed to get instruments", {"error": str(e)})
            return []
    
    def get_prices(self, instruments: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get current prices for instruments"""
        try:
            params = {
                'instruments': ','.join(instruments)
            }
            response = self.session.get(f"{self.base_url}/v3/accounts/{self.account_id}/pricing", params=params)
            
            if validate_api_response(response):
                data = response.json()
                prices = {}
                
                for price in data['prices']:
                    instrument = price['instrument']
                    prices[instrument] = {
                        'bid': float(price['bids'][0]['price']),
                        'ask': float(price['asks'][0]['price']),
                        'timestamp': price['time']
                    }
                
                return prices
            return {}
        except Exception as e:
            log_error("Failed to get prices", {"error": str(e)})
            return {}
    
    def get_candles(self, instrument: str, granularity: str = "M5", count: int = 100) -> Dict[str, List[float]]:
        """Get candlestick data"""
        try:
            params = {
                'granularity': granularity,
                'count': count
            }
            response = self.session.get(f"{self.base_url}/v3/instruments/{instrument}/candles", params=params)
            
            if validate_api_response(response):
                data = response.json()
                candles = {
                    'open': [],
                    'high': [],
                    'low': [],
                    'close': [],
                    'volume': []
                }
                
                for candle in data['candles']:
                    if candle['complete']:
                        candles['open'].append(float(candle['mid']['o']))
                        candles['high'].append(float(candle['mid']['h']))
                        candles['low'].append(float(candle['mid']['l']))
                        candles['close'].append(float(candle['mid']['c']))
                        candles['volume'].append(int(candle['volume']))
                
                return candles
            return {}
        except Exception as e:
            log_error("Failed to get candles", {"error": str(e), "instrument": instrument})
            return {}
    
    def place_order(self, instrument: str, units: int, side: str, 
                   stop_loss: Optional[float] = None, take_profit: Optional[float] = None) -> Dict[str, Any]:
        """Place a market order"""
        try:
            order_data = {
                "order": {
                    "type": "MARKET",
                    "instrument": instrument,
                    "units": str(units),
                    "side": side.upper()
                }
            }
            
            if stop_loss:
                order_data["order"]["stopLossOnFill"] = {
                    "price": str(stop_loss)
                }
            
            if take_profit:
                order_data["order"]["takeProfitOnFill"] = {
                    "price": str(take_profit)
                }
            
            response = self.session.post(f"{self.base_url}/v3/accounts/{self.account_id}/orders", 
                                       json=order_data)
            
            if validate_api_response(response):
                data = response.json()
                order_info = {
                    "order_id": data['orderFillTransaction']['id'],
                    "instrument": instrument,
                    "units": units,
                    "side": side,
                    "price": float(data['orderFillTransaction']['price']),
                    "timestamp": data['orderFillTransaction']['time']
                }
                
                log_action("Order placed successfully", order_info)
                return order_info
            else:
                log_error("Failed to place order", {"instrument": instrument, "units": units, "side": side})
                return {}
                
        except Exception as e:
            log_error("Order placement error", {"error": str(e), "instrument": instrument})
            return {}
    
    def close_position(self, instrument: str, units: Optional[int] = None) -> Dict[str, Any]:
        """Close a position"""
        try:
            # Get current positions
            positions = self.get_positions()
            
            for position in positions:
                if position['instrument'] == instrument:
                    close_units = units if units else abs(position['units'])
                    
                    # Determine side (opposite of current position)
                    side = "sell" if position['units'] > 0 else "buy"
                    
                    order_data = {
                        "order": {
                            "type": "MARKET",
                            "instrument": instrument,
                            "units": str(-close_units if side == "sell" else close_units),
                            "side": side.upper()
                        }
                    }
                    
                    response = self.session.post(f"{self.base_url}/v3/accounts/{self.account_id}/orders", 
                                               json=order_data)
                    
                    if validate_api_response(response):
                        data = response.json()
                        close_info = {
                            "position_id": position['id'],
                            "instrument": instrument,
                            "units_closed": close_units,
                            "price": float(data['orderFillTransaction']['price']),
                            "timestamp": data['orderFillTransaction']['time']
                        }
                        
                        log_action("Position closed successfully", close_info)
                        return close_info
            
            log_error("No position found to close", {"instrument": instrument})
            return {}
            
        except Exception as e:
            log_error("Position close error", {"error": str(e), "instrument": instrument})
            return {}
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        try:
            response = self.session.get(f"{self.base_url}/v3/accounts/{self.account_id}/positions")
            
            if validate_api_response(response):
                data = response.json()
                positions = []
                
                for position in data['positions']:
                    if float(position['long']['units']) != 0 or float(position['short']['units']) != 0:
                        # Determine which side has units
                        if float(position['long']['units']) > 0:
                            units = float(position['long']['units'])
                            side = "long"
                            unrealized_pnl = float(position['long']['unrealizedPL'])
                        else:
                            units = float(position['short']['units'])
                            side = "short"
                            unrealized_pnl = float(position['short']['unrealizedPL'])
                        
                        positions.append({
                            'id': position['instrument'],
                            'instrument': position['instrument'],
                            'units': units,
                            'side': side,
                            'unrealized_pnl': unrealized_pnl
                        })
                
                return positions
            return []
            
        except Exception as e:
            log_error("Failed to get positions", {"error": str(e)})
            return []
    
    def get_trades(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent trades"""
        try:
            params = {'count': count}
            response = self.session.get(f"{self.base_url}/v3/accounts/{self.account_id}/trades", params=params)
            
            if validate_api_response(response):
                data = response.json()
                trades = []
                
                for trade in data['trades']:
                    trades.append({
                        'id': trade['id'],
                        'instrument': trade['instrument'],
                        'units': float(trade['currentUnits']),
                        'price': float(trade['price']),
                        'unrealized_pnl': float(trade['unrealizedPL']),
                        'realized_pnl': float(trade['realizedPL']),
                        'state': trade['state']
                    })
                
                return trades
            return []
            
        except Exception as e:
            log_error("Failed to get trades", {"error": str(e)})
            return []
    
    def calculate_position_size(self, account_balance: float, risk_percentage: float, 
                              stop_loss_pips: int, instrument: str) -> float:
        """Calculate position size based on risk management"""
        try:
            # Get current price
            prices = self.get_prices([instrument])
            if not prices or instrument not in prices:
                return 0.01  # Minimum position size
            
            current_price = prices[instrument]['ask']
            
            # Calculate pip value (simplified)
            if 'JPY' in instrument:
                pip_value = 0.01
            else:
                pip_value = 0.0001
            
            # Calculate risk amount
            risk_amount = account_balance * (risk_percentage / 100)
            
            # Calculate position size
            position_size = risk_amount / (stop_loss_pips * pip_value)
            
            # Ensure minimum and maximum limits
            min_size = 0.01
            max_size = account_balance * 0.1  # Max 10% of account
            
            return max(min_size, min(position_size, max_size))
            
        except Exception as e:
            log_error("Position size calculation error", {"error": str(e)})
            return 0.01
    
    def get_spread(self, instrument: str) -> float:
        """Get current spread for instrument"""
        try:
            prices = self.get_prices([instrument])
            if instrument in prices:
                bid = prices[instrument]['bid']
                ask = prices[instrument]['ask']
                return ask - bid
            return 0.0
        except Exception as e:
            log_error("Spread calculation error", {"error": str(e)})
            return 0.0
    
    def is_spread_acceptable(self, instrument: str, max_spread_pips: float = 5.0) -> bool:
        """Check if spread is acceptable for trading"""
        try:
            spread = self.get_spread(instrument)
            
            # Convert to pips
            if 'JPY' in instrument:
                spread_pips = spread * 100
            else:
                spread_pips = spread * 10000
            
            return spread_pips <= max_spread_pips
            
        except Exception as e:
            log_error("Spread check error", {"error": str(e)})
            return False
    
    def get_account_summary(self) -> str:
        """Get human-readable account summary"""
        try:
            account_info = self.get_account_info()
            positions = self.get_positions()
            
            summary = f"💰 Account Summary\n"
            summary += f"Balance: ${account_info.get('balance', 0):.2f}\n"
            summary += f"Unrealized P&L: ${account_info.get('unrealized_pnl', 0):.2f}\n"
            summary += f"Realized P&L: ${account_info.get('realized_pnl', 0):.2f}\n"
            summary += f"Open Positions: {len(positions)}\n"
            
            if positions:
                summary += "\n📊 Open Positions:\n"
                for pos in positions:
                    pnl_emoji = "💰" if pos['unrealized_pnl'] > 0 else "💸"
                    summary += f"{pnl_emoji} {pos['instrument']}: {pos['units']} units (${pos['unrealized_pnl']:.2f})\n"
            
            return summary
            
        except Exception as e:
            return f"❌ Account summary error: {str(e)}"