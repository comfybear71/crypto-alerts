import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_daily_update():
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Debug: Try to fetch data
    debug_info = []
    
    # Try 1: Basic request
    try:
        response = requests.get("https://api.swyftx.com.au/markets/live-rates/AUD/", timeout=10)
        debug_info.append(f"Status: {response.status_code}")
        debug_info.append(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        debug_info.append(f"Length: {len(response.text)}")
        
        if response.status_code == 200:
            data = response.json()
            debug_info.append(f"Type: {type(data)}")
            
            if isinstance(data, list):
                debug_info.append(f"Items: {len(data)}")
                if len(data) > 0:
                    debug_info.append(f"First item: {str(data[0])[:100]}")
                    # Try to extract prices
                    coins = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA']
                    prices = []
                    for item in data:
                        if isinstance(item, dict):
                            asset = item.get('asset') or item.get('code') or item.get('symbol')
                            rate = item.get('rate') or item.get('price')
                            if asset and rate:
                                prices.append(f"{asset}: ${rate}")
                    debug_info.append(f"Found prices: {len(prices)}")
                    if prices:
                        debug_info.append("Sample: " + ", ".join(prices[:3]))
            elif isinstance(data, dict):
                debug_info.append(f"Keys: {list(data.keys())[:5]}")
        else:
            debug_info.append(f"Error: {response.text[:200]}")
    except Exception as e:
        debug_info.append(f"Exception: {str(e)}")
    
    # Build message
    message = f"📊 *Debug Info*\n⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    message += "\n".join(debug_info)
    
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(send_daily_update())
