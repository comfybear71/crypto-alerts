import os
import requests
import asyncio
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '') or os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '') or os.getenv('CHAT_ID', '')

async def test_swyftx():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # List ALL environment variables that start with SWYFTX or contain API
    env_vars = []
    for key in os.environ.keys():
        if 'SWYFTX' in key or 'API' in key or 'TOKEN' in key:
            # Mask the actual values for security
            value = os.environ[key]
            masked = value[:10] + '...' if len(value) > 10 else value
            env_vars.append(f"{key}: {masked}")
    
    message = "Environment Variables Found:\n\n"
    if env_vars:
        message += "\n".join(env_vars)
    else:
        message += "No matching variables found"
    
    # Also try direct access with different variations
    message += "\n\nDirect Access Tests:\n"
    
    variations = [
        'SWYFTX_API_KEY',
        'SWYFTXAPIKEY',
        'swyftx_api_key',
        'SWYFTX-API-KEY',
        'API_KEY',
    ]
    
    for var in variations:
        value = os.getenv(var, '')
        message += f"{var}: {'FOUND' if value else 'NOT FOUND'}\n"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(test_swyftx())
