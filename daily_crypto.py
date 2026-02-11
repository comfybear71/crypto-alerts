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
    
    message = "Swyftx Balance Test\n\n"
    
    # Get balance
    balance_url = "https://api.swyftx.com.au/user/balance/"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(balance_url, headers=headers, timeout=10)
        message += f"Status: {response.status_code}\n\n"
        
        if response.status_code == 200:
            data = response.json()
            message += f"Data type: {type(data)}\n"
            
            if isinstance(data, list):
                message += f"Items: {len(data)}\n\n"
                message += "Your Balances:\n"
                
                total_aud = 0
                for item in data[:10]:  # First 10 items
                    if isinstance(item, dict):
                        asset = item.get('asset') or item.get('code') or item.get('symbol') or 'Unknown'
                        qty = float(item.get('balance') or item.get('quantity') or item.get('amount') or 0)
                        aud_value = float(item.get('audValue') or item.get('value') or item.get('aud') or 0)
                        
                        if qty > 0:
                            message += f"• {asset}: {qty:.4f} (${aud_value:,.2f} AUD)\n"
                            total_aud += aud_value
                
                message += f"\nTotal Value: ${total_aud:,.2f} AUD"
                
            elif isinstance(data, dict):
                message += f"Keys: {list(data.keys())}\n"
                message += f"Data: {str(data)[:300]}"
        else:
            message += f"Error: {response.text[:200]}"
            
    except Exception as e:
        message += f"Exception: {str(e)}"
        import traceback
        message += f"\n{traceback.format_exc()[:500]}"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(test_swyftx())
