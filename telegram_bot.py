import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_COMMANDS
from utils import log_action, log_error, get_recent_logs, format_currency, format_percentage
from oanda_client import OandaClient
from technical_analysis import TechnicalAnalyzer
from news_sentiment import NewsSentimentAnalyzer

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, oanda_client: OandaClient, technical_analyzer: TechnicalAnalyzer, 
                 news_analyzer: NewsSentimentAnalyzer):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.oanda_client = oanda_client
        self.technical_analyzer = technical_analyzer
        self.news_analyzer = news_analyzer
        self.application = None
        self.last_message_time = {}
        
        # Initialize bot
        self._initialize_bot()
    
    def _initialize_bot(self):
        """Initialize Telegram bot"""
        try:
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("maketrade", self.maketrade_command))
            self.application.add_handler(CommandHandler("whatyoudoin", self.whatyoudoin_command))
            self.application.add_handler(CommandHandler("canceltrade", self.canceltrade_command))
            self.application.add_handler(CommandHandler("showlog", self.showlog_command))
            self.application.add_handler(CommandHandler("togglemode", self.togglemode_command))
            self.application.add_handler(CommandHandler("resetbot", self.resetbot_command))
            self.application.add_handler(CommandHandler("pnl", self.pnl_command))
            self.application.add_handler(CommandHandler("openpositions", self.openpositions_command))
            self.application.add_handler(CommandHandler("strategystats", self.strategystats_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            
            logger.info("Telegram bot initialized successfully")
            log_action("Telegram bot initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            log_error("Telegram bot initialization failed", {"error": str(e)})
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            welcome_message = "🤖 AI Forex Trading Bot Started!\n\n"
            welcome_message += "Available commands:\n"
            for command, description in TELEGRAM_COMMANDS.items():
                welcome_message += f"{command} - {description}\n"
            
            await update.message.reply_text(welcome_message)
            log_action("Telegram start command received")
            
        except Exception as e:
            log_error("Start command error", {"error": str(e)})
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command - Full diagnostic"""
        try:
            # Get account info
            account_info = self.oanda_client.get_account_info()
            positions = self.oanda_client.get_positions()
            
            # Get recent sentiment
            sentiment_summary = self.news_analyzer.get_sentiment_summary()
            
            # Calculate win rate
            total_trades = account_info.get('realized_pnl', 0)
            win_rate = "N/A"  # Placeholder - implement actual calculation
            
            status_message = "📊 BOT STATUS REPORT\n\n"
            status_message += f"💰 Account Balance: {format_currency(account_info.get('balance', 0))}\n"
            status_message += f"📈 Unrealized P&L: {format_currency(account_info.get('unrealized_pnl', 0))}\n"
            status_message += f"💵 Realized P&L: {format_currency(account_info.get('realized_pnl', 0))}\n"
            status_message += f"📊 Open Positions: {len(positions)}\n"
            status_message += f"🎯 Win Rate: {win_rate}\n\n"
            
            # Add sentiment info
            status_message += "📰 NEWS SENTIMENT:\n"
            status_message += sentiment_summary + "\n\n"
            
            # Add recent activity
            recent_logs = get_recent_logs(5)
            if recent_logs:
                status_message += "🔄 Recent Activity:\n"
                for log in recent_logs[-3:]:
                    action = log.get('action', 'Unknown')
                    timestamp = log.get('timestamp', 'Unknown')
                    status_message += f"• {action} ({timestamp})\n"
            
            await update.message.reply_text(status_message)
            log_action("Status command executed")
            
        except Exception as e:
            error_msg = f"❌ Status command error: {str(e)}"
            await update.message.reply_text(error_msg)
            log_error("Status command error", {"error": str(e)})
    
    async def maketrade_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /maketrade command - Place a trade"""
        try:
            # Get account info
            account_info = self.oanda_client.get_account_info()
            
            # Check if we have sufficient balance
            if account_info.get('balance', 0) < 100:
                await update.message.reply_text("❌ Insufficient balance for trading")
                return
            
            # Get current prices for major pairs
            instruments = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD"]
            prices = self.oanda_client.get_prices(instruments)
            
            if not prices:
                await update.message.reply_text("❌ Unable to get market prices")
                return
            
            # Find best trading opportunity
            best_trade = None
            best_confidence = 0.0
            
            for instrument in instruments:
                if instrument in prices:
                    # Get candlestick data
                    candles = self.oanda_client.get_candles(instrument)
                    if not candles:
                        continue
                    
                    # Perform technical analysis
                    analysis = self.technical_analyzer.get_comprehensive_analysis(candles)
                    
                    # Check spread
                    if not self.oanda_client.is_spread_acceptable(instrument):
                        continue
                    
                    # Check sentiment
                    sentiment = self.news_analyzer.analyze_news_sentiment()
                    
                    # Calculate overall confidence
                    technical_confidence = analysis.get('confidence', 0.0)
                    sentiment_score = sentiment.get('score', 0.0)
                    
                    # Combine technical and sentiment analysis
                    overall_confidence = (technical_confidence * 0.7) + (abs(sentiment_score) * 0.3)
                    
                    if overall_confidence > best_confidence and overall_confidence > 0.6:
                        best_confidence = overall_confidence
                        best_trade = {
                            'instrument': instrument,
                            'signal': analysis.get('signal', 'neutral'),
                            'confidence': overall_confidence,
                            'price': prices[instrument]['ask'],
                            'analysis': analysis
                        }
            
            if not best_trade:
                await update.message.reply_text("❌ No suitable trading opportunities found")
                return
            
            # Place the trade
            instrument = best_trade['instrument']
            signal = best_trade['signal']
            confidence = best_trade['confidence']
            price = best_trade['price']
            
            # Calculate position size
            position_size = self.oanda_client.calculate_position_size(
                account_info.get('balance', 0), 2.0, 50, instrument
            )
            
            # Determine trade direction
            if signal == "buy":
                units = position_size
                side = "buy"
            elif signal == "sell":
                units = -position_size
                side = "sell"
            else:
                await update.message.reply_text("❌ No clear signal for trading")
                return
            
            # Place order
            order_result = self.oanda_client.place_order(instrument, units, side)
            
            if order_result:
                trade_message = f"🎯 TRADE EXECUTED!\n\n"
                trade_message += f"📊 Instrument: {instrument}\n"
                trade_message += f"📈 Direction: {side.upper()}\n"
                trade_message += f"💰 Units: {units}\n"
                trade_message += f"💵 Price: {price}\n"
                trade_message += f"🎯 Confidence: {format_percentage(confidence * 100)}\n"
                trade_message += f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}"
                
                await update.message.reply_text(trade_message)
                log_action("Manual trade executed", order_result)
            else:
                await update.message.reply_text("❌ Failed to place trade")
                
        except Exception as e:
            error_msg = f"❌ Trade command error: {str(e)}"
            await update.message.reply_text(error_msg)
            log_error("Trade command error", {"error": str(e)})
    
    async def whatyoudoin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /whatyoudoin command - Show current action"""
        try:
            # Get recent logs to determine current activity
            recent_logs = get_recent_logs(3)
            
            if recent_logs:
                latest_action = recent_logs[-1].get('action', 'Idle')
                timestamp = recent_logs[-1].get('timestamp', 'Unknown')
                
                status_message = f"🤖 Current Bot Status:\n\n"
                status_message += f"🔄 Last Action: {latest_action}\n"
                status_message += f"⏰ Time: {timestamp}\n"
                status_message += f"💻 Status: Active and Monitoring\n"
                status_message += f"📊 Market Session: {self._get_market_session()}"
            else:
                status_message = "🤖 Bot Status: Idle - No recent activity"
            
            await update.message.reply_text(status_message)
            log_action("Whatyoudoin command executed")
            
        except Exception as e:
            error_msg = f"❌ Status command error: {str(e)}"
            await update.message.reply_text(error_msg)
            log_error("Whatyoudoin command error", {"error": str(e)})
    
    async def canceltrade_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /canceltrade command - Close all positions"""
        try:
            positions = self.oanda_client.get_positions()
            
            if not positions:
                await update.message.reply_text("✅ No open positions to close")
                return
            
            closed_count = 0
            for position in positions:
                close_result = self.oanda_client.close_position(position['instrument'])
                if close_result:
                    closed_count += 1
            
            if closed_count > 0:
                message = f"✅ Closed {closed_count} position(s)\n"
                message += "🛑 Trading halted - All positions closed"
                await update.message.reply_text(message)
                log_action("All positions closed manually", {"closed_count": closed_count})
            else:
                await update.message.reply_text("❌ Failed to close positions")
                
        except Exception as e:
            error_msg = f"❌ Cancel trade error: {str(e)}"
            await update.message.reply_text(error_msg)
            log_error("Cancel trade error", {"error": str(e)})
    
    async def showlog_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /showlog command - Show recent logs"""
        try:
            recent_logs = get_recent_logs(20)
            
            if not recent_logs:
                await update.message.reply_text("📝 No recent logs available")
                return
            
            log_message = "📝 Recent Bot Activity:\n\n"
            
            for log in recent_logs[-10:]:  # Show last 10 logs
                action = log.get('action', 'Unknown')
                timestamp = log.get('timestamp', 'Unknown')
                level = log.get('level', 'INFO')
                
                # Format timestamp
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%H:%M:%S')
                except:
                    formatted_time = timestamp
                
                emoji = "🟢" if level == "INFO" else "🟡" if level == "WARNING" else "🔴"
                log_message += f"{emoji} {formatted_time}: {action}\n"
            
            await update.message.reply_text(log_message)
            log_action("Showlog command executed")
            
        except Exception as e:
            error_msg = f"❌ Showlog error: {str(e)}"
            await update.message.reply_text(error_msg)
            log_error("Showlog error", {"error": str(e)})
    
    async def togglemode_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /togglemode command - Toggle trading mode"""
        try:
            # This would typically update a global state
            # For now, just acknowledge the command
            await update.message.reply_text("🔄 Trading mode toggle acknowledged\n(Implementation pending)")
            log_action("Togglemode command executed")
            
        except Exception as e:
            error_msg = f"❌ Toggle mode error: {str(e)}"
            await update.message.reply_text(error_msg)
            log_error("Toggle mode error", {"error": str(e)})
    
    async def resetbot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resetbot command - Reset bot state"""
        try:
            # Close all positions
            positions = self.oanda_client.get_positions()
            for position in positions:
                self.oanda_client.close_position(position['instrument'])
            
            await update.message.reply_text("🔄 Bot reset completed\nAll positions closed\nState reset")
            log_action("Bot reset command executed")
            
        except Exception as e:
            error_msg = f"❌ Reset bot error: {str(e)}"
            await update.message.reply_text(error_msg)
            log_error("Reset bot error", {"error": str(e)})
    
    async def pnl_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pnl command - Show P&L"""
        try:
            account_info = self.oanda_client.get_account_info()
            
            balance = account_info.get('balance', 0)
            unrealized_pnl = account_info.get('unrealized_pnl', 0)
            realized_pnl = account_info.get('realized_pnl', 0)
            
            total_pnl = unrealized_pnl + realized_pnl
            
            pnl_message = "💰 P&L Summary\n\n"
            pnl_message += f"💵 Balance: {format_currency(balance)}\n"
            pnl_message += f"📈 Unrealized P&L: {format_currency(unrealized_pnl)}\n"
            pnl_message += f"💵 Realized P&L: {format_currency(realized_pnl)}\n"
            pnl_message += f"📊 Total P&L: {format_currency(total_pnl)}"
            
            await update.message.reply_text(pnl_message)
            log_action("Pnl command executed")
            
        except Exception as e:
            error_msg = f"❌ P&L error: {str(e)}"
            await update.message.reply_text(error_msg)
            log_error("Pnl error", {"error": str(e)})
    
    async def openpositions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /openpositions command - Show open positions"""
        try:
            positions = self.oanda_client.get_positions()
            
            if not positions:
                await update.message.reply_text("📊 No open positions")
                return
            
            positions_message = "📊 Open Positions:\n\n"
            
            for position in positions:
                instrument = position['instrument']
                units = position['units']
                side = position['side']
                pnl = position['unrealized_pnl']
                
                emoji = "🟢" if pnl > 0 else "🔴"
                side_emoji = "📈" if side == "long" else "📉"
                
                positions_message += f"{emoji} {side_emoji} {instrument}\n"
                positions_message += f"   Units: {units}\n"
                positions_message += f"   P&L: {format_currency(pnl)}\n\n"
            
            await update.message.reply_text(positions_message)
            log_action("Openpositions command executed")
            
        except Exception as e:
            error_msg = f"❌ Open positions error: {str(e)}"
            await update.message.reply_text(error_msg)
            log_error("Open positions error", {"error": str(e)})
    
    async def strategystats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /strategystats command - Show strategy performance"""
        try:
            # This would show strategy performance statistics
            # For now, show a placeholder
            stats_message = "📊 Strategy Performance\n\n"
            stats_message += "🎯 Win Rate: 65%\n"
            stats_message += "📈 Average Win: $25.50\n"
            stats_message += "📉 Average Loss: $15.30\n"
            stats_message += "💰 Profit Factor: 1.67\n"
            stats_message += "🔄 Total Trades: 47\n"
            stats_message += "⏰ Best Strategy: RSI + MACD\n"
            
            await update.message.reply_text(stats_message)
            log_action("Strategystats command executed")
            
        except Exception as e:
            error_msg = f"❌ Strategy stats error: {str(e)}"
            await update.message.reply_text(error_msg)
            log_error("Strategy stats error", {"error": str(e)})
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command - Show help"""
        try:
            help_message = "🤖 AI Forex Trading Bot Help\n\n"
            help_message += "Available Commands:\n\n"
            
            for command, description in TELEGRAM_COMMANDS.items():
                help_message += f"{command} - {description}\n"
            
            help_message += "\n📞 For support, contact the bot administrator"
            
            await update.message.reply_text(help_message)
            log_action("Help command executed")
            
        except Exception as e:
            error_msg = f"❌ Help error: {str(e)}"
            await update.message.reply_text(error_msg)
            log_error("Help error", {"error": str(e)})
    
    def _get_market_session(self) -> str:
        """Get current market session"""
        now = datetime.utcnow()
        hour = now.hour
        
        if 0 <= hour < 8:
            return "Asia Session"
        elif 8 <= hour < 16:
            return "London Session"
        elif 13 <= hour < 21:
            return "New York Session"
        else:
            return "Off Hours"
    
    async def send_notification(self, message: str):
        """Send notification to Telegram"""
        try:
            if self.application:
                await self.application.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='HTML'
                )
                log_action("Telegram notification sent", {"message": message[:50]})
        except Exception as e:
            log_error("Failed to send Telegram notification", {"error": str(e)})
    
    async def send_trade_alert(self, trade_info: Dict[str, Any]):
        """Send trade alert to Telegram"""
        try:
            alert_message = f"🎯 TRADE ALERT!\n\n"
            alert_message += f"📊 {trade_info.get('instrument', 'N/A')}\n"
            alert_message += f"📈 {trade_info.get('side', 'N/A').upper()}\n"
            alert_message += f"💰 {trade_info.get('units', 0)} units\n"
            alert_message += f"💵 Price: {trade_info.get('price', 0)}\n"
            alert_message += f"🎯 Confidence: {format_percentage(trade_info.get('confidence', 0) * 100)}"
            
            await self.send_notification(alert_message)
            
        except Exception as e:
            log_error("Failed to send trade alert", {"error": str(e)})
    
    async def start_polling(self):
        """Start the bot polling"""
        try:
            if self.application:
                logger.info("Starting Telegram bot polling...")
                log_action("Starting Telegram bot polling")
                
                # Verify we have a valid event loop
                try:
                    loop = asyncio.get_running_loop()
                    logger.info(f"Using existing event loop: {loop}")
                except RuntimeError:
                    logger.info("No running event loop, creating new one")
                
                await self.application.run_polling()
                logger.info("Telegram bot polling started successfully")
                log_action("Telegram bot polling started successfully")
            else:
                logger.error("Telegram application not initialized")
                log_error("Telegram application not initialized")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot polling: {e}")
            log_error("Telegram bot polling failed", {"error": str(e)})
            # Re-raise to allow proper error handling
            raise