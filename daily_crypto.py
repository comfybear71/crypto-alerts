import os
import requests
import asyncio
import json
from datetime import datetime
from telegram import Bot

# Coins to track - edit this list as needed
COINS = [
    'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'MATIC', 'LINK', 'UNI', 'LTC',
    'BCH', 'ETC', 'XLM', 'VET', 'FIL', 'TRX', 'EOS', 'AAVE', 'ATOM', 'XTZ',
    'ALGO', 'AVAX', 'BNB', 'DOGE', 'SHIB', 'PEPE', 'TON', 'SUI', 'RAY', 'JUP',
    'WIF', 'BONK', 'FLOKI', 'MOG', 'LUNC', 'COTI', 'BEAM', 'IMX', 'GALA', 'SAND'
]

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY')

async def get_swyftx_token():
    """Get JWT token from API key"""
    if not SWYFTX_API_KEY:
        return None
    
    url = "https://api.swyftx.com.au/auth/refresh/"
    headers = {"Content-Type": "application/json"}
    payload = {"apiKey": SWYFTX_API_KEY}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("accessToken")
    except Exception as e:
        print(f"Auth error: {e}")
    return None

async def get_portfolio(token):
    """Get portfolio balance"""
    if not token:
        return None
    
    url = "https://api.swyftx.com.au/portfolio/balance/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Balance error: {e}")
    return None

async def get_prices(token):
    """Get live rates"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = "https://api.swyftx.com.au/markets/live-rates/AUD/"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Price fetch error: {e}")
    
    return None

async def send_daily_update():
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Get auth token
    auth_token = await get_swyftx_token()
    
    # Get data
    portfolio = await get_portfolio(auth_token) if auth_token else None
    rates_data = await get_prices(auth_token)
    
    # Build message
    message = f"📊 *Daily Crypto Update*\n"
    message += f"⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Portfolio summary
    if portfolio:
        message += "💰 *Your Portfolio*\n"
        
        total_aud = portfolio.get('totalAudBalance') or 0
        available_aud = portfolio.get('availableAudBalance') or 0
        
        message += f"Total: `${float(total_aud):,.2f}` AUD\n"
        message += f"Available: `${float(available_aud):,.2f}` AUD\n\n"
        
        # Holdings
        holdings = portfolio.get('assets') or []
        if holdings:
            message += "*Holdings:*\n"
            for h in holdings[:10]:
                asset = h.get('asset') or 'Unknown'
                qty = float(h.get('balance') or 0)
                if qty > 0:
                    message += f"• {asset}: {qty:.4f}\n"
            message += "\n"
    elif auth_token:
        message += "💰 Portfolio: No balance data\n\n"
    else:
        message += "⚠️ Not authenticated - using public API\n\n"
    
    # Market prices
    if rates_data:
        prices = {}
        
        # Handle different formats
        rates_list = []
        if isinstance(rates_data, list):
            rates_list = rates_data
        elif isinstance(rates_data, dict):
            rates_list = [v for v in rates_data.values() if isinstance(v, dict)]
        
        for rate in rates_list:
            if not isinstance(rate, dict):
                continue
            
            coin = (rate.get('asset') or rate.get('code') or rate.get('name'))
            
            if coin:
                coin = str(coin).upper()
                if coin in [c.upper() for c in COINS]:
                    prices[coin] = {
                        'price': float(rate.get('rate') or rate.get('price') or 0),
                        'change': float(rate.get('change24hPercent') or rate.get('change24h') or 0)
                    }
        
        if prices:
            message += "*Market Prices:*\n"
            for coin in sorted(prices.keys()):
                p = prices[coin]
                emoji = "🟢" if p['change'] >= 0 else "🔴"
                
                if p['price'] > 1000:
                    price_str = f"${p['price']:,.2f}"
                elif p['price'] > 1:
                    price_str = f"${p['price']:.2f}"
                else:
                    price_str = f"${p['price']:.4f}"
                
                message += f"{emoji} *{coin}*: {price_str} ({p['change']:+.2f}%)\n"
            
            message += f"\n📈 {len(prices)} coins"
        else:
            message += "⚠️ No price data matched"
    else:
        message += "❌ Failed to fetch prices"
    
    # Send to Telegram
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(send_daily_update())
