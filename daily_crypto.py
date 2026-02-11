import os
import requests
import asyncio
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '') or os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '') or os.getenv('CHAT_ID', '')
API_KEY = "5QWI1sDraKpbnDWDDVBsyU4x68jA33pj6HYli50WTGXiW"

async def test_swyftx():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # First, get token
    auth_url = "https://api.swyftx.com.au/auth/refresh/"
    auth_response = requests.post(auth_url, json={"apiKey": API_KEY}, headers={"Content-Type": "application/json"})
    token = auth_response.json().get("accessToken")
    
    message = "Swyftx Portfolio Test\n\n"
    message += f"✅ Auth Success\n"
    message += f"Token: {token[:30]}...\n\n"
    
    # Try different portfolio endpoints
    endpoints = [
        "https://api.swyftx.com.au/portfolio/",
        "https://api.swyftx.com.au/portfolio/balance/",
        "https://api.swyftx.com.au/account/balance/",
        "https://api.swyftx.com.au/user/balance/",
        "https://api.swyftx.com.au/wallet/balance/",
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for url in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            message += f"{url.split('/')[-2]}/: {response.status_code}\n"
            
            if response.status_code == 200:
                data = response.json()
                message += f"✅ SUCCESS! Keys: {list(data.keys())[:5]}\n"
                
                # Try to get balance
                total = (data.get('totalAudBalance') or 
                        data.get('totalBalance') or 
                        data.get('balance') or 
                        data.get('audBalance') or 0)
                message += f"Total: ${float(total):,.2f} AUD\n\n"
                break
        except Exception as e:
            message += f"Error: {str(e)[:50]}\n"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(test_swyftx())
