import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

# Expanded coin list - add any coins you want here
COINS = [
    'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'MATIC', 'LINK', 'UNI', 'LTC',
    'BCH', 'ETC', 'XLM', 'VET', 'FIL', 'TRX', 'EOS', 'AAVE', 'ATOM', 'XTZ',
    'ALGO', 'AVAX', 'BNB', 'DOGE', 'SHIB', 'PEPE', 'TON', 'TRUMP', 'SUI', 'RAY'
]

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_daily_update():
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Get prices from Swyftx
    url = "https://api.swyftx.com.au/markets/live-rates/AUD/"
    
    try:
        response = requests.get(url, timeout=30)
        data = response.json()
    except Exception as e:
        await bot.send_message(chat_id=CHAT_ID, text=f"❌ Error fetching data: {e}")
        return
    
    # Build price lookup - check multiple possible formats
    prices = {}
    available_coins = []
    
    for key, info in data.items():
        if isinstance(info, dict):
            # Try to find coin code in different fields
            coin_code = info.get('asset') or info.get('code') or info.get('symbol') or key
            if coin_code:
                coin_code = str(coin_code).upper()
                available_coins.append(coin_code)
                
                if coin_code in [c.upper() for c in COINS]:
                    prices[coin_code] = {
                        'price': info.get('rate') or info.get('price') or info.get('last') or 0,
                        'change': info.get('change24hPercent') or info.get('change24h') or info.get('percentChange') or 0,
                        'high': info.get('high24h') or info.get('high') or 0,
                        'low': info.get('low24h') or info.get('low') or 0
                    }
    
    # Debug: Show available coins if no matches found
    if not prices:
        debug_msg = f"⚠️ No coins matched. Available coins (first 20): {', '.join(sorted(available_coins)[:20])}"
        await bot.send_message(chat_id=CHAT_ID, text=debug_msg)
        return
    
    # Sort by coin code
    sorted_coins = sorted(prices.keys())
    
    # Format message
    message = "📊 *Daily Crypto Prices (AUD)*\n"
    message += f"⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    for coin in sorted_coins:
        p = prices[coin]
        price = float(p['price']) if p['price'] else 0
        change = float(p['change']) if p['change'] else 0
        
        emoji = "🟢" if change >= 0 else "🔴"
        
        if price > 1000:
            price_str = f"${price:,.2f}"
        elif price > 1:
            price_str = f"${price:.2f}"
        else:
            price_str = f"${price:.4f}"
            
        message += f"{emoji} *{coin}*: {price_str} ({change:+.2f}%)\n"
    
    message += f"\n📈 *{len(prices)} coins tracked*"
    
    # Send to Telegram
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(send_daily_update())
