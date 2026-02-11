import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_daily_update():
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        
        # Check if secrets are loaded
        if not TELEGRAM_TOKEN:
            print("ERROR: TELEGRAM_TOKEN not set")
            return
            
        if not CHAT_ID:
            print("ERROR: CHAT_ID not set")
            return
        
        # Try endpoints
        endpoints = [
            "https://api.swyftx.com.au/markets/live-rates/AUD/",
            "https://api.swyftx.com.au/markets/assets/",
        ]
        
        results = []
        data = None
        
        for url in endpoints:
            try:
                response = requests.get(url, timeout=10)
                results.append(f"{url}: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    results.append(f"Success!")
                    break
            except Exception as e:
                results.append(f"{url}: {str(e)[:50]}")
        
        # Build message
        message = f"📊 *Debug*\n⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
        message += f"Token exists: {bool(TELEGRAM_TOKEN)}\n"
        message += f"Chat ID exists: {bool(CHAT_ID)}\n\n"
        message += "*Endpoints:*\n" + "\n".join(results)
        
        if data:
            message += f"\n\n*Data type:* {type(data)}"
            if isinstance(data, list):
                message += f"\n*Count:* {len(data)}"
            elif isinstance(data, dict):
                message += f"\n*Keys:* {list(data.keys())[:5]}"
        
        # Send message
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
        print("Message sent successfully")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        # Try to send error message
        try:
            bot = Bot(token=TELEGRAM_TOKEN or "dummy")
            await bot.send_message(chat_id=CHAT_ID or "123456", text=f"Error: {str(e)[:400]}")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(send_daily_update())
