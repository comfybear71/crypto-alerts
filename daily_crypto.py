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
    # Debug: Check secrets
    debug_info = []
    debug_info.append(f"TELEGRAM_BOT_TOKEN exists: {bool(TELEGRAM_BOT_TOKEN)}")
    debug_info.append(f"TELEGRAM_CHAT_ID exists: {bool(TELEGRAM_CHAT_ID)}")
    debug_info.append(f"SWYFTX_API_KEY exists: {bool(SWYFTX_API_KEY)}")
    
    # Try to init bot
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        debug_info.append("Bot initialized OK")
    except Exception as e:
        debug_info.append(f"Bot init error: {str(e)}")
        # Print to GitHub logs
        print("\n".join(debug_info))
        return
    
    # Build message
    message = "Daily Crypto Update\n"
    message += f"Time: {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    message += "Debug Info:\n" + "\n".join(debug_info) + "\n\n"
    
    # Try Swyftx
    if SWYFTX_API_KEY:
        try:
            auth_response = requests.post(
                "https://api.swyftx.com.au/auth/refresh/",
                json={"apiKey": SWYFTX_API_KEY},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            message += f"Swyftx auth: {auth_response.status_code}\n"
            
            if auth_response.status_code == 200:
                token = auth_response.json().get("accessToken")
                balance_response = requests.get(
                    "https://api.swyftx.com.au/user/balance/",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10
                )
                message += f"Swyftx balance: {balance_response.status_code}\n"
                if balance_response.status_code == 200:
                    balances = balance_response.json()
                    message += f"Assets: {len(balances)}\n"
        except Exception as e:
            message += f"Swyftx error: {str(e)[:100]}\n"
    else:
        message += "No Swyftx API key\n"
    
    message += "\n"
    
    # Get prices
    try:
        coins = ['bitcoin', 'ethereum', 'solana', 'ripple', 'cardano']
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(coins)}&vs_currencies=aud"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            prices = response.json()
            message += "Prices:\n"
            for coin in coins:
                if coin in prices:
                    price = prices[coin]['aud']
                    message += f"{coin.upper()}: ${price:,.2f}\n"
        else:
            message += f"Price API error: {response.status_code}\n"
    except Exception as e:
        message += f"Price error: {str(e)[:100]}"
    
    # Send to Telegram
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("SUCCESS: Message sent to Telegram")
    except Exception as e:
        print(f"FAILED to send: {str(e)}")
        print(f"Message was:\n{message}")

if __name__ == "__main__":
    asyncio.run(send_daily_update())
