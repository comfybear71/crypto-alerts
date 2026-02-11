import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '') or os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '') or os.getenv('CHAT_ID', '')

# Get API key from secret or use hardcoded for now
API_KEY = os.getenv('SWYFTX_API_KEY', '') or "5QWI1sDraKpbnDWDDVBsyU4x68jA33pj6HYli50WTGXiW"

# Asset ID mapping (common coins)
ASSET_IDS = {
    1: 'BTC', 2: 'ETH', 3: 'XRP', 4: 'BCH', 5: 'LTC',
    6: 'ADA', 7: 'DOT', 8: 'LINK', 9: 'UNI', 10: 'SOL',
    11: 'MATIC', 12: 'DOGE', 13: 'SHIB', 14: 'AVAX', 15: 'ATOM',
    16: 'ALGO', 17: 'ETC', 18: 'VET', 19: 'FIL', 20: 'TRX',
    21: 'EOS', 22: 'AAVE', 23: 'XTZ', 24: 'XLM', 25: 'NEO',
    26: 'WAVES', 27: 'ZEC', 28: 'DASH', 29: 'XEM', 30: 'OMG',
    31: 'ZRX', 32: 'BAT', 33: 'REP', 34: 'GNT', 35: 'SNT',
    36: 'KNC', 37: 'BNT', 38: 'CVC', 39: 'STORJ', 40: 'MANA',
    41: 'ANT', 42: 'SNGLS', 43: 'MLN', 44: 'DGD', 45: '1ST',
    46: 'NMR', 47: 'EDG', 48: 'RLC', 49: 'GNO', 50: 'TRST',
    51: 'SWT', 52: 'WINGS', 53: 'TAAS', 54: 'DNT', 55: 'CFI',
    56: 'PTOY', 57: 'AST', 58: 'HMQ', 59: 'BCAP', 60: 'NMR',
}

async def send_daily_update():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Get Swyftx token
    auth_url = "https://api.swyftx.com.au/auth/refresh/"
    auth_response = requests.post(auth_url, json={"apiKey": API_KEY}, headers={"Content-Type": "application/json"}, timeout=10)
    token = auth_response.json().get("accessToken")
    
    # Get balances
    balance_url = "https://api.swyftx.com.au/user/balance/"
    headers = {"Authorization": f"Bearer {token}"}
    balance_response = requests.get(balance_url, headers=headers, timeout=10)
    balances_data = balance_response.json()
    
    # Get prices from CoinGecko
    prices = {}
    try:
        COINS = ['bitcoin', 'ethereum', 'solana', 'ripple', 'cardano', 'polkadot', 
                 'matic', 'chainlink', 'uniswap', 'litecoin', 'dogecoin', 'shiba-inu',
                 'avalanche-2', 'cosmos', 'algorand', 'ethereum-classic', 'vechain',
                 'filecoin', 'tron', 'eos', 'aave', 'tezos', 'stellar', 'neo',
                 'waves', 'zcash', 'dash', 'nem', 'omisego', '0x', 'basic-attention-token',
                 'kyber-network', 'bancor', 'civic', 'storj', 'decentraland', 'aragon',
                 'singulardtv', 'melon', 'digixdao', 'firstblood', 'numeraire',
                 'edgeless', 'iexec-rlc', 'gnosis', 'trustcoin', 'swarm-city', 'wings']
        ids = ','.join(COINS)
        price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=aud"
        price_response = requests.get(price_url, timeout=10)
        prices = price_response.json()
    except Exception as e:
        print(f"Price error: {e}")
    
    # Build message
    message = f"Daily Crypto Update\n"
    message += f"Time: {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Swyftx Portfolio
    message += "💰 Swyftx Portfolio\n\n"
    
    total_aud = 0
    holdings = []
    
    for item in balances_data:
        asset_id = item.get('assetId')
        balance = float(item.get('availableBalance', 0))
        
        if balance > 0:
            asset_name = ASSET_IDS.get(asset_id, f"ID_{asset_id}")
            
            # Try to get AUD value from CoinGecko
            aud_value = 0
            # Map asset name to CoinGecko ID
            cg_map = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'XRP': 'ripple', 'BCH': 'bitcoin-cash',
                'LTC': 'litecoin', 'ADA': 'cardano', 'DOT': 'polkadot', 'LINK': 'chainlink',
                'UNI': 'uniswap', 'SOL': 'solana', 'MATIC': 'matic', 'DOGE': 'dogecoin',
                'SHIB': 'shiba-inu', 'AVAX': 'avalanche-2', 'ATOM': 'cosmos', 'ALGO': 'algorand',
                'ETC': 'ethereum-classic', 'VET': 'vechain', 'FIL': 'filecoin', 'TRX': 'tron',
                'EOS': 'eos', 'AAVE': 'aave', 'XTZ': 'tezos', 'XLM': 'stellar', 'NEO': 'neo',
                'WAVES': 'waves', 'ZEC': 'zcash', 'DASH': 'dash', 'XEM': 'nem', 'OMG': 'omisego',
                'ZRX': '0x', 'BAT': 'basic-attention-token', 'KNC': 'kyber-network', 'BNT': 'bancor',
                'CVC': 'civic', 'STORJ': 'storj', 'MANA': 'decentraland', 'ANT': 'aragon',
                'SNGLS': 'singulardtv', 'MLN': 'melon', 'DGD': 'digixdao', '1ST': 'firstblood',
                'NMR': 'numeraire', 'EDG': 'edgeless', 'RLC': 'iexec-rlc', 'GNO': 'gnosis',
                'TRST': 'trustcoin', 'SWT': 'swarm-city', 'WINGS': 'wings', 'TAAS': 'taas',
            }
            
            cg_id = cg_map.get(asset_name)
            if cg_id and cg_id in prices:
                price_aud = prices[cg_id].get('aud', 0)
                aud_value = balance * price_aud
            
            total_aud += aud_value
            holdings.append((asset_name, balance, aud_value))
    
    # Show top holdings
    holdings.sort(key=lambda x: x[2], reverse=True)
    for name, qty, value in holdings[:10]:
        if value > 1000:
            value_str = f"${value:,.0f}"
        elif value > 1:
            value_str = f"${value:.2f}"
        else:
            value_str = f"${value:.4f}"
        
        if qty < 1:
            qty_str = f"{qty:.6f}"
        elif qty < 1000:
            qty_str = f"{qty:.2f}"
        else:
            qty_str = f"{qty:.0f}"
        
        message += f"• {name}: {qty_str} ({value_str} AUD)\n"
    
    message += f"\nTotal Value: ${total_aud:,.2f} AUD\n\n"
    
    # Market Prices
    message += "📈 Market Prices (AUD):\n"
    coin_map = {
        'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL',
        'ripple': 'XRP', 'cardano': 'ADA', 'polkadot': 'DOT',
        'matic': 'MATIC', 'chainlink': 'LINK', 'uniswap': 'UNI',
        'litecoin': 'LTC'
    }
    
    for coin_id, symbol in coin_map.items():
        if coin_id in prices:
            p = prices[coin_id]
            price = float(p['aud'])
            change = float(p.get('aud_24h_change', 0))
            price_str = f"${price:,.2f}" if price > 1000 else f"${price:.4f}"
            message += f"{symbol}: {price_str} ({change:+.2f}%)\n"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
