#!/usr/bin/env python3
"""
Trading Bot Runner - Modular async entry point
Handles bot startup, shutdown, and health monitoring
"""

import asyncio
import signal
import sys
import logging
import time
from typing import Optional, List
from datetime import datetime

from trading_bot import TradingBot
from utils import log_action, log_error

logger = logging.getLogger(__name__)

class BotRunner:
    """Manages the trading bot lifecycle with health monitoring"""
    
    def __init__(self):
        self.bot: Optional[TradingBot] = None
        self.tasks: List[asyncio.Task] = []
        self.is_running = False
        self.health_check_interval = 60  # seconds
        self.max_consecutive_failures = 3
        self.consecutive_failures = 0
        self.last_health_check = 0
        
    async def start(self):
        """Start the trading bot with comprehensive error handling"""
        try:
            log_action("BotRunner: Starting trading bot")
            self.is_running = True
            
            # Initialize bot
            self.bot = TradingBot()
            
            # Start health monitoring
            health_task = asyncio.create_task(self._health_monitor())
            self.tasks.append(health_task)
            
            # Start Telegram bot if available
            if self.bot.telegram_bot:
                log_action("BotRunner: Starting Telegram bot")
                telegram_task = asyncio.create_task(self.bot.telegram_bot.start_polling())
                self.tasks.append(telegram_task)
            
            # Start main trading loop
            log_action("BotRunner: Starting trading loop")
            trading_task = asyncio.create_task(self._run_trading_loop_with_recovery())
            self.tasks.append(trading_task)
            
            # Wait for all tasks
            await asyncio.gather(*self.tasks, return_exceptions=True)
            
        except Exception as e:
            log_error("BotRunner: Critical startup error", {"error": str(e)})
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the trading bot gracefully"""
        try:
            log_action("BotRunner: Stopping trading bot")
            self.is_running = False
            
            # Cancel all tasks
            for task in self.tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete cancellation
            if self.tasks:
                await asyncio.gather(*self.tasks, return_exceptions=True)
            
            # Stop the bot
            if self.bot:
                await self.bot.stop_async()
            
            log_action("BotRunner: Trading bot stopped successfully")
            
        except Exception as e:
            log_error("BotRunner: Error during shutdown", {"error": str(e)})
    
    async def _run_trading_loop_with_recovery(self):
        """Run trading loop with automatic recovery"""
        while self.is_running:
            try:
                await self.bot._run_trading_loop_async()
            except asyncio.CancelledError:
                log_action("BotRunner: Trading loop cancelled")
                break
            except Exception as e:
                self.consecutive_failures += 1
                log_error("BotRunner: Trading loop error", {
                    "error": str(e),
                    "consecutive_failures": self.consecutive_failures
                })
                
                if self.consecutive_failures >= self.max_consecutive_failures:
                    log_error("BotRunner: Max consecutive failures reached, stopping bot")
                    await self.stop()
                    break
                
                # Wait before retrying
                await asyncio.sleep(10)
    
    async def _health_monitor(self):
        """Monitor bot health and restart components if needed"""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Check if it's time for health check
                if current_time - self.last_health_check >= self.health_check_interval:
                    await self._perform_health_check()
                    self.last_health_check = current_time
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except asyncio.CancelledError:
                log_action("BotRunner: Health monitor cancelled")
                break
            except Exception as e:
                log_error("BotRunner: Health monitor error", {"error": str(e)})
                await asyncio.sleep(30)  # Wait longer on error
    
    async def _perform_health_check(self):
        """Perform comprehensive health check"""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "bot_running": self.bot.is_running if self.bot else False,
                "tasks_active": len([t for t in self.tasks if not t.done()]),
                "consecutive_failures": self.consecutive_failures
            }
            
            # Check OANDA connection
            if self.bot and self.bot.oanda_client:
                try:
                    # Simple connection test
                    account_info = self.bot.oanda_client.get_account_info()
                    health_status["oanda_connected"] = True
                    health_status["account_balance"] = account_info.get("balance", 0)
                except Exception as e:
                    health_status["oanda_connected"] = False
                    health_status["oanda_error"] = str(e)
            
            # Check Telegram connection
            if self.bot and self.bot.telegram_bot:
                try:
                    # Send a silent health check message
                    await self.bot.telegram_bot.send_notification(
                        f"🏥 Health Check - {datetime.now().strftime('%H:%M:%S')}\n"
                        f"Bot: {'✅' if health_status['bot_running'] else '❌'}\n"
                        f"Tasks: {health_status['tasks_active']}\n"
                        f"Failures: {health_status['consecutive_failures']}"
                    )
                    health_status["telegram_connected"] = True
                except Exception as e:
                    health_status["telegram_connected"] = False
                    health_status["telegram_error"] = str(e)
            
            # Log health status
            log_action("BotRunner: Health check completed", health_status)
            
            # Reset failure counter if everything is healthy
            if (health_status.get("bot_running", False) and 
                health_status.get("oanda_connected", False)):
                self.consecutive_failures = 0
            
        except Exception as e:
            log_error("BotRunner: Health check error", {"error": str(e)})

async def async_main():
    """Async main entry point with comprehensive error handling"""
    runner = None
    try:
        runner = BotRunner()
        await runner.start()
    except asyncio.CancelledError:
        log_action("BotRunner: Main cancelled")
        if runner:
            await runner.stop()
    except Exception as e:
        log_error("BotRunner: Main error", {"error": str(e)})
        if runner:
            await runner.stop()
        raise

def main():
    """Main entry point with signal handling"""
    try:
        # Set up signal handlers
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}")
            log_action(f"Shutdown signal received: {signum}")
            # The async loop will handle graceful shutdown
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGHUP, signal_handler)
        
        log_action("BotRunner: Starting application")
        asyncio.run(async_main())
        
    except KeyboardInterrupt:
        log_action("BotRunner: Stopped by keyboard interrupt")
    except Exception as e:
        log_error("BotRunner: Fatal error", {"error": str(e)})
        sys.exit(1)

if __name__ == "__main__":
    main()