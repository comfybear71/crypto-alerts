import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

# Match the secret names in your GitHub
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '').strip() or os.getenv('TELEGRAM_TOKEN', '').strip()
CHAT_ID = os.getenv('CHAT_ID', '').strip()
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY', '').strip()
SWYFTX_ACCESS_TOKEN = os.getenv('SWYFTX_ACCESS_TOKEN', '').strip()

async def send_daily_update():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Debug info
    debug_info = []
    debug_info.append(f"TELEGRAM_BOT_TOKEN exists: {bool(TELEGRAM_BOT_TOKEN)}")
    debug_info.append(f"CHAT_ID exists: {bool(CHAT_ID)}")
    debug_info.append(f"SWYFTX_API_KEY exists: {bool(SWYFTX_API_KEY)}")
    debug_info.append(f"SWYFTX_ACCESS_TOKEN exists: {bool(SWYFTX_ACCESS_TOKEN)}")
    
    # Try to get portfolio
    portfolio = None
    token = SWYFTX_ACCESS_TOKEN
    
    if not token and SWYFTX_API_KEY:
        try:
            url = "https://api.swyftx.com.au/auth/refresh/"
            response = requests.post(url, json={"apiKey": SWYFTX_API_KEY}, timeout=15)
            if response.status_code == 200:
                token = response.json().get("accessToken")
                debug_info.append("Token generated from API key")
        except Exception as e:
            debug_info.append(f"Auth error: {str(e)}")
    
    if token:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get("https://api.swyftx.com.au/portfolio/", headers=headers, timeout=10)
            if response.status_code == 200:
                portfolio = response.json()
        except Exception as e:
            debug_info.append(f"Portfolio error: {str(e)}")
    
    # Get prices
    prices = None
    try:
        COINS = ['bitcoin', 'ethereum', 'solana', 'ripple', 'cardano', 'polkadot', 
                 'matic', 'chainlink', 'uniswap', 'litecoin']
        ids = ','.join(COINS)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=aud&include_24hr_change=true"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            prices = response.json()
    except Exception as e:
        debug_info.append(f"Price error: {e}")
    
    # Build message
    message = f"Daily Crypto Update\n"
    message += f"Time: {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Portfolio
    if portfolio:
        message += "Swyftx Portfolio\n"
        total = portfolio.get('totalAudBalance', 0)
        message += f"Total: ${float(total):,.2f} AUD\n\n"
    else:
        message += "Portfolio: Not available\n\n"
    
    # Prices
    if prices:
        message += "Market Prices (AUD):\n"
        coin_map = {
            'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL',
            'ripple': 'XRP', 'cardano': 'ADA', 'polkadot': 'DOT',
            'matic': 'MATIC', 'chainlink': 'LINK', 'uniswap': 'UNI',
            'litecoin': 'LTC'
        }
        
        for coin_id, symbol in coin_map.items():
            if coin_id in prices:
                p = prices[coin_id]
                price = float(p['aud'])
                change = float(p.get('aud_24h_change', 0))
                price_str = f"${price:,.2f}" if price > 1000 else f"${price:.4f}"
                message += f"{symbol}: {price_str} ({change:+.2f}%)\n"
    
    await bot.send_message(chat_id=CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
