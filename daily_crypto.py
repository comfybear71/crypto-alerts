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
    
    # Step 1: Authenticate (get fresh token)
    auth_url = "https://api.swyftx.com.au/auth/refresh/"
    auth_response = requests.post(
        auth_url,
        json={"apiKey": SWYFTX_API_KEY},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if auth_response.status_code != 200:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID, 
            text=f"Auth failed: {auth_response.status_code}"
        )
        return
    
    token = auth_response.json().get("accessToken")
    headers = {"Authorization": f"Bearer {token}"}
    
    message = f"📊 Swyftx Portfolio\n"
    message += f"⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Step 2: Get portfolio (like swyftx-cli portfolio)
    try:
        portfolio_url = "https://api.swyftx.com.au/portfolio/"
        portfolio_resp = requests.get(portfolio_url, headers=headers, timeout=10)
        message += f"Portfolio endpoint: {portfolio_resp.status_code}\n"
        
        if portfolio_resp.status_code == 200:
            portfolio_data = portfolio_resp.json()
            message += f"Portfolio keys: {list(portfolio_data.keys())}\n"
            message += f"Data: {str(portfolio_data)[:500]}\n\n"
        else:
            message += f"Portfolio error: {portfolio_resp.text[:200]}\n\n"
    except Exception as e:
        message += f"Portfolio exception: {str(e)}\n\n"
    
    # Step 3: Try markets endpoint (like swyftx-cli markets)
    try:
        markets_url = "https://api.swyftx.com.au/markets/assets/"
        markets_resp = requests.get(markets_url, headers=headers, timeout=10)
        message += f"Markets assets: {markets_resp.status_code}\n"
        
        if markets_resp.status_code == 200:
            assets = markets_resp.json()
            message += f"Total assets: {len(assets)}\n"
            
            # Find BTC (ID 3)
            for asset in assets:
                if isinstance(asset, dict) and asset.get('id') == 3:
                    message += f"BTC data: {str(asset)[:400]}\n"
                    break
    except Exception as e:
        message += f"Markets error: {str(e)}\n"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
