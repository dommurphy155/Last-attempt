#!/usr/bin/env python3
"""
Test script to verify AI Forex Trading Bot installation
"""

import sys
import os
import importlib
from datetime import datetime

def test_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    
    required_modules = [
        'requests',
        'bs4',
        'pandas',
        'numpy',
        'ta',
        'transformers',
        'torch',
        'textblob',
        'vaderSentiment',
        'schedule'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("✅ All imports successful")
        return True

def test_local_modules():
    """Test local bot modules"""
    print("\n🔍 Testing local modules...")
    
    local_modules = [
        'config',
        'utils',
        'technical_analysis',
        'news_sentiment',
        'oanda_client',
        'telegram_bot',
        'trading_bot'
    ]
    
    failed_modules = []
    
    for module in local_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_modules.append(module)
    
    if failed_modules:
        print(f"\n❌ Failed to import local modules: {', '.join(failed_modules)}")
        return False
    else:
        print("✅ All local modules successful")
        return True

def test_configuration():
    """Test configuration validation"""
    print("\n🔍 Testing configuration...")
    
    try:
        from config import validate_config, get_default_state
        
        # Test default state
        default_state = get_default_state()
        if isinstance(default_state, dict):
            print("✅ Default state creation successful")
        else:
            print("❌ Default state creation failed")
            return False
        
        # Test configuration validation (will fail without env vars, which is expected)
        try:
            validate_config()
            print("✅ Configuration validation successful")
        except ValueError as e:
            print(f"⚠️ Configuration validation (expected without env vars): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_utils():
    """Test utility functions"""
    print("\n🔍 Testing utility functions...")
    
    try:
        from utils import (
            log_action, log_error, calculate_win_rate, 
            format_currency, format_percentage, get_current_session
        )
        
        # Test basic functions
        log_action("Test action")
        log_error("Test error")
        
        win_rate = calculate_win_rate(10, 5)
        if win_rate == 66.67:
            print("✅ Win rate calculation successful")
        else:
            print(f"❌ Win rate calculation failed: {win_rate}")
            return False
        
        currency = format_currency(123.45)
        if currency == "123.45 USD":
            print("✅ Currency formatting successful")
        else:
            print(f"❌ Currency formatting failed: {currency}")
            return False
        
        percentage = format_percentage(12.34)
        if percentage == "12.34%":
            print("✅ Percentage formatting successful")
        else:
            print(f"❌ Percentage formatting failed: {percentage}")
            return False
        
        session = get_current_session()
        if session in ["Asia", "London", "New York", "Off Hours"]:
            print("✅ Session detection successful")
        else:
            print(f"❌ Session detection failed: {session}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Utility functions test failed: {e}")
        return False

def test_technical_analysis():
    """Test technical analysis module"""
    print("\n🔍 Testing technical analysis...")
    
    try:
        from technical_analysis import TechnicalAnalyzer
        
        analyzer = TechnicalAnalyzer()
        
        # Test with sample data
        prices = [1.1000, 1.1010, 1.1020, 1.1030, 1.1040, 1.1050, 1.1060, 1.1070, 1.1080, 1.1090]
        
        # Test RSI calculation
        rsi = analyzer.calculate_rsi(prices)
        if 0 <= rsi <= 100:
            print("✅ RSI calculation successful")
        else:
            print(f"❌ RSI calculation failed: {rsi}")
            return False
        
        # Test MACD calculation
        macd_line, signal_line, histogram = analyzer.calculate_macd(prices)
        if all(isinstance(x, (int, float)) for x in [macd_line, signal_line, histogram]):
            print("✅ MACD calculation successful")
        else:
            print("❌ MACD calculation failed")
            return False
        
        # Test EMA calculation
        ema = analyzer.calculate_ema(prices, 5)
        if isinstance(ema, (int, float)) and ema > 0:
            print("✅ EMA calculation successful")
        else:
            print(f"❌ EMA calculation failed: {ema}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Technical analysis test failed: {e}")
        return False

def test_file_structure():
    """Test file structure"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'requirements.txt',
        'config.py',
        'utils.py',
        'technical_analysis.py',
        'news_sentiment.py',
        'oanda_client.py',
        'telegram_bot.py',
        'trading_bot.py',
        'README.md',
        'setup.py',
        '.gitignore'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def main():
    """Run all tests"""
    print("🤖 AI Forex Trading Bot - Installation Test")
    print("=" * 50)
    print(f"Test time: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Local Modules", test_local_modules),
        ("Configuration", test_configuration),
        ("Utility Functions", test_utils),
        ("Technical Analysis", test_technical_analysis)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Installation is successful.")
        print("\nNext steps:")
        print("1. Set your environment variables:")
        print("   export HUGGINGFACE_API_KEY='your_key'")
        print("   export TELEGRAM_BOT_TOKEN='your_token'")
        print("   export TELEGRAM_CHAT_ID='your_chat_id'")
        print("   export OANDA_API_KEY='your_key'")
        print("   export OANDA_ACCOUNT_ID='your_account_id'")
        print("2. Run the bot: python trading_bot.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())