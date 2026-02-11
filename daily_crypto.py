import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

# Get secrets
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '') or os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '') or os.getenv('CHAT_ID', '')
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY', '')

async def send_daily_update():
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
    except Exception as e:
        print(f"Bot init error: {e}")
        return
    
    message = f"Daily Crypto Update\n"
    message += f"Time: {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Try Swyftx
    if SWYFTX_API_KEY:
        try:
            # Auth
            auth_response = requests.post(
                "https://api.swyftx.com.au/auth/refresh/",
                json={"apiKey": SWYFTX_API_KEY},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if auth_response.status_code == 200:
                token = auth_response.json().get("accessToken")
                
                # Get balances
                balance_response = requests.get(
                    "https://api.swyftx.com.au/user/balance/",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10
                )
                
                if balance_response.status_code == 200:
                    balances = balance_response.json()
                    message += f"Swyftx: {len(balances)} assets found\n\n"
                else:
                    message += f"Swyftx balance error: {balance_response.status_code}\n\n"
            else:
                message += f"Swyftx auth error: {auth_response.status_code}\n\n"
        except Exception as e:
            message += f"Swyftx error: {str(e)[:100]}\n\n"
    else:
        message += "Swyftx: No API key\n\n"
    
    # Get CoinGecko prices
    try:
        coins = ['bitcoin', 'ethereum', 'solana', 'ripple', 'cardano']
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(coins)}&vs_currencies=aud"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            prices = response.json()
            message += "Market Prices:\n"
            for coin in coins:
                if coin in prices:
                    price = prices[coin]['aud']
                    message += f"{coin.upper()}: ${price:,.2f}\n"
    except Exception as e:
        message += f"Price error: {str(e)[:100]}"
    
    # Send message
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("Message sent successfully")
    except Exception as e:
        print(f"Send error: {e}")

if __name__ == "__main__":
    asyncio.run(send_daily_update())
