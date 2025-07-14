# Forex Demo Trading Bot (OANDA + Telegram)

## Minimal, Safe, Demo-Only Deployment

### 1. Prerequisites
- Python 3.8.10+ (Ubuntu 20.04+ recommended)
- OANDA demo account
- Telegram bot token & chat ID

### 2. Clone and Prepare
```bash
git clone https://github.com/dommurphy155/Last-attempt.git
cd Last-attempt
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Export Required Environment Variables
```bash
export TELEGRAM_BOT_TOKEN="7874560450:AAH-Bmu1GJTVjwRM7jounms9FFYfC4EbVBQ"
export TELEGRAM_CHAT_ID="8038953791"
export OANDA_API_KEY="e02c6cecb654c12d7874d8d5a7a912cc-463d0c7414dbc13e09ce5fbd4d309e02"
export OANDA_ACCOUNT_ID="101-004-31152935-001"
```

### 4. Run the Bot Manually (for testing)
```bash
python3 bot_runner.py
```

### 5. Deploy as a Systemd Service
- Edit `forex-bot.service` and set the correct WorkingDirectory and Environment values if needed.
- Copy the service file:
```bash
sudo cp forex-bot.service /etc/systemd/system/forex-bot.service
sudo systemctl daemon-reload
sudo systemctl enable forex-bot
sudo systemctl start forex-bot
```

### 6. Monitor the Bot
```bash
sudo systemctl status forex-bot
sudo journalctl -u forex-bot -f --no-pager
```

### 7. Telegram Bot Usage
- Use `/start`, `/status`, `/maketrade`, `/canceltrade`, `/showlog`, `/pnl`, `/openpositions`, `/strategystats` in your Telegram chat.
- All trades are demo-only. Live trading is **blocked** and logged if attempted.

### 8. Safety & Security
- **demo_mode** is always `True` in `config.py`. No live trades are possible.
- All credentials are loaded from environment variables only. No secrets in code.
- Only OANDA and Telegram APIs are used. No AI, scraping, or external bloat.
- Logging clearly shows demo mode status and all trade actions.

### 9. Troubleshooting
- Check logs for errors: `sudo journalctl -u forex-bot -f --no-pager`
- Ensure all environment variables are exported in the shell or set in the systemd service.
- For import or dependency errors: `pip install -r requirements.txt`

---

**This repo is 100% minimal, demo-only, and safe for immediate deployment. No AI, no scraping, no bloat.**