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
    
    message = f"📊 Swyftx BTC Price Test\n"
    message += f"⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Try to get BTC price using different methods
    
    # Method 1: Try assets endpoint for BTC (ID 3)
    try:
        btc_asset = requests.get(
            "https://api.swyftx.com.au/markets/assets/3/",  # BTC is ID 3
            headers=headers,
            timeout=10
        )
        message += f"Method 1 (assets/3/): {btc_asset.status_code}\n"
        if btc_asset.status_code == 200:
            data = btc_asset.json()
            message += f"Data: {str(data)[:500]}\n\n"
        else:
            message += f"Error: {btc_asset.text[:200]}\n\n"
    except Exception as e:
        message += f"Method 1 error: {str(e)}\n\n"
    
    # Method 2: Try user/balance to see BTC balance
    try:
        balances = requests.get(
            "https://api.swyftx.com.au/user/balance/",
            headers=headers,
            timeout=10
        )
        message += f"Method 2 (user/balance): {balances.status_code}\n"
        if balances.status_code == 200:
            data = balances.json()
            # Find BTC (ID 3)
            for item in data:
                if item.get('assetId') == 3:
                    message += f"BTC Balance: {item.get('availableBalance')}\n\n"
                    break
    except Exception as e:
        message += f"Method 2 error: {str(e)}\n\n"
    
    # Method 3: Try any working endpoint
    endpoints = [
        "https://api.swyftx.com.au/user/",
        "https://api.swyftx.com.au/account/",
        "https://api.swyftx.com.au/info/",
    ]
    
    message += "Method 3 (Testing endpoints):\n"
    for url in endpoints:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            message += f"{url.split('/')[-2]}: {resp.status_code}\n"
        except Exception as e:
            message += f"{url.split('/')[-2]}: Error\n"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
