import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Coins to track
COINS = ['bitcoin', 'ethereum', 'solana', 'ripple', 'cardano', 'polkadot', 'matic', 'chainlink', 'uniswap', 'litecoin']

async def send_daily_update():
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Try CoinGecko API (free, no auth needed)
    prices = {}
    try:
        # Get prices from CoinGecko
        ids = ','.join(COINS)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=aud&include_24hr_change=true"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for coin in COINS:
                if coin in data:
                    prices[coin.upper()] = {
                        'price': data[coin]['aud'],
                        'change': data[coin].get('aud_24h_change', 0)
                    }
        else:
            print(f"CoinGecko error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Build message
    message = f"Daily Crypto Update\n"
    message += f"Time: {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    if prices:
        message += "Market Prices (AUD):\n"
        for coin in sorted(prices.keys()):
            p = prices[coin]
            price = float(p['price'])
            change = float(p['change'])
            
            if price > 1000:
                price_str = f"${price:,.2f}"
            else:
                price_str = f"${price:.4f}"
            
            message += f"{coin}: {price_str} ({change:+.2f}%)\n"
        
        message += f"\n{len(prices)} coins tracked"
    else:
        message += "Could not fetch prices. API may be rate limited."
        message += "\nTry again in a few minutes."
    
    await bot.send_message(chat_id=CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
