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
    
    message = f"📊 Swyftx Data Test\n"
    message += f"⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Get user info
    try:
        user = requests.get("https://api.swyftx.com.au/user/", headers=headers, timeout=10)
        message += f"User Info: {user.status_code}\n"
        if user.status_code == 200:
            data = user.json()
            message += f"Email: {data.get('email', 'N/A')}\n"
            message += f"Name: {data.get('firstName', 'N/A')} {data.get('lastName', 'N/A')}\n\n"
    except Exception as e:
        message += f"User error: {str(e)}\n\n"
    
    # Get info endpoint
    try:
        info = requests.get("https://api.swyftx.com.au/info/", headers=headers, timeout=10)
        message += f"Info Endpoint: {info.status_code}\n"
        if info.status_code == 200:
            data = info.json()
            message += f"Keys: {list(data.keys())}\n"
            message += f"Data: {str(data)[:500]}\n\n"
    except Exception as e:
        message += f"Info error: {str(e)}\n\n"
    
    # Get balances (we know this works)
    try:
        balances = requests.get("https://api.swyftx.com.au/user/balance/", headers=headers, timeout=10)
        message += f"Balances: {balances.status_code}\n"
        if balances.status_code == 200:
            data = balances.json()
            # Show only non-zero balances
            non_zero = []
            for item in data:
                bal = float(item.get('availableBalance', 0))
                if bal > 0:
                    asset_id = item.get('assetId')
                    non_zero.append(f"ID {asset_id}: {bal:.6f}")
            
            message += f"Non-zero balances: {len(non_zero)}\n"
            for b in non_zero[:5]:
                message += f"• {b}\n"
    except Exception as e:
        message += f"Balance error: {str(e)}\n"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
