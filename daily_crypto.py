import os
import requests
import asyncio
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '') or os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '') or os.getenv('CHAT_ID', '')
API_KEY = "5QWI1sDraKpbnDWDDVBsyU4x68jA33pj6HYli50WTGXiW"

# Common Swyftx asset IDs (we'll fetch the actual list)
ASSET_IDS = {
    1: 'BTC',
    2: 'ETH', 
    3: 'XRP',
    4: 'BCH',
    5: 'LTC',
    6: 'ADA',
    7: 'DOT',
    8: 'LINK',
    9: 'UNI',
    10: 'SOL',
    11: 'MATIC',
    12: 'DOGE',
    13: 'SHIB',
    14: 'AVAX',
    15: 'ATOM',
    16: 'ALGO',
    17: 'ETC',
    18: 'VET',
    19: 'FIL',
    20: 'TRX',
    21: 'EOS',
    22: 'AAVE',
    23: 'XTZ',
    24: 'XLM',
    25: 'NEO',
    26: 'WAVES',
    27: 'ZEC',
    28: 'DASH',
    29: 'XEM',
    30: 'OMG',
    31: 'ZRX',
    32: 'BAT',
    33: 'REP',
    34: 'GNT',
    35: 'SNT',
    36: 'KNC',
    37: 'BNT',
    38: 'CVC',
    39: 'STORJ',
    40: 'MANA',
    41: 'ANT',
    42: 'SNGLS',
    43: 'MLN',
    44: 'DGD',
    45: '1ST',
    46: 'NMR',
    47: 'EDG',
    48: 'RLC',
    49: 'GNO',
    50: 'TRST',
    51: 'SWT',
    52: 'WINGS',
    53: 'TAAS',
    54: 'DNT',
    55: 'CFI',
    56: 'PTOY',
    57: 'AST',
    58: 'HMQ',
    59: 'BCAP',
    60: 'NMR',
}

async def test_swyftx():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Get token
    auth_url = "https://api.swyftx.com.au/auth/refresh/"
    auth_response = requests.post(auth_url, json={"apiKey": API_KEY}, headers={"Content-Type": "application/json"})
    token = auth_response.json().get("accessToken")
    
    message = "Swyftx Balance\n\n"
    
    # Get balance
    balance_url = "https://api.swyftx.com.au/user/balance/"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(balance_url, headers=headers, timeout=10)
        data = response.json()
        
        total_aud = 0
        balances = []
        
        for item in data:
            asset_id = item.get('assetId')
            balance = float(item.get('availableBalance', 0))
            
            if balance > 0:
                asset_name = ASSET_IDS.get(asset_id, f"ID_{asset_id}")
                balances.append((asset_name, balance))
        
        if balances:
            message += "Your Holdings:\n"
            for name, qty in balances:
                message += f"• {name}: {qty:.8f}\n"
            message += f"\nTotal items with balance: {len(balances)}"
        else:
            message += "No balances found"
        
    except Exception as e:
        message += f"Error: {str(e)}"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(test_swyftx())
