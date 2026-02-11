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
    
    # First, fetch all assets to get ID-to-name mapping
    assets_response = requests.get(
        "https://api.swyftx.com.au/markets/assets/",
        headers=headers,
        timeout=10
    )
    
    # Build ID to name mapping from API
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
    
    # Get prices
    prices = {}
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
                        asset_id = item.get('assetId')
                        rate = item.get('rate')
                        if asset_id and rate:
                            prices[asset_id] = float(rate)
    except Exception as e:
        print(f"Price error: {e}")
    
    # Build message
    message = f"📊 Daily Crypto Update\n"
    message += f"⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Show first 10 asset mappings for debugging
    message += "Asset ID Mapping (first 10):\n"
    for i, (aid, code) in enumerate(list(asset_map.items())[:10]):
        message += f"ID {aid}: {code}\n"
    message += "\n"
    
    # Calculate portfolio
    total_aud = 0
    holdings = []
    
    for item in balances:
        asset_id = item.get('assetId')
        balance = float(item.get('availableBalance', 0))
        
        if balance > 0:
            name = asset_map.get(asset_id, f"ID_{asset_id}")
            
            aud_value = 0
            if asset_id in prices:
                aud_value = balance * prices[asset_id]
            
            total_aud += aud_value
            holdings.append((name, balance, aud_value, asset_id))
    
    # Sort by value
    holdings.sort(key=lambda x: x[2], reverse=True)
    
    # Display
    message += "💰 Your Portfolio:\n\n"
    for name, qty, value, aid in holdings[:15]:
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
        
        message += f"• {name} (ID:{aid}): {qty_str} ({value_str})\n"
    
    message += f"\n💵 Total: ${total_aud:,.2f} AUD"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
