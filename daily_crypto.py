import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY', '')

async def test_triggers():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Authenticate
    auth = requests.post(
        "https://api.swyftx.com.au/auth/refresh/",
        json={"apiKey": SWYFTX_API_KEY},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    token = auth.json().get("accessToken")
    headers = {"Authorization": f"Bearer {token}"}
    
    message = f"📊 Swyftx Triggers Test\n"
    message += f"⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Test trigger endpoints
    trigger_endpoints = [
        "https://api.swyftx.com.au/triggers/",
        "https://api.swyftx.com.au/triggers/list/",
        "https://api.swyftx.com.au/orders/triggers/",
        "https://api.swyftx.com.au/user/triggers/",
    ]
    
    message += "Testing Trigger Endpoints:\n\n"
    
    for url in trigger_endpoints:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            message += f"{url.split('/')[-2]}: {resp.status_code}\n"
            
            if resp.status_code == 200:
                data = resp.json()
                message += f"✅ Data: {str(data)[:300]}\n\n"
            elif resp.status_code != 404:
                message += f"Response: {resp.text[:200]}\n\n"
                
        except Exception as e:
            message += f"{url.split('/')[-2]}: Error - {str(e)[:50]}\n\n"
    
    # Also test creating a trigger (if endpoint exists)
    message += "Testing Trigger Creation:\n"
    
    # Try POST to create a simple price alert
    try:
        create_url = "https://api.swyftx.com.au/triggers/"
        trigger_data = {
            "assetId": 3,  # BTC
            "triggerType": "price",  # or "market"
            "condition": "above",  # or "below"
            "price": 100000,  # Trigger when BTC > $100k AUD
            "orderType": "market",  # or "limit"
            "side": "sell",  # or "buy"
            "amount": 0.001  # Amount to trade
        }
        
        create_resp = requests.post(
            create_url,
            json=trigger_data,
            headers=headers,
            timeout=10
        )
        
        message += f"Create trigger: {create_resp.status_code}\n"
        message += f"Response: {create_resp.text[:300]}\n"
        
    except Exception as e:
        message += f"Create error: {str(e)[:100]}\n"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(test_triggers())
