import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY', '')

# Asset ID to name mapping (update with your coins)
ASSET_MAP = {
    1: 'BTC', 2: 'ETH', 3: 'XRP', 5: 'LTC', 6: 'ADA', 
    10: 'SOL', 12: 'DOGE', 73: 'SUI', 130: 'LUNA', 
    405: 'ENA', 407: 'USDC', 438: 'NEXO', 496: 'POL', 
    569: 'XAUT', 635: 'XTZ'
}

async def send_daily_update():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    message = f"📊 Daily Crypto Update\n"
    message += f"⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Get Swyftx data
    auth_response = requests.post(
        "https://api.swyftx.com.au/auth/refresh/",
        json={"apiKey": SWYFTX_API_KEY},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    token = auth_response.json().get("accessToken")
    
    balance_response = requests.get(
        "https://api.swyftx.com.au/user/balance/",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    balances = balance_response.json()
    
    # Get CoinGecko prices
    coins = ['bitcoin', 'ethereum', 'solana', 'ripple', 'cardano', 'dogecoin',
             'litecoin', 'sui', 'terra-luna', 'ethena', 'usd-coin', 'nexo',
             'polygon-ecosystem-token', 'tether-gold', 'tezos']
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(coins)}&vs_currencies=aud"
    prices = requests.get(url, timeout=10).json()
    
    # Map CoinGecko IDs
    CG_MAP = {
        'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'XRP': 'ripple',
        'ADA': 'cardano', 'DOGE': 'dogecoin', 'LTC': 'litecoin', 'SUI': 'sui',
        'LUNA': 'terra-luna', 'ENA': 'ethena', 'USDC': 'usd-coin', 'NEXO': 'nexo',
        'POL': 'polygon-ecosystem-token', 'XAUT': 'tether-gold', 'XTZ': 'tezos'
    }
    
    # Calculate portfolio
    total_aud = 0
    holdings = []
    
    for item in balances:
        asset_id = item.get('assetId')
        balance = float(item.get('availableBalance', 0))
        
        if balance > 0:
            name = ASSET_MAP.get(asset_id, f"ID_{asset_id}")
            cg_id = CG_MAP.get(name)
            
            aud_value = 0
            if cg_id and cg_id in prices:
                price = prices[cg_id]['aud']
                aud_value = balance * price
            
            total_aud += aud_value
            holdings.append((name, balance, aud_value))
    
    # Sort by value
    holdings.sort(key=lambda x: x[2], reverse=True)
    
    # Display top 10
    message += "💰 Your Portfolio:\n\n"
    for name, qty, value in holdings[:10]:
        if value > 1000:
            value_str = f"${value:,.0f}"
        elif value > 1:
            value_str = f"${value:.2f}"
        else:
            value_str = f"${value:.4f}"
        
        if qty < 1:
            qty_str = f"{qty:.6f}"
        elif qty < 1000:
            qty_str = f"{qty:.2f}"
        else:
            qty_str = f"{qty:.0f}"
        
        message += f"• {name}: {qty_str} ({value_str})\n"
    
    message += f"\n💵 Total: ${total_aud:,.2f} AUD\n\n"
    
    # Market prices
    message += "📈 Market Prices:\n"
    for symbol, cg_id in [('BTC', 'bitcoin'), ('ETH', 'ethereum'), ('SOL', 'solana'), 
                          ('XRP', 'ripple'), ('ADA', 'cardano')]:
        if cg_id in prices:
            price = prices[cg_id]['aud']
            message += f"• {symbol}: ${price:,.2f}\n"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
