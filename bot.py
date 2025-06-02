import yfinance as yf
import pandas as pd
import numpy as np
import requests

# Bot token and your chat_id
BOT_TOKEN = 'YOUR_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

# Get Natural Gas data
data = yf.download('NG=F', period="6mo", interval="1d")

# RSI Calculation
def compute_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = np.maximum(delta, 0)
    loss = -np.minimum(delta, 0)
    avg_gain = pd.Series(gain).rolling(window).mean()
    avg_loss = pd.Series(loss).rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# MACD Calculation
def compute_macd(data):
    ema12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema26 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

# Indicators
data['EMA20'] = data['Close'].ewm(span=20).mean()
data['EMA50'] = data['Close'].ewm(span=50).mean()
data['RSI'] = compute_rsi(data)
data['MACD'], data['MACD_signal'] = compute_macd(data)

# Latest row
latest = data.iloc[-1]
msg = f"🧠 Natural Gas Technicals:\n\n💰 Close: ₹{latest['Close']:.2f}\n📈 RSI: {latest['RSI']:.2f}\n📊 MACD: {latest['MACD']:.2f} | Signal: {latest['MACD_signal']:.2f}"

# Signal Logic
if latest['RSI'] > 50 and latest['MACD'] > latest['MACD_signal'] and latest['Close'] > latest['EMA20'] and latest['Close'] > latest['EMA50']:
    msg += "\n\n✅ Signal: **BUY**"
else:
    msg += "\n\n⚠️ Signal: **WAIT/NO TRADE**"

# Send to Telegram
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
params = {
    "chat_id": CHAT_ID,
    "text": msg,
    "parse_mode": "Markdown"
}
response = requests.get(url, params=params)
print(response.json())
