import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY', '').strip()

async def get_portfolio():
    """Try API key as Bearer token"""
    if not SWYFTX_API_KEY:
        return None
    
    endpoints = [
        "https://api.swyftx.com.au/portfolio/",
        "https://api.swyftx.com.au/account/balance/",
    ]
    
    # Try API Key as Bearer (some APIs support this)
    headers_api_key = {
        "Authorization": f"Bearer {SWYFTX_API_KEY}",
        "User-Agent": "CryptoBot/1.0",
        "Content-Type": "application/json"
    }
    
    # Try with API-Key header (alternative)
    headers_key_header = {
        "API-Key": SWYFTX_API_KEY,
        "User-Agent": "CryptoBot/1.0",
        "Content-Type": "application/json"
    }
    
    for url in endpoints:
        # Try Bearer first
        try:
            response = requests.get(url, headers=headers_api_key, timeout=10)
            print(f"{url} (Bearer): {response.status_code}")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Bearer error: {e}")
        
        # Try API-Key header
        try:
            response = requests.get(url, headers=headers_key_header, timeout=10)
            print(f"{url} (API-Key): {response.status_code}")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"API-Key header error: {e}")
    
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
    
    # Get Swyftx portfolio
    portfolio = await get_portfolio()
    
    # Get prices
    prices = await get_prices()
    
    # Build message
    message = f"Daily Crypto Update\n"
    message += f"Time: {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Portfolio section
    if portfolio:
        message += "Swyftx Portfolio\n"
        
        total = (portfolio.get('totalAudBalance') or 
                portfolio.get('totalBalance') or 0)
        
        message += f"Total: ${float(total):,.2f} AUD\n\n"
        
        holdings = portfolio.get('assets') or []
        if holdings:
            message += "Holdings:\n"
            for h in holdings[:10]:
                asset = h.get('asset') or h.get('code') or 'Unknown'
                qty = float(h.get('balance') or 0)
                if qty > 0:
                    message += f"• {asset}: {qty:.4f}\n"
            message += "\n"
    else:
        message += "Portfolio: Not available (API key auth failed)\n\n"
    
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
