import os
import requests
import asyncio
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '') or os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '') or os.getenv('CHAT_ID', '')
API_KEY = "5QWI1sDraKpbnDWDDVBsyU4x68jA33pj6HYli50WTGXiW"

async def test_swyftx():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Get token
    auth_url = "https://api.swyftx.com.au/auth/refresh/"
    auth_response = requests.post(auth_url, json={"apiKey": API_KEY}, headers={"Content-Type": "application/json"})
    token = auth_response.json().get("accessToken")
    
    message = "Swyftx Debug\n\n"
    
    # Get balance
    balance_url = "https://api.swyftx.com.au/user/balance/"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(balance_url, headers=headers, timeout=10)
        data = response.json()
        
        message += f"Items: {len(data)}\n\n"
        
        # Show first 3 items raw
        for i, item in enumerate(data[:3]):
            message += f"Item {i+1}:\n"
            message += f"{str(item)}\n\n"
        
        # Try to extract with different field names
        message += "Trying to extract:\n"
        for item in data[:5]:
            if isinstance(item, dict):
                asset = item.get('asset') or item.get('code') or item.get('symbol') or item.get('name') or 'N/A'
                balance = item.get('balance') or item.get('quantity') or item.get('amount') or item.get('total') or 'N/A'
                value = item.get('audValue') or item.get('value') or item.get('audBalance') or item.get('aud') or 'N/A'
                
                message += f"{asset}: qty={balance}, aud={value}\n"
        
    except Exception as e:
        message += f"Error: {str(e)}"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(test_swyftx())
