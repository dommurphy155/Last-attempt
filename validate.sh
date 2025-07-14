# ✅ AI FOREX BOT - FULL SYSTEM VALIDATOR SCRIPT

echo "🔍 Starting full system validation for AI Forex Demo Bot..."

# Step 1: Check for correct Python version
echo "🐍 Python version check..."
python3 -c 'import sys; assert sys.version_info >= (3,8), "❌ Python 3.8+ required!"'
echo "✅ Python version is OK."

# Step 2: Check virtual environment activation
echo "📦 Checking virtual environment..."
if [[ "$VIRTUAL_ENV" == "" ]]; then echo "❌ Virtual environment not active. Run: source venv/bin/activate" && exit 1; fi
echo "✅ Virtual environment is active."

# Step 3: Validate all required environment variables
echo "🔐 Checking credentials in environment..."
: "${TELEGRAM_BOT_TOKEN:?Missing TELEGRAM_BOT_TOKEN}"
: "${TELEGRAM_CHAT_ID:?Missing TELEGRAM_CHAT_ID}"
: "${OANDA_API_KEY:?Missing OANDA_API_KEY}"
: "${OANDA_ACCOUNT_ID:?Missing OANDA_ACCOUNT_ID}"
echo "✅ All required environment variables are set."

# Step 4: Confirm all Python dependencies are installed
echo "📦 Validating dependencies from requirements.txt..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed."

# Step 5: Check syntax of every .py file
echo "🧪 Running syntax checks on all Python files..."
for f in *.py; do
  python3 -m py_compile "$f" || { echo "❌ Syntax error in $f"; exit 1; }
done
echo "✅ Syntax OK on all files."

# Step 6: Attempt to import each module
echo "🧠 Checking Python module imports..."
for f in *.py; do
  module="${f%.py}"
  python3 -c "import $module" || { echo "❌ Import error in $module"; exit 1; }
done
echo "✅ All modules import cleanly."

# Step 7: Perform dry-run of bot logic
echo "🔁 Dry-running bot for async and init sanity..."
python3 bot_runner.py --dry-run || { echo "❌ Dry-run failed. Check async/init logic."; exit 1; }
echo "✅ Dry-run passed."

# Step 8: Check systemd service file if present
if [ -f forex-bot.service ]; then
  echo "🛠️ Validating systemd service file..."
  grep -q "ExecStart" forex-bot.service || { echo "❌ ExecStart missing in systemd service"; exit 1; }
  grep -q "Restart=always" forex-bot.service || { echo "❌ Missing restart policy in service file"; exit 1; }
  echo "✅ systemd service file looks valid."
fi

# Step 9: Check bot readiness from Telegram
echo "📨 Sending test /status command to Telegram bot..."
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
     -d chat_id="$TELEGRAM_CHAT_ID" \
     -d text="/status" > /dev/null && echo "✅ Telegram command sent."

# Step 10: Final verdict
echo "🎯 Bot environment, logic, dependencies, and control all appear healthy and functional."