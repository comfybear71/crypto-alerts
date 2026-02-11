import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY', '').strip()

async def get_swyftx_token():
    """Get JWT token from API key"""
    if not SWYFTX_API_KEY:
        return None
    
    url = "https://api.swyftx.com.au/auth/refresh/"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "CryptoBot/1.0"
    }
    payload = {"apiKey": SWYFTX_API_KEY}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Auth status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            return data.get("accessToken")
        else:
            print(f"Auth error: {response.text[:200]}")
    except Exception as e:
        print(f"Auth exception: {e}")
    return None

async def get_portfolio(token):
    """Try multiple portfolio endpoints"""
    if not token:
        return None
    
    # Try different endpoints
    endpoints = [
        "https://api.swyftx.com.au/portfolio/",
        "https://api.swyftx.com.au/account/balance/",
        "https://api.swyftx.com.au/portfolio/balance/"
    ]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "CryptoBot/1.0",
        "Content-Type": "application/json"
    }
    
    for url in endpoints:
        try:
            print(f"Trying: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Response: {response.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")
    
    return None

async def get_prices():
    """Get prices from CoinGecko"""
    COINS = ['bitcoin', 'ethereum', 'solana', 'ripple', 'cardano', 'polkadot', 
             'matic', 'chainlink', 'uniswap', 'litecoin']
    
    try:
        ids = ','.join(COINS)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=aud&include_24hr_change=true"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Price error: {e}")
    return None

async def send_daily_update():
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Get Swyftx data
    token = await get_swyftx_token()
    portfolio = await get_portfolio(token) if token else None
    
    # Get prices
    prices = await get_prices()
    
    # Build message
    message = f"Daily Crypto Update\n"
    message += f"Time: {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Portfolio section
    if portfolio:
        message += "Swyftx Portfolio\n"
        
        # Try different field names
        total = (portfolio.get('totalAudBalance') or 
                portfolio.get('totalBalance') or 
                portfolio.get('balance') or 0)
        
        message += f"Total: ${float(total):,.2f} AUD\n\n"
        
        # Holdings
        holdings = (portfolio.get('assets') or 
                   portfolio.get('holdings') or 
                   portfolio.get('balances') or [])
        
        if holdings:
            message += "Holdings:\n"
            for h in holdings[:10]:
                asset = (h.get('asset') or h.get('code') or 
                        h.get('symbol') or 'Unknown')
                qty = float(h.get('balance') or h.get('quantity') or 0)
                if qty > 0:
                    message += f"• {asset}: {qty:.4f}\n"
            message += "\n"
    else:
        message += "Portfolio: Not available\n"
        if not token:
            message += "(Auth failed - check API key)\n"
        message += "\n"
    
    # Market prices
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
                
                if price > 1000:
                    price_str = f"${price:,.2f}"
                else:
                    price_str = f"${price:.4f}"
                
                message += f"{symbol}: {price_str} ({change:+.2f}%)\n"
    
    await bot.send_message(chat_id=CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
