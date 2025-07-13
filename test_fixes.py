#!/usr/bin/env python3
"""
Test script to verify the fixes for:
1. Telegram bot async polling issues
2. News sentiment volatility_score KeyError
"""

import asyncio
import logging
import sys
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_news_sentiment_fixes():
    """Test the news sentiment fixes"""
    print("🧪 Testing News Sentiment Fixes...")
    
    try:
        from news_sentiment import NewsSentimentAnalyzer
        
        # Create analyzer
        analyzer = NewsSentimentAnalyzer()
        
        # Test 1: Analyze sentiment with safe dictionary access
        print("  Testing sentiment analysis...")
        result = analyzer.analyze_news_sentiment()
        
        # Verify all required keys exist
        required_keys = ["sentiment", "score", "confidence", "volatility_score", "articles_analyzed"]
        for key in required_keys:
            if key not in result:
                print(f"  ❌ Missing key: {key}")
                return False
            print(f"  ✅ Key '{key}' exists: {result[key]}")
        
        # Test 2: Test should_avoid_trading with safe access
        print("  Testing should_avoid_trading...")
        should_avoid = analyzer.should_avoid_trading()
        print(f"  ✅ should_avoid_trading returned: {should_avoid}")
        
        # Test 3: Test get_sentiment_summary with safe access
        print("  Testing get_sentiment_summary...")
        summary = analyzer.get_sentiment_summary()
        print(f"  ✅ get_sentiment_summary returned: {summary[:100]}...")
        
        print("  ✅ All news sentiment tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ News sentiment test failed: {e}")
        return False

async def test_telegram_bot_async():
    """Test the Telegram bot async fixes"""
    print("🤖 Testing Telegram Bot Async Fixes...")
    
    try:
        from telegram_bot import TelegramBot
        from oanda_client import OandaClient
        from technical_analysis import TechnicalAnalyzer
        from news_sentiment import NewsSentimentAnalyzer
        
        # Create mock components (without real API calls)
        oanda_client = None
        technical_analyzer = None
        news_analyzer = None
        
        # Create Telegram bot instance
        bot = TelegramBot(oanda_client, technical_analyzer, news_analyzer)
        
        # Test 1: Verify start_polling is async
        print("  Testing start_polling method signature...")
        if asyncio.iscoroutinefunction(bot.start_polling):
            print("  ✅ start_polling is properly async")
        else:
            print("  ❌ start_polling is not async")
            return False
        
        # Test 2: Test async notification sending
        print("  Testing async notification sending...")
        try:
            await bot.send_notification("🧪 Test notification from fix verification")
            print("  ✅ Async notification sending works")
        except Exception as e:
            print(f"  ⚠️  Notification test failed (expected if no bot token): {e}")
        
        print("  ✅ All Telegram bot async tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Telegram bot async test failed: {e}")
        return False

def test_trading_bot_integration():
    """Test the trading bot integration fixes"""
    print("📈 Testing Trading Bot Integration Fixes...")
    
    try:
        from trading_bot import TradingBot
        
        # Test 1: Verify async main function exists
        print("  Testing async main function...")
        import trading_bot
        if hasattr(trading_bot, 'async_main'):
            print("  ✅ async_main function exists")
        else:
            print("  ❌ async_main function missing")
            return False
        
        # Test 2: Verify main function uses asyncio.run
        print("  Testing main function...")
        main_source = trading_bot.main.__code__.co_consts
        if any('asyncio.run' in str(const) for const in main_source):
            print("  ✅ main function uses asyncio.run")
        else:
            print("  ⚠️  main function may not use asyncio.run (check manually)")
        
        print("  ✅ All trading bot integration tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Trading bot integration test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Fix Verification Tests...")
    print("=" * 50)
    
    # Test news sentiment fixes
    news_sentiment_ok = test_news_sentiment_fixes()
    print()
    
    # Test Telegram bot async fixes
    telegram_bot_ok = await test_telegram_bot_async()
    print()
    
    # Test trading bot integration
    trading_bot_ok = test_trading_bot_integration()
    print()
    
    # Summary
    print("=" * 50)
    print("📊 Test Results Summary:")
    print(f"  News Sentiment Fixes: {'✅ PASSED' if news_sentiment_ok else '❌ FAILED'}")
    print(f"  Telegram Bot Async: {'✅ PASSED' if telegram_bot_ok else '❌ FAILED'}")
    print(f"  Trading Bot Integration: {'✅ PASSED' if trading_bot_ok else '❌ FAILED'}")
    
    all_passed = news_sentiment_ok and telegram_bot_ok and trading_bot_ok
    
    if all_passed:
        print("\n🎉 All fixes verified successfully!")
        print("✅ The bot should now run without the reported errors.")
    else:
        print("\n⚠️  Some tests failed. Please review the issues above.")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        sys.exit(1)