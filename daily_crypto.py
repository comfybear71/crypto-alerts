import os
import requests
import asyncio
import traceback
from datetime import datetime
from telegram import Bot

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY', '').strip()

async def test_auth():
    """Test authentication and return debug info"""
    debug_info = []
    
    # Check if API key exists
    if not SWYFTX_API_KEY:
        return False, ["No API key found in secrets"]
    
    debug_info.append(f"API Key found: {SWYFTX_API_KEY[:15]}... (length: {len(SWYFTX_API_KEY)})")
    
    # Try auth
    url = "https://api.swyftx.com.au/auth/refresh/"
    headers = {"Content-Type": "application/json"}
    payload = {"apiKey": SWYFTX_API_KEY}
    
    try:
        debug_info.append(f"POST {url}")
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        debug_info.append(f"Status: {response.status_code}")
        debug_info.append(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("accessToken")
            if token:
                debug_info.append("✓ Token acquired!")
                return True, debug_info, token
            else:
                debug_info.append("✗ No accessToken in response")
                debug_info.append(f"Keys found: {list(data.keys())}")
        else:
            debug_info.append(f"✗ Auth failed with status {response.status_code}")
    except Exception as e:
        debug_info.append(f"✗ Exception: {str(e)}")
        debug_info.append(traceback.format_exc()[:500])
    
    return False, debug_info, None

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
    
    # Test auth and get debug info
    auth_success, debug_info, token = await test_auth()
    
    # Get prices
    prices = await get_prices()
    
    # Build message
    message = f"Daily Crypto Update\n"
    message += f"Time: {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Auth debug info
    message += "Auth Debug:\n"
    for line in debug_info:
        message += f"{line}\n"
    message += "\n"
    
    # If auth succeeded, try to get portfolio
    if auth_success and token:
        message += "Auth: SUCCESS\n"
        # Try portfolio with token
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get("https://api.swyftx.com.au/portfolio/", headers=headers, timeout=10)
            message += f"Portfolio status: {response.status_code}\n"
            if response.status_code == 200:
                portfolio = response.json()
                total = portfolio.get('totalAudBalance', 0)
                message += f"Portfolio total: ${float(total):,.2f} AUD\n"
            else:
                message += f"Portfolio error: {response.text[:200]}\n"
        except Exception as e:
            message += f"Portfolio exception: {str(e)}\n"
    else:
        message += "Auth: FAILED\n"
    
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
    
    # Split message if too long
    if len(message) > 4000:
        parts = [message[i:i+4000] for i in range(0, len(message), 4000)]
        for i, part in enumerate(parts):
            await bot.send_message(chat_id=CHAT_ID, text=f"Part {i+1}:\n{part}")
    else:
        await bot.send_message(chat_id=CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
