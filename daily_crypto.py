import os
import requests
import asyncio
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '') or os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '') or os.getenv('CHAT_ID', '')
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY', '')

async def test_swyftx():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Simple test - just try to authenticate
    message = "Swyftx API Test\n\n"
    
    if not SWYFTX_API_KEY:
        message += "ERROR: No API key found"
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        return
    
    # Try auth
    try:
        url = "https://api.swyftx.com.au/auth/refresh/"
        response = requests.post(
            url, 
            json={"apiKey": SWYFTX_API_KEY},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        message += f"Auth URL: {url}\n"
        message += f"Status Code: {response.status_code}\n"
        message += f"Response: {response.text[:500]}\n\n"
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("accessToken")
            if token:
                message += "SUCCESS! Token received.\n"
                message += f"Token starts with: {token[:30]}..."
            else:
                message += "FAILED: No accessToken in response\n"
                message += f"Keys found: {list(data.keys())}"
        else:
            message += f"FAILED: HTTP {response.status_code}"
            
    except Exception as e:
        message += f"ERROR: {str(e)}"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(test_swyftx())
