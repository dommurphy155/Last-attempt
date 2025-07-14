#!/usr/bin/env python3
"""
Comprehensive deployment validation script
Checks all components, configuration, and dependencies
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_status(message, status="INFO"):
    """Print colored status message"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m", 
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, colors['INFO'])}[{status}]{colors['RESET']} {message}")

def check_python_version():
    """Check Python version compatibility"""
    print_status("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - OK", "SUCCESS")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+", "ERROR")
        return False

def check_required_files():
    """Check all required files exist"""
    print_status("Checking required files...")
    
    required_files = [
        "bot_runner.py",
        "trading_bot.py", 
        "config.py",
        "utils.py",
        "oanda_client.py",
        "technical_analysis.py",
        "news_sentiment.py",
        "telegram_bot.py",
        "requirements.txt",
        "README.md",
        "deploy.sh",
        "start_bot.sh",
        "stop_bot.sh",
        "forex-bot.service",
        "test_bot.py"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print_status(f"✅ {file}", "SUCCESS")
        else:
            print_status(f"❌ {file} - Missing", "ERROR")
            missing_files.append(file)
    
    return len(missing_files) == 0

def check_python_syntax():
    """Check Python syntax of all files"""
    print_status("Checking Python syntax...")
    
    python_files = [
        "config.py", "utils.py", "oanda_client.py", "technical_analysis.py",
        "news_sentiment.py", "telegram_bot.py", "trading_bot.py", "bot_runner.py"
    ]
    
    syntax_errors = []
    for file in python_files:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", file],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print_status(f"✅ {file}", "SUCCESS")
            else:
                print_status(f"❌ {file} - Syntax error", "ERROR")
                syntax_errors.append(file)
        except Exception as e:
            print_status(f"❌ {file} - Check failed: {e}", "ERROR")
            syntax_errors.append(file)
    
    return len(syntax_errors) == 0

def check_imports():
    """Test basic imports (without dependencies)"""
    print_status("Testing basic imports...")
    
    # Test config.py (should work without dependencies)
    try:
        import config
        print_status("✅ config.py imports", "SUCCESS")
    except Exception as e:
        print_status(f"❌ config.py import failed: {e}", "ERROR")
        return False
    
    return True

def check_environment_template():
    """Check environment template exists"""
    print_status("Checking environment template...")
    
    if os.path.exists(".env.template"):
        print_status("✅ .env.template exists", "SUCCESS")
        
        # Check template content
        with open(".env.template", "r") as f:
            content = f.read()
            required_vars = [
                "HUGGINGFACE_API_KEY",
                "TELEGRAM_BOT_TOKEN", 
                "TELEGRAM_CHAT_ID",
                "OANDA_API_KEY",
                "OANDA_ACCOUNT_ID"
            ]
            
            missing_vars = []
            for var in required_vars:
                if var not in content:
                    missing_vars.append(var)
            
            if missing_vars:
                print_status(f"⚠️  Missing variables in template: {missing_vars}", "WARNING")
            else:
                print_status("✅ All required variables in template", "SUCCESS")
        
        return True
    else:
        print_status("❌ .env.template missing", "ERROR")
        return False

def check_systemd_service():
    """Check systemd service file"""
    print_status("Checking systemd service file...")
    
    if os.path.exists("forex-bot.service"):
        print_status("✅ forex-bot.service exists", "SUCCESS")
        
        # Check service file content
        with open("forex-bot.service", "r") as f:
            content = f.read()
            
            # Check for bot_runner.py (not trading_bot.py)
            if "bot_runner.py" in content:
                print_status("✅ Service uses bot_runner.py", "SUCCESS")
            else:
                print_status("⚠️  Service may not use bot_runner.py", "WARNING")
            
            # Check for proper user/group
            if "User=" in content and "Group=" in content:
                print_status("✅ Service has user/group config", "SUCCESS")
            else:
                print_status("⚠️  Service missing user/group config", "WARNING")
        
        return True
    else:
        print_status("❌ forex-bot.service missing", "ERROR")
        return False

def check_deploy_script():
    """Check deployment script"""
    print_status("Checking deployment script...")
    
    if os.path.exists("deploy.sh"):
        print_status("✅ deploy.sh exists", "SUCCESS")
        
        # Check if executable
        if os.access("deploy.sh", os.X_OK):
            print_status("✅ deploy.sh is executable", "SUCCESS")
        else:
            print_status("⚠️  deploy.sh not executable", "WARNING")
        
        return True
    else:
        print_status("❌ deploy.sh missing", "ERROR")
        return False

def check_requirements():
    """Check requirements.txt"""
    print_status("Checking requirements.txt...")
    
    if os.path.exists("requirements.txt"):
        print_status("✅ requirements.txt exists", "SUCCESS")
        
        # Check for problematic entries
        with open("requirements.txt", "r") as f:
            content = f.read()
            
            if "asyncio" in content:
                print_status("⚠️  asyncio in requirements (should be removed)", "WARNING")
            
            # Check for essential packages
            essential_packages = [
                "requests", "python-telegram-bot", "oandapyV20", 
                "ta", "schedule", "python-dotenv"
            ]
            
            missing_packages = []
            for package in essential_packages:
                if package not in content:
                    missing_packages.append(package)
            
            if missing_packages:
                print_status(f"⚠️  Missing packages: {missing_packages}", "WARNING")
            else:
                print_status("✅ All essential packages included", "SUCCESS")
        
        return True
    else:
        print_status("❌ requirements.txt missing", "ERROR")
        return False

def check_directory_structure():
    """Check directory structure"""
    print_status("Checking directory structure...")
    
    # Check for unnecessary files that should be removed
    unnecessary_files = [
        "ASYNC_REFACTORING_SUMMARY.md",
        "DEPLOYMENT_GUIDE.md", 
        "forex-bot.timer",
        "setup_env.sh",
        "status_bot.sh",
        "health_check.sh",
        "monitor_bot.sh",
        "cleanup.sh"
    ]
    
    found_unnecessary = []
    for file in unnecessary_files:
        if os.path.exists(file):
            found_unnecessary.append(file)
    
    if found_unnecessary:
        print_status(f"⚠️  Unnecessary files found: {found_unnecessary}", "WARNING")
    else:
        print_status("✅ No unnecessary files found", "SUCCESS")
    
    return True

def generate_deployment_summary():
    """Generate deployment summary"""
    print_status("Generating deployment summary...")
    
    summary = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "files_checked": 15,
        "python_files": 8,
        "deployment_ready": True,
        "next_steps": [
            "1. Copy .env.template to .env",
            "2. Fill in your API keys in .env", 
            "3. Run: ./deploy.sh",
            "4. Start bot: ./start_bot.sh"
        ]
    }
    
    # Save summary
    with open("deployment_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print_status("✅ deployment_summary.json created", "SUCCESS")
    return summary

def main():
    """Run comprehensive validation"""
    print("🤖 AI Forex Trading Bot - Deployment Validation")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_required_files),
        ("Python Syntax", check_python_syntax),
        ("Basic Imports", check_imports),
        ("Environment Template", check_environment_template),
        ("Systemd Service", check_systemd_service),
        ("Deploy Script", check_deploy_script),
        ("Requirements", check_requirements),
        ("Directory Structure", check_directory_structure)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_status(f"Check failed: {e}", "ERROR")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print_status("🎉 All checks passed! Deployment is ready.", "SUCCESS")
        generate_deployment_summary()
        
        print("\n📋 Next Steps:")
        print("1. Copy .env.template to .env")
        print("2. Fill in your API keys in .env")
        print("3. Run: ./deploy.sh")
        print("4. Start bot: ./start_bot.sh")
        
        return 0
    else:
        print_status("❌ Some checks failed. Please fix issues before deployment.", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())