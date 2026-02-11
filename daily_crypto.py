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
    
    # Get live rates in AUD (asset ID 1 = AUD)
    price_data = {}
    try:
        rates_response = requests.get(
            "https://api.swyftx.com.au/markets/live-rates/1/",  # Correct endpoint for AUD
            headers=headers,
            timeout=10
        )
        
        if rates_response.status_code == 200:
            data = rates_response.json()
            
            # The response is a dict with asset IDs as keys
            if isinstance(data, dict):
                for asset_id_str, rate_info in data.items():
                    try:
                        asset_id = int(asset_id_str)
                        if isinstance(rate_info, dict):
                            price_data[asset_id] = {
                                'rate': float(rate_info.get('rate', 0)),
                                'change24h': float(rate_info.get('change24h', 0) or rate_info.get('change24hPercent', 0) or 0),
                                'ask': float(rate_info.get('ask', 0)),
                                'bid': float(rate_info.get('bid', 0))
                            }
                    except (ValueError, TypeError):
                        continue
            
            # Debug info
            debug_info = f"Found {len(price_data)} prices\n"
            if price_data:
                sample = list(price_data.items())[:3]
                for aid, pdata in sample:
                    debug_info += f"ID {aid}: rate={pdata['rate']}, 24h={pdata['change24h']}%\n"
        else:
            debug_info = f"Rates API returned {rates_response.status_code}\n"
    except Exception as e:
        debug_info = f"Error: {str(e)[:100]}\n"
    
    # Build message
    message = f"📊 Daily Crypto Update\n"
    message += f"⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    message += f"Debug: {debug_info}\n"
    
    # Calculate portfolio
    total_aud = 0
    holdings = []
    
    for item in balances:
        asset_id = item.get('assetId')
        balance = float(item.get('availableBalance', 0))
        
        if balance > 0:
            code = asset_map.get(asset_id, f"ID_{asset_id}")
            
            aud_value = 0
            change_24h = 0
            
            if code == 'AUD':
                aud_value = balance
                change_24h = 0
            elif asset_id in price_data:
                aud_value = balance * price_data[asset_id]['rate']
                change_24h = price_data[asset_id]['change24h']
            
            total_aud += aud_value
            holdings.append((code, balance, aud_value, change_24h))
    
    # Sort by value
    holdings.sort(key=lambda x: x[2], reverse=True)
    
    # Display
    message += "💰 Your Portfolio:\n\n"
    for code, qty, value, change in holdings[:15]:
        if value > 1000:
            value_str = f"${value:,.0f}"
        elif value > 1:
            value_str = f"${value:.2f}"
        else:
            value_str = f"${value:.4f}"
        
        if qty < 0.01:
            qty_str = f"{qty:.8f}"
        elif qty < 1:
            qty_str = f"{qty:.6f}"
        elif qty < 1000:
            qty_str = f"{qty:.2f}"
        else:
            qty_str = f"{qty:.0f}"
        
        emoji = "🟢" if change >= 0 else "🔴"
        message += f"• {code}: {qty_str} ({value_str}) {emoji} {change:+.2f}%\n"
    
    message += f"\n💵 Total: ${total_aud:,.2f} AUD"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
