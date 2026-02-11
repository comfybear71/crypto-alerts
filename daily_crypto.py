import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

COINS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'MATIC', 'LINK', 'UNI', 'LTC',
         'BCH', 'ETC', 'XLM', 'VET', 'FIL', 'TRX', 'EOS', 'AAVE', 'ATOM', 'XTZ']

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SWYFTX_TOKEN = os.getenv('SWYFTX_ACCESS_TOKEN', '').strip()

async def send_daily_update():
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Get portfolio using access token
    portfolio = None
    if SWYFTX_TOKEN:
        url = "https://api.swyftx.com.au/portfolio/balance/"
        headers = {"Authorization": f"Bearer {SWYFTX_TOKEN}"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                portfolio = response.json()
        except Exception as e:
            print(f"Portfolio error: {e}")
    
    # Get prices (public)
    rates_data = None
    try:
        response = requests.get("https://api.swyftx.com.au/markets/live-rates/AUD/", timeout=10)
        if response.status_code == 200:
            rates_data = response.json()
    except Exception as e:
        print(f"Price error: {e}")
    
    # Build message
    message = f"📊 *Daily Crypto Update*\n⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Portfolio
    if portfolio:
        message += "💰 *Your Portfolio*\n"
        total = portfolio.get('totalAudBalance', 0)
        available = portfolio.get('availableAudBalance', 0)
        message += f"Total: `${float(total):,.2f}` AUD\n"
        message += f"Available: `${float(available):,.2f}` AUD\n\n"
        
        holdings = portfolio.get('assets', [])
        if holdings:
            message += "*Holdings:*\n"
            for h in holdings[:10]:
                asset = h.get('asset', 'Unknown')
                qty = float(h.get('balance', 0))
                if qty > 0:
                    message += f"• {asset}: {qty:.4f}\n"
            message += "\n"
    else:
        message += "⚠️ *Portfolio not available*\n\n"
    
    # Prices
    if rates_data and isinstance(rates_data, list):
        prices = {}
        for rate in rates_data:
            if isinstance(rate, dict):
                coin = str(rate.get('asset', '')).upper()
                if coin in COINS:
                    prices[coin] = {
                        'price': float(rate.get('rate', 0)),
                        'change': float(rate.get('change24hPercent', 0))
                    }
        
        if prices:
            message += "*Market Prices (AUD):*\n"
            for coin in sorted(prices.keys()):
                p = prices[coin]
                emoji = "🟢" if p['change'] >= 0 else "🔴"
                if p['price'] > 1000:
                    price_str = f"${p['price']:,.2f}"
                else:
                    price_str = f"${p['price']:.2f}"
                message += f"{emoji} *{coin}*: {price_str} ({p['change']:+.2f}%)\n"
            message += f"\n📈 {len(prices)} coins"
    
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(send_daily_update())
