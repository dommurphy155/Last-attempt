import asyncio
import time
import threading
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import signal
import sys

from config import (
    TRADING_PAIRS, NEWS_SCRAPE_INTERVAL, PRICE_SCAN_INTERVAL, 
    HEARTBEAT_INTERVAL, LOG_CLEANUP_INTERVAL, validate_config,
    load_state, save_state, get_default_state
)
from utils import log_action, log_error, cleanup_old_logs, calculate_confidence_score
from oanda_client import OandaClient
from technical_analysis import TechnicalAnalyzer
from news_sentiment import NewsSentimentAnalyzer
from telegram_bot import TelegramBot

logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.is_running = False
        self.state = load_state()
        self.oanda_client = None
        self.technical_analyzer = None
        self.news_analyzer = None
        self.telegram_bot = None
        
        # Performance tracking
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.last_trade_time = None
        self.consecutive_losses = 0
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all bot components"""
        try:
            # Validate configuration
            validate_config()
            
            # Initialize OANDA client
            self.oanda_client = OandaClient()
            
            # Initialize technical analyzer
            self.technical_analyzer = TechnicalAnalyzer()
            
            # Initialize news sentiment analyzer
            self.news_analyzer = NewsSentimentAnalyzer()
            
            # Initialize Telegram bot
            self.telegram_bot = TelegramBot(
                self.oanda_client, 
                self.technical_analyzer, 
                self.news_analyzer
            )
            
            log_action("Trading bot components initialized successfully")
            
        except Exception as e:
            log_error("Failed to initialize trading bot components", {"error": str(e)})
            raise
    
    def start(self):
        """Start the trading bot"""
        try:
            self.is_running = True
            log_action("Trading bot started")
            
            # Start main trading loop
            self._run_trading_loop()
            
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            log_error("Trading bot start error", {"error": str(e)})
            self.stop()
    
    def stop(self):
        """Stop the trading bot"""
        try:
            self.is_running = False
            log_action("Trading bot stopping...")
            
            # Close all positions
            if self.oanda_client:
                try:
                    positions = self.oanda_client.get_positions()
                    for position in positions:
                        self.oanda_client.close_position(position['instrument'])
                except Exception as e:
                    log_error("Error closing positions during shutdown", {"error": str(e)})
            
            # Save final state
            try:
                save_state(self.state)
            except Exception as e:
                log_error("Error saving state during shutdown", {"error": str(e)})
            
            log_action("Trading bot stopped successfully")
            
        except Exception as e:
            log_error("Error stopping trading bot", {"error": str(e)})
    
    async def stop_async(self):
        """Stop the trading bot (async version)"""
        try:
            self.is_running = False
            log_action("Trading bot stopping (async)...")
            
            # Close all positions
            if self.oanda_client:
                try:
                    positions = self.oanda_client.get_positions()
                    for position in positions:
                        self.oanda_client.close_position(position['instrument'])
                except Exception as e:
                    log_error("Error closing positions during async shutdown", {"error": str(e)})
            
            # Save final state
            try:
                save_state(self.state)
            except Exception as e:
                log_error("Error saving state during async shutdown", {"error": str(e)})
            
            log_action("Trading bot stopped successfully (async)")
            
        except Exception as e:
            log_error("Error stopping trading bot (async)", {"error": str(e)})
    
    def _start_telegram_bot(self):
        """Start Telegram bot polling"""
        try:
            if self.telegram_bot:
                # Create a new event loop for the Telegram bot thread
                import threading
                
                def run_telegram_bot():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self.telegram_bot.start_polling())
                    except Exception as e:
                        log_error("Telegram bot thread error", {"error": str(e)})
                
                # Start Telegram bot in a separate thread
                telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
                telegram_thread.start()
                
        except Exception as e:
            log_error("Telegram bot start error", {"error": str(e)})
    
    def _run_trading_loop(self):
        """Main trading loop (synchronous version)"""
        log_action("Starting main trading loop")
        
        # Schedule periodic tasks
        schedule.every(NEWS_SCRAPE_INTERVAL).seconds.do(self._scrape_news)
        schedule.every(PRICE_SCAN_INTERVAL).seconds.do(self._scan_prices)
        schedule.every(HEARTBEAT_INTERVAL).seconds.do(self._send_heartbeat)
        schedule.every(LOG_CLEANUP_INTERVAL).seconds.do(self._cleanup_logs)
        
        # Schedule daily reset
        schedule.every().day.at("00:00").do(self._daily_reset)
        
        while self.is_running:
            try:
                # Run scheduled tasks
                schedule.run_pending()
                
                # Check for trading opportunities
                if self._should_trade():
                    self._execute_trading_strategy()
                
                # Small delay to prevent excessive CPU usage
                time.sleep(1)
                
            except Exception as e:
                log_error("Trading loop error", {"error": str(e)})
                time.sleep(5)  # Wait before retrying
    
    async def _run_trading_loop_async(self):
        """Main trading loop (async version)"""
        log_action("Starting async main trading loop")
        
        # Track last execution times for periodic tasks
        last_news_scrape = 0
        last_price_scan = 0
        last_heartbeat = 0
        last_cleanup = 0
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # Run periodic tasks based on intervals
                if current_time - last_news_scrape >= NEWS_SCRAPE_INTERVAL:
                    await self._scrape_news_async()
                    last_news_scrape = current_time
                
                if current_time - last_price_scan >= PRICE_SCAN_INTERVAL:
                    await self._scan_prices_async()
                    last_price_scan = current_time
                
                if current_time - last_heartbeat >= HEARTBEAT_INTERVAL:
                    await self._send_heartbeat_async()
                    last_heartbeat = current_time
                
                if current_time - last_cleanup >= LOG_CLEANUP_INTERVAL:
                    await self._cleanup_logs_async()
                    last_cleanup = current_time
                
                # Check for trading opportunities
                if self._should_trade():
                    await self._execute_trading_strategy_async()
                
                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                log_action("Async trading loop cancelled")
                break
            except Exception as e:
                log_error("Async trading loop error", {"error": str(e)})
                await asyncio.sleep(5)  # Wait before retrying
    
    def _should_trade(self) -> bool:
        """Check if we should trade based on various conditions"""
        try:
            # Check if trading is enabled
            if not self.state.get('is_trading', True):
                return False
            
            # Check daily trade limit
            if self.daily_trades >= 15:
                return False
            
            # Check consecutive losses
            if self.consecutive_losses >= 3:
                log_action("Trading paused due to consecutive losses")
                return False
            
            # Check if we're in a high-impact news period
            if self.news_analyzer.should_avoid_trading():
                return False
            
            # Check time-based restrictions
            now = datetime.utcnow()
            hour = now.hour
            
            # Avoid trading during low-liquidity hours
            if hour < 2 or hour > 22:
                return False
            
            # Check if enough time has passed since last trade
            if self.last_trade_time:
                time_since_last_trade = (now - self.last_trade_time).total_seconds()
                if time_since_last_trade < 300:  # 5 minutes minimum between trades
                    return False
            
            return True
            
        except Exception as e:
            log_error("Error checking trade conditions", {"error": str(e)})
            return False
    
    def _execute_trading_strategy(self):
        """Execute the main trading strategy"""
        try:
            # Get account information
            account_info = self.oanda_client.get_account_info()
            if not account_info or account_info.get('balance', 0) < 100:
                return
            
            # Get current prices for all trading pairs
            prices = self.oanda_client.get_prices(TRADING_PAIRS)
            if not prices:
                return
            
            # Analyze each pair for trading opportunities
            best_opportunity = None
            best_confidence = 0.0
            
            for pair in TRADING_PAIRS:
                if pair not in prices:
                    continue
                
                # Check spread
                if not self.oanda_client.is_spread_acceptable(pair):
                    continue
                
                # Get candlestick data
                candles = self.oanda_client.get_candles(pair)
                if not candles or len(candles.get('close', [])) < 50:
                    continue
                
                # Perform technical analysis
                technical_analysis = self.technical_analyzer.get_comprehensive_analysis(candles)
                
                # Get news sentiment
                sentiment_analysis = self.news_analyzer.analyze_news_sentiment()
                
                # Calculate overall confidence
                technical_confidence = technical_analysis.get('confidence', 0.0)
                sentiment_score = abs(sentiment_analysis.get('score', 0.0))
                
                # Combine technical and sentiment analysis
                overall_confidence = calculate_confidence_score(
                    technical_confidence, sentiment_score, 0.5
                )
                
                # Check if this is a good opportunity
                if (overall_confidence > best_confidence and 
                    overall_confidence > 0.6 and 
                    technical_analysis.get('signal') != 'neutral'):
                    
                    best_confidence = overall_confidence
                    best_opportunity = {
                        'pair': pair,
                        'signal': technical_analysis.get('signal'),
                        'confidence': overall_confidence,
                        'price': prices[pair]['ask'],
                        'technical_analysis': technical_analysis,
                        'sentiment_analysis': sentiment_analysis
                    }
            
            # Execute trade if we found a good opportunity
            if best_opportunity and best_confidence > 0.7:
                self._execute_trade(best_opportunity)
            
        except Exception as e:
            log_error("Trading strategy execution error", {"error": str(e)})
    
    async def _execute_trading_strategy_async(self):
        """Execute the main trading strategy (async version)"""
        try:
            # Get account information
            account_info = self.oanda_client.get_account_info()
            if not account_info or account_info.get('balance', 0) < 100:
                return
            
            # Get current prices for all trading pairs
            prices = self.oanda_client.get_prices(TRADING_PAIRS)
            if not prices:
                return
            
            # Analyze each pair for trading opportunities
            best_opportunity = None
            best_confidence = 0.0
            
            for pair in TRADING_PAIRS:
                if pair not in prices:
                    continue
                
                # Check spread
                if not self.oanda_client.is_spread_acceptable(pair):
                    continue
                
                # Get candlestick data
                candles = self.oanda_client.get_candles(pair)
                if not candles or len(candles.get('close', [])) < 50:
                    continue
                
                # Perform technical analysis
                technical_analysis = self.technical_analyzer.get_comprehensive_analysis(candles)
                
                # Get news sentiment
                sentiment_analysis = self.news_analyzer.analyze_news_sentiment()
                
                # Calculate overall confidence
                technical_confidence = technical_analysis.get('confidence', 0.0)
                sentiment_score = abs(sentiment_analysis.get('score', 0.0))
                
                # Combine technical and sentiment analysis
                overall_confidence = calculate_confidence_score(
                    technical_confidence, sentiment_score, 0.5
                )
                
                # Check if this is a good opportunity
                if (overall_confidence > best_confidence and 
                    overall_confidence > 0.6 and 
                    technical_analysis.get('signal') != 'neutral'):
                    
                    best_confidence = overall_confidence
                    best_opportunity = {
                        'pair': pair,
                        'signal': technical_analysis.get('signal'),
                        'confidence': overall_confidence,
                        'price': prices[pair]['ask'],
                        'technical_analysis': technical_analysis,
                        'sentiment_analysis': sentiment_analysis
                    }
            
            # Execute trade if we found a good opportunity
            if best_opportunity and best_confidence > 0.7:
                await self._execute_trade_async(best_opportunity)
            
        except Exception as e:
            log_error("Async trading strategy execution error", {"error": str(e)})
    
    def _execute_trade(self, opportunity: Dict[str, Any]):
        """Execute a trade based on the opportunity"""
        try:
            pair = opportunity['pair']
            signal = opportunity['signal']
            confidence = opportunity['confidence']
            price = opportunity['price']
            
            # Get account info for position sizing
            account_info = self.oanda_client.get_account_info()
            balance = account_info.get('balance', 0)
            
            # Calculate position size
            position_size = self.oanda_client.calculate_position_size(
                balance, 2.0, 50, pair
            )
            
            # Determine trade direction and units
            if signal == "buy":
                units = position_size
                side = "buy"
            elif signal == "sell":
                units = -position_size
                side = "sell"
            else:
                return
            
            # Place the order
            order_result = self.oanda_client.place_order(pair, units, side)
            
            if order_result:
                # Update tracking variables
                self.daily_trades += 1
                self.last_trade_time = datetime.now()
                
                # Log the trade
                trade_info = {
                    'pair': pair,
                    'side': side,
                    'units': units,
                    'price': price,
                    'confidence': confidence,
                    'timestamp': datetime.now().isoformat()
                }
                
                log_action("Trade executed", trade_info)
                
                # Send Telegram notification
                if self.telegram_bot:
                    try:
                        # Create a new event loop for the notification
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self.telegram_bot.send_trade_alert(trade_info))
                        loop.close()
                    except Exception as e:
                        log_error("Failed to send trade alert", {"error": str(e)})
                
                # Update state
                self.state['trades'].append(trade_info)
                save_state(self.state)
            
        except Exception as e:
            log_error("Trade execution error", {"error": str(e)})
    
    async def _execute_trade_async(self, opportunity: Dict[str, Any]):
        """Execute a trade based on the opportunity (async version)"""
        try:
            pair = opportunity['pair']
            signal = opportunity['signal']
            confidence = opportunity['confidence']
            price = opportunity['price']
            
            # Get account info for position sizing
            account_info = self.oanda_client.get_account_info()
            balance = account_info.get('balance', 0)
            
            # Calculate position size
            position_size = self.oanda_client.calculate_position_size(
                balance, 2.0, 50, pair
            )
            
            # Determine trade direction and units
            if signal == "buy":
                units = position_size
                side = "buy"
            elif signal == "sell":
                units = -position_size
                side = "sell"
            else:
                return
            
            # Place the order
            order_result = self.oanda_client.place_order(pair, units, side)
            
            if order_result:
                # Update tracking variables
                self.daily_trades += 1
                self.last_trade_time = datetime.now()
                
                # Log the trade
                trade_info = {
                    'pair': pair,
                    'side': side,
                    'units': units,
                    'price': price,
                    'confidence': confidence,
                    'timestamp': datetime.now().isoformat()
                }
                
                log_action("Async trade executed", trade_info)
                
                # Send Telegram notification
                if self.telegram_bot:
                    await self.telegram_bot.send_trade_alert(trade_info)
                
                # Update state
                self.state['trades'].append(trade_info)
                save_state(self.state)
            
        except Exception as e:
            log_error("Async trade execution error", {"error": str(e)})
    
    def _scrape_news(self):
        """Scrape and analyze news"""
        try:
            log_action("Starting news scraping")
            sentiment_result = self.news_analyzer.analyze_news_sentiment()
            
            # Update state with sentiment
            self.state['sentiment_scores'] = sentiment_result
            self.state['last_news_scrape'] = datetime.now().isoformat()
            save_state(self.state)
            
            log_action("News scraping completed", sentiment_result)
            
        except Exception as e:
            log_error("News scraping error", {"error": str(e)})
    
    async def _scrape_news_async(self):
        """Scrape and analyze news (async version)"""
        try:
            log_action("Starting async news scraping")
            sentiment_result = self.news_analyzer.analyze_news_sentiment()
            
            # Update state with sentiment
            self.state['sentiment_scores'] = sentiment_result
            self.state['last_news_scrape'] = datetime.now().isoformat()
            save_state(self.state)
            
            log_action("Async news scraping completed", sentiment_result)
            
        except Exception as e:
            log_error("Async news scraping error", {"error": str(e)})
    
    def _scan_prices(self):
        """Scan market prices"""
        try:
            log_action("Starting price scan")
            
            # Get current prices
            prices = self.oanda_client.get_prices(TRADING_PAIRS)
            
            # Update state
            self.state['last_price_scan'] = datetime.now().isoformat()
            save_state(self.state)
            
            log_action("Price scan completed", {"pairs_scanned": len(prices)})
            
        except Exception as e:
            log_error("Price scan error", {"error": str(e)})
    
    async def _scan_prices_async(self):
        """Scan market prices (async version)"""
        try:
            log_action("Starting async price scan")
            
            # Get current prices
            prices = self.oanda_client.get_prices(TRADING_PAIRS)
            
            # Update state
            self.state['last_price_scan'] = datetime.now().isoformat()
            save_state(self.state)
            
            log_action("Async price scan completed", {"pairs_scanned": len(prices)})
            
        except Exception as e:
            log_error("Async price scan error", {"error": str(e)})
    
    def _send_heartbeat(self):
        """Send heartbeat to Telegram"""
        try:
            if self.telegram_bot:
                heartbeat_message = f"💓 Bot Heartbeat - {datetime.now().strftime('%H:%M:%S')}"
                try:
                    # Create a new event loop for the notification
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.telegram_bot.send_notification(heartbeat_message))
                    loop.close()
                except Exception as e:
                    log_error("Failed to send heartbeat", {"error": str(e)})
            
            self.state['last_heartbeat'] = datetime.now().isoformat()
            save_state(self.state)
            
        except Exception as e:
            log_error("Heartbeat error", {"error": str(e)})
    
    async def _send_heartbeat_async(self):
        """Send heartbeat to Telegram (async version)"""
        try:
            if self.telegram_bot:
                heartbeat_message = f"💓 Bot Heartbeat - {datetime.now().strftime('%H:%M:%S')}"
                await self.telegram_bot.send_notification(heartbeat_message)
            
            self.state['last_heartbeat'] = datetime.now().isoformat()
            save_state(self.state)
            
        except Exception as e:
            log_error("Async heartbeat error", {"error": str(e)})
    
    def _cleanup_logs(self):
        """Clean up old log files"""
        try:
            cleanup_old_logs()
            log_action("Log cleanup completed")
        except Exception as e:
            log_error("Log cleanup error", {"error": str(e)})
    
    async def _cleanup_logs_async(self):
        """Clean up old log files (async version)"""
        try:
            cleanup_old_logs()
            log_action("Async log cleanup completed")
        except Exception as e:
            log_error("Async log cleanup error", {"error": str(e)})
    
    def _daily_reset(self):
        """Reset daily counters"""
        try:
            self.daily_trades = 0
            self.daily_pnl = 0.0
            self.consecutive_losses = 0
            
            log_action("Daily reset completed")
            
        except Exception as e:
            log_error("Daily reset error", {"error": str(e)})
    
    def _update_performance_metrics(self, trade_result: Dict[str, Any]):
        """Update performance metrics after a trade"""
        try:
            pnl = trade_result.get('pnl', 0)
            
            # Update daily P&L
            self.daily_pnl += pnl
            
            # Update consecutive losses
            if pnl < 0:
                self.consecutive_losses += 1
            else:
                self.consecutive_losses = 0
            
            # Update win rate
            if pnl > 0:
                self.state['win_count'] = self.state.get('win_count', 0) + 1
            else:
                self.state['loss_count'] = self.state.get('loss_count', 0) + 1
            
            # Update total P&L
            self.state['total_pnl'] = self.state.get('total_pnl', 0) + pnl
            
            save_state(self.state)
            
        except Exception as e:
            log_error("Performance metrics update error", {"error": str(e)})

async def async_main():
    """Async main entry point"""
    bot = None
    tasks = []
    try:
        # Create and start the trading bot
        bot = TradingBot()
        main.bot = bot  # Store reference for signal handler
        
        log_action("Starting trading bot in async mode")
        
        # Start the bot
        bot.is_running = True
        
        # Start Telegram bot polling in the main event loop
        if bot.telegram_bot:
            log_action("Starting Telegram bot polling")
            # Start Telegram bot polling as a background task
            telegram_task = asyncio.create_task(bot.telegram_bot.start_polling())
            tasks.append(telegram_task)
        
        # Start main trading loop as a background task
        log_action("Starting async trading loop")
        trading_task = asyncio.create_task(bot._run_trading_loop_async())
        tasks.append(trading_task)
        
        # Wait for all tasks to complete (they should run indefinitely)
        if tasks:
            log_action(f"Running {len(tasks)} async tasks")
            await asyncio.gather(*tasks, return_exceptions=True)
        else:
            log_action("No async tasks available, falling back to synchronous mode")
            # Fallback to synchronous trading loop if no async tasks
            bot._run_trading_loop()
        
    except asyncio.CancelledError:
        log_action("Async main cancelled")
        # Cancel all running tasks
        for task in tasks:
            if not task.done():
                task.cancel()
        # Wait for tasks to complete cancellation
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        if bot:
            await bot.stop_async()
    except Exception as e:
        logger.error(f"Async main error: {e}")
        log_error("Async main application error", {"error": str(e)})
        # Cancel all running tasks
        for task in tasks:
            if not task.done():
                task.cancel()
        # Wait for tasks to complete cancellation
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        if bot:
            await bot.stop_async()
        raise

def main():
    """Main entry point"""
    try:
        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received shutdown signal {signum}")
            log_action(f"Shutdown signal received: {signum}")
            # Graceful shutdown - set the bot to stop
            if hasattr(main, 'bot') and main.bot:
                main.bot.is_running = False
            # The async loop will handle the actual shutdown
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGHUP, signal_handler)  # For systemd reload
        
        log_action("Starting trading bot application")
        
        # Run the async main function - this will block until completion
        asyncio.run(async_main())
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        log_action("Application stopped by keyboard interrupt")
        if hasattr(main, 'bot') and main.bot:
            main.bot.is_running = False
    except Exception as e:
        logger.error(f"Main error: {e}")
        log_error("Main application error", {"error": str(e)})
        if hasattr(main, 'bot') and main.bot:
            main.bot.is_running = False
        sys.exit(1)

if __name__ == "__main__":
    main()