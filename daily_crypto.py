import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

# Match your EXACT secret names from GitHub
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '') or os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '') or os.getenv('CHAT_ID', '')
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY', '')
SWYFTX_ACCESS_TOKEN = os.getenv('SWYFTX_ACCESS_TOKEN', '')

async def send_daily_update():
    # Debug
    print(f"Token exists: {bool(TELEGRAM_BOT_TOKEN)}")
    print(f"Chat ID exists: {bool(TELEGRAM_CHAT_ID)}")
    print(f"Chat ID value: {TELEGRAM_CHAT_ID}")
    
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Get prices
    prices = {}
    try:
        COINS = ['bitcoin', 'ethereum', 'solana', 'ripple', 'cardano', 'polkadot', 
                 'matic', 'chainlink', 'uniswap', 'litecoin']
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
    except Exception as e:
        print(f"Price error: {e}")
    
    # Build message
    message = f"Daily Crypto Update\n"
    message += f"Time: {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    if prices:
        message += "Market Prices (AUD):\n"
        coin_names = {
            'BITCOIN': 'BTC', 'ETHEREUM': 'ETH', 'SOLANA': 'SOL',
            'RIPPLE': 'XRP', 'CARDANO': 'ADA', 'POLKADOT': 'DOT',
            'MATIC': 'MATIC', 'CHAINLINK': 'LINK', 'UNISWAP': 'UNI',
            'LITECOIN': 'LTC'
        }
        
        for coin, symbol in coin_names.items():
            if coin in prices:
                p = prices[coin]
                price = float(p['price'])
                change = float(p['change'])
                price_str = f"${price:,.2f}" if price > 1000 else f"${price:.4f}"
                emoji = "+" if change >= 0 else ""
                message += f"{symbol}: {price_str} ({emoji}{change:.2f}%)\n"
    
    # Send message
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
