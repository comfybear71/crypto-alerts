import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_daily_update():
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Try to get prices
    prices = {}
    try:
        response = requests.get("https://api.swyftx.com.au/markets/live-rates/AUD/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        coin = item.get('asset') or item.get('code')
                        if coin:
                            prices[coin] = {
                                'price': item.get('rate', 0),
                                'change': item.get('change24hPercent', 0)
                            }
    except Exception as e:
        print(f"Error: {e}")
    
    # Build simple message (no markdown)
    message = f"Daily Crypto Update\n"
    message += f"Time: {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    if prices:
        message += "Market Prices (AUD):\n"
        # Just show first 10 coins
        for coin in list(prices.keys())[:10]:
            p = prices[coin]
            price = float(p['price'])
            change = float(p['change'])
            message += f"{coin}: ${price:.2f} ({change:+.2f}%)\n"
        message += f"\nTotal coins: {len(prices)}"
    else:
        message += "Could not fetch prices"
    
    # Send without markdown parsing
    await bot.send_message(chat_id=CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
