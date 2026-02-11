import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_daily_update():
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Try different endpoints
    endpoints = [
        "https://api.swyftx.com.au/markets/live-rates/AUD/",
        "https://api.swyftx.com.au/markets/assets/",
        "https://api.swyftx.com.au/rates/",
    ]
    
    results = []
    data = None
    
    for url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            results.append(f"{url}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                results.append(f"Success! Type: {type(data)}")
                break
        except Exception as e:
            results.append(f"{url}: Error - {str(e)}")
    
    # Build message
    message = f"📊 *Debug*\n⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    message += "*Endpoint Tests:*\n" + "\n".join(results)
    
    if data:
        message += f"\n\n*Data Sample:*\n{str(data)[:500]}"
    
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(send_daily_update())
