import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
SWYFTX_API_KEY = "VFYGZCDPG-f4ZXWzr6g0fKE9x2Z6nNPbbDSu_Ub7cjI1x"

async def send_daily_update():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Get Swyftx token
    auth_response = requests.post(
        "https://api.swyftx.com.au/auth/refresh/",
        json={"apiKey": SWYFTX_API_KEY},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    token = auth_response.json().get("accessToken")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get asset mapping
    assets_response = requests.get(
        "https://api.swyftx.com.au/markets/assets/",
        headers=headers,
        timeout=10
    )
    
    asset_map = {}
    if assets_response.status_code == 200:
        assets = assets_response.json()
        for asset in assets:
            if isinstance(asset, dict):
                asset_id = asset.get('id') or asset.get('assetId')
                code = asset.get('code') or asset.get('asset') or asset.get('symbol')
                if asset_id and code:
                    asset_map[asset_id] = code
    
    # Get balances
    balance_response = requests.get(
        "https://api.swyftx.com.au/user/balance/",
        headers=headers,
        timeout=10
    )
    balances = balance_response.json()
    
    # Get prices and 24h change from Swyftx
    price_data = {}  # asset_id -> {rate, change24h}
    try:
        rates_response = requests.get(
            "https://api.swyftx.com.au/markets/live-rates/AUD/",
            headers=headers,
            timeout=10
        )
        
        if rates_response.status_code == 200:
            rates_data = rates_response.json()
            
            if isinstance(rates_data, list):
                for item in rates_data:
                    if isinstance(item, dict):
                        asset_id = item.get('assetId') or item.get('id')
                        rate = item.get('rate') or item.get('price')
                        change24h = item.get('change24h') or item.get('change24hPercent') or item.get('percentChange24h')
                        
                        if asset_id and rate:
                            price_data[asset_id] = {
                                'rate': float(rate),
                                'change24h': float(change24h) if change24h else 0
                            }
    except Exception as e:
        print(f"Price fetch error: {e}")
    
    # Build message
    message = f"📊 Daily Crypto Update\n"
    message += f"⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Calculate portfolio
    total_aud = 0
    total_change_24h = 0  # Weighted 24h change
    holdings = []
    
    for item in balances:
        asset_id = item.get('assetId')
        balance = float(item.get('availableBalance', 0))
        
        if balance > 0:
            code = asset_map.get(asset_id, f"ID_{asset_id}")
            
            # Get price and 24h change
            aud_value = 0
            change_24h = 0
            
            if code == 'AUD':
                aud_value = balance
                change_24h = 0
            elif asset_id in price_data:
                aud_value = balance * price_data[asset_id]['rate']
                change_24h = price_data[asset_id]['change24h']
            
            total_aud += aud_value
            if aud_value > 0:
                total_change_24h += (aud_value * change_24h / 100)  # Convert % to absolute
            
            holdings.append((code, balance, aud_value, change_24h))
    
    # Calculate overall portfolio 24h change %
    portfolio_change_pct = (total_change_24h / total_aud * 100) if total_aud > 0 else 0
    
    # Sort by value
    holdings.sort(key=lambda x: x[2], reverse=True)
    
    # Display portfolio
    message += "💰 Your Swyftx Portfolio:\n\n"
    for code, qty, value, change in holdings:
        # Format value
        if value > 1000:
            value_str = f"${value:,.0f}"
        elif value > 1:
            value_str = f"${value:.2f}"
        else:
            value_str = f"${value:.4f}"
        
        # Format quantity
        if qty < 0.01:
            qty_str = f"{qty:.8f}"
        elif qty < 1:
            qty_str = f"{qty:.6f}"
        elif qty < 1000:
            qty_str = f"{qty:.2f}"
        else:
            qty_str = f"{qty:.0f}"
        
        # Format 24h change with emoji
        emoji = "🟢" if change >= 0 else "🔴"
        
        message += f"• {code}: {qty_str} ({value_str}) {emoji} {change:+.2f}%\n"
    
    # Overall portfolio change
    portfolio_emoji = "🟢" if portfolio_change_pct >= 0 else "🔴"
    message += f"\n💵 Total: ${total_aud:,.2f} AUD"
    message += f"\n📈 24h Change: {portfolio_emoji} {portfolio_change_pct:+.2f}%"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
