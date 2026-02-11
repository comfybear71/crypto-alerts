import os
import requests
import asyncio
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '') or os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '') or os.getenv('CHAT_ID', '')

# HARDCODE YOUR API KEY HERE FOR TESTING (we'll remove it after)
# Replace this with your actual API key
TEST_API_KEY = "5QWI1sDraKpbnDWDDVBsyU4x68jA33pj6HYli50WTGXiW"

async def test_swyftx():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    message = "Swyftx API Test (Hardcoded Key)\n\n"
    
    try:
        url = "https://api.swyftx.com.au/auth/refresh/"
        response = requests.post(
            url, 
            json={"apiKey": TEST_API_KEY},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        message += f"Status: {response.status_code}\n"
        message += f"Response: {response.text[:300]}\n\n"
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("accessToken")
            if token:
                message += "✅ AUTH SUCCESS!\n"
                message += f"Token: {token[:40]}..."
                
                # Try to get portfolio
                headers = {"Authorization": f"Bearer {token}"}
                portfolio_resp = requests.get(
                    "https://api.swyftx.com.au/portfolio/",
                    headers=headers,
                    timeout=10
                )
                message += f"\n\nPortfolio Status: {portfolio_resp.status_code}"
                if portfolio_resp.status_code == 200:
                    portfolio = portfolio_resp.json()
                    total = portfolio.get('totalAudBalance', 0)
                    message += f"\nPortfolio Total: ${float(total):,.2f} AUD"
            else:
                message += "❌ No token in response"
        else:
            message += f"❌ Auth failed: {response.status_code}"
            
    except Exception as e:
        message += f"❌ Error: {str(e)}"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(test_swyftx())
