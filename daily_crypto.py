import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

COINS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'MATIC', 'LINK', 'UNI', 'LTC',
         'BCH', 'ETC', 'XLM', 'VET', 'FIL', 'TRX', 'EOS', 'AAVE', 'ATOM', 'XTZ']

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY', '').strip()

async def send_daily_update():
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Try to get prices from public endpoint
    prices = {}
    try:
        response = requests.get("https://api.swyftx.com.au/markets/live-rates/AUD/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Handle different response formats
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        coin = item.get('asset') or item.get('code')
                        if coin and coin.upper() in COINS:
                            prices[coin.upper()] = {
                                'price': item.get('rate') or item.get('price') or 0,
                                'change': item.get('change24hPercent') or item.get('change24h') or 0
                            }
    except Exception as e:
        print(f"Error fetching prices: {e}")
    
    # Build message
    message = f"📊 *Daily Crypto Update*\n⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    if prices:
        message += "*Market Prices (AUD):*\n"
        for coin in sorted(prices.keys()):
            p = prices[coin]
            emoji = "🟢" if float(p['change']) >= 0 else "🔴"
            price = float(p['price'])
            if price > 1000:
                price_str = f"${price:,.2f}"
            else:
                price_str = f"${price:.2f}"
            message += f"{emoji} *{coin}*: {price_str} ({float(p['change']):+.2f}%)\n"
        message += f"\n📈 {len(prices)} coins"
    else:
        message += "❌ Could not fetch prices"
    
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(send_daily_update())
