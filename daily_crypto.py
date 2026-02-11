import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

COINS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'MATIC', 'LINK', 'UNI', 'LTC']

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_daily_update():
    bot = Bot(token=TELEGRAM_TOKEN)
    
    url = "https://api.swyftx.com.au/markets/live-rates/AUD/"
    response = requests.get(url)
    data = response.json()
    
    prices = {}
    for asset_id, info in data.items():
        if isinstance(info, dict) and info.get('asset') in COINS:
            prices[info['asset']] = {
                'price': info.get('rate', 0),
                'change': info.get('change24hPercent', 0)
            }
    
    message = "📊 *Daily Crypto Prices (AUD)*\n\n"
    for coin in COINS:
        if coin in prices:
            p = prices[coin]
            emoji = "🟢" if p['change'] >= 0 else "🔴"
            message += f"*{coin}*: ${p['price']:,.2f} {emoji} {p['change']:+.2f}%\n"
    
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(send_daily_update())
