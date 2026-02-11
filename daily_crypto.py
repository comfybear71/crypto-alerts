import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY', '').strip()

async def get_access_token():
    """Generate JWT access token from API key"""
    if not SWYFTX_API_KEY:
        print("No API key found")
        return None
    
    url = "https://api.swyftx.com.au/auth/refresh/"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; CryptoBot/1.0)"
    }
    payload = {"apiKey": SWYFTX_API_KEY}
    
    try:
        print(f"Auth request to {url}")
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"Auth status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("accessToken")
            if token:
                print(f"Token acquired successfully")
                return token
            else:
                print(f"No accessToken in response. Got: {list(data.keys())}")
        else:
            print(f"Auth failed: {response.status_code} - {response.text[:300]}")
    except Exception as e:
        print(f"Auth error: {str(e)}")
    
    return None

async def get_account_info(token):
    """Get account info to verify auth works"""
    if not token:
        return None
    
    url = "https://api.swyftx.com.au/user/"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"User info status: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"User info error: {response.text[:200]}")
    except Exception as e:
        print(f"User info exception: {e}")
    
    return None

async def get_portfolio(token):
    """Get portfolio using correct endpoint"""
    if not token:
        return None
    
    # Try the exact endpoints from Apiary docs
    endpoints = [
        "https://api.swyftx.com.au/portfolio/",  # Portfolio endpoint
        "https://api.swyftx.com.au/account/balance/",  # Account balance
    ]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    for url in endpoints:
        try:
            print(f"Trying endpoint: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Got data with keys: {list(data.keys())[:5]}")
                return data
            else:
                print(f"Failed: {response.text[:200]}")
        except Exception as e:
            print(f"Exception: {e}")
    
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
    token = await get_access_token()
    user_info = await get_account_info(token) if token else None
    portfolio = await get_portfolio(token) if token else None
    
    # Get prices
    prices = await get_prices()
    
    # Build message
    message = f"Daily Crypto Update\n"
    message += f"Time: {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Auth status
    if user_info:
        email = user_info.get('email', 'Unknown')
        message += f"Swyftx Account: {email}\n\n"
    
    # Portfolio section
    if portfolio:
        message += "Portfolio\n"
        
        # Try different possible field names
        total = (portfolio.get('totalAudBalance') or 
                portfolio.get('totalBalance') or 
                portfolio.get('balance') or
                portfolio.get('audBalance') or 0)
        
        message += f"Total: ${float(total):,.2f} AUD\n\n"
        
        # Holdings
        holdings = (portfolio.get('assets') or 
                   portfolio.get('holdings') or 
                   portfolio.get('items') or [])
        
        if holdings:
            message += "Holdings:\n"
            for h in holdings[:10]:
                asset = (h.get('asset') or h.get('code') or 
                        h.get('symbol') or h.get('name') or 'Unknown')
                qty = float(h.get('balance') or h.get('quantity') or h.get('amount') or 0)
                if qty > 0:
                    message += f"• {asset}: {qty:.4f}\n"
            message += "\n"
    else:
        message += "Portfolio: Not available\n"
        if not token:
            message += "(Authentication failed - check API key)\n"
        elif not user_info:
            message += "(Token valid but no user info)\n"
        else:
            message += "(Token valid but portfolio fetch failed)\n"
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
                
                price_str = f"${price:,.2f}" if price > 1000 else f"${price:.4f}"
                message += f"{symbol}: {price_str} ({change:+.2f}%)\n"
    
    await bot.send_message(chat_id=CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
