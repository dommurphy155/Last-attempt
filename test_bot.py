#!/usr/bin/env python3
"""
Test script to validate bot components
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import config
        print("✅ config.py")
    except Exception as e:
        print(f"❌ config.py: {e}")
        return False
    
    try:
        import utils
        print("✅ utils.py")
    except Exception as e:
        print(f"❌ utils.py: {e}")
        return False
    
    try:
        import oanda_client
        print("✅ oanda_client.py")
    except Exception as e:
        print(f"❌ oanda_client.py: {e}")
        return False
    
    try:
        import technical_analysis
        print("✅ technical_analysis.py")
    except Exception as e:
        print(f"❌ technical_analysis.py: {e}")
        return False
    
    try:
        import news_sentiment
        print("✅ news_sentiment.py")
    except Exception as e:
        print(f"❌ news_sentiment.py: {e}")
        return False
    
    try:
        import telegram_bot
        print("✅ telegram_bot.py")
    except Exception as e:
        print(f"❌ telegram_bot.py: {e}")
        return False
    
    try:
        import trading_bot
        print("✅ trading_bot.py")
    except Exception as e:
        print(f"❌ trading_bot.py: {e}")
        return False
    
    try:
        import bot_runner
        print("✅ bot_runner.py")
    except Exception as e:
        print(f"❌ bot_runner.py: {e}")
        return False
    
    return True

def test_config():
    """Test configuration validation"""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import validate_config
        # This will fail without environment variables, which is expected
        validate_config()
        print("✅ Configuration validation passed")
        return True
    except ValueError as e:
        print(f"⚠️  Configuration validation: {e}")
        print("   (This is expected without environment variables)")
        return True
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def test_syntax():
    """Test Python syntax of all files"""
    print("\n📝 Testing Python syntax...")
    
    python_files = [
        "config.py", "utils.py", "oanda_client.py", "technical_analysis.py",
        "news_sentiment.py", "telegram_bot.py", "trading_bot.py", "bot_runner.py"
    ]
    
    all_good = True
    for file in python_files:
        try:
            import py_compile
            py_compile.compile(file, doraise=True)
            print(f"✅ {file}")
        except Exception as e:
            print(f"❌ {file}: {e}")
            all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("🤖 AI Forex Trading Bot - Component Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        sys.exit(1)
    
    # Test configuration
    if not test_config():
        print("\n❌ Configuration tests failed!")
        sys.exit(1)
    
    # Test syntax
    if not test_syntax():
        print("\n❌ Syntax tests failed!")
        sys.exit(1)
    
    print("\n🎉 All tests passed!")
    print("\n📋 Next steps:")
    print("1. Copy .env.template to .env")
    print("2. Fill in your API keys in .env")
    print("3. Run: python3 bot_runner.py")
    print("4. Or deploy with: ./deploy.sh")

if __name__ == "__main__":
    main()