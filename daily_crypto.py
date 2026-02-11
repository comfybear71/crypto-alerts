import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Check all possible secret names
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY', '').strip()
SWYFTX_ACCESS_TOKEN = os.getenv('SWYFTX_ACCESS_TOKEN', '').strip()
SWYFTX_TOKEN = os.getenv('SWYFTX_TOKEN', '').strip()

async def send_daily_update():
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Debug: Show what we found
    debug_info = []
    debug_info.append(f"TELEGRAM_TOKEN exists: {bool(TELEGRAM_TOKEN)}")
    debug_info.append(f"CHAT_ID exists: {bool(CHAT_ID)}")
    debug_info.append(f"SWYFTX_API_KEY exists: {bool(SWYFTX_API_KEY)}")
    debug_info.append(f"SWYFTX_ACCESS_TOKEN exists: {bool(SWYFTX_ACCESS_TOKEN)}")
    debug_info.append(f"SWYFTX_TOKEN exists: {bool(SWYFTX_TOKEN)}")
    
    if SWYFTX_API_KEY:
        debug_info.append(f"API Key: {SWYFTX_API_KEY[:20]}...")
    if SWYFTX_ACCESS_TOKEN:
        debug_info.append(f"Access Token: {SWYFTX_ACCESS_TOKEN[:30]}...")
    if SWYFTX_TOKEN:
        debug_info.append(f"Token: {SWYFTX_TOKEN[:30]}...")
    
    # Try auth with whatever we have
    token = None
    
    # Priority 1: Use access token directly if available
    if SWYFTX_ACCESS_TOKEN:
        debug_info.append("Trying SWYFTX_ACCESS_TOKEN...")
        token = SWYFTX_ACCESS_TOKEN
    
    # Priority 2: Try API key to generate token
    elif SWYFTX_API_KEY:
        debug_info.append("Trying to generate token from API key...")
        url = "https://api.swyftx.com.au/auth/refresh/"
        headers = {"Content-Type": "application/json"}
        payload = {"apiKey": SWYFTX_API_KEY}
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            debug_info.append(f"Auth status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("accessToken")
                if token:
                    debug_info.append("Token generated successfully!")
                else:
                    debug_info.append(f"No token. Response keys: {list(data.keys())}")
            else:
                debug_info.append(f"Auth failed: {response.text[:200]}")
        except Exception as e:
            debug_info.append(f"Auth error: {str(e)}")
    
    # Get portfolio if we have a token
    portfolio = None
    if token:
        debug_info.append("Fetching portfolio...")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get("https://api.swyftx.com.au/portfolio/", headers=headers, timeout=10)
            debug_info.append(f"Portfolio status: {response.status_code}")
            
            if response.status_code == 200:
                portfolio = response.json()
                debug_info.append("Portfolio fetched!")
            else:
                debug_info.append(f"Portfolio error: {response.text[:200]}")
        except Exception as e:
            debug_info.append(f"Portfolio exception: {str(e)}")
    
    # Get prices from CoinGecko
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
    
    # Debug info
    message += "Debug Info:\n"
    for line in debug_info:
        message += f"{line}\n"
    message += "\n"
    
    # Portfolio
    if portfolio:
        message += "Portfolio\n"
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
