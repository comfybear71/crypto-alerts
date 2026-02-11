import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

# Get secrets from environment (passed by GitHub Actions)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
SWYFTX_API_KEY = os.getenv('SWYFTX_API_KEY', '')

# Your coin mapping based on actual wallet
ASSET_MAP = {
    1: 'BTC', 2: 'ETH', 3: 'XRP', 5: 'LTC', 6: 'ADA', 
    10: 'SOL', 12: 'DOGE', 13: 'SHIB', 18: 'VET', 24: 'XLM',
    73: 'SUI', 130: 'LUNA', 405: 'ENA', 407: 'USDC', 
    438: 'NEXO', 496: 'POL', 569: 'XAUT'
}

async def send_daily_update():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Get Swyftx token
    token = None
    if SWYFTX_API_KEY:
        try:
            auth_url = "https://api.swyftx.com.au/auth/refresh/"
            auth_response = requests.post(
                auth_url, 
                json={"apiKey": SWYFTX_API_KEY}, 
                headers={"Content-Type": "application/json"}, 
                timeout=10
            )
            if auth_response.status_code == 200:
                token = auth_response.json().get("accessToken")
        except Exception as e:
            print(f"Auth error: {e}")
    
    # Get Swyftx balances
    balances_data = []
    if token:
        try:
            balance_url = "https://api.swyftx.com.au/user/balance/"
            headers = {"Authorization": f"Bearer {token}"}
            balance_response = requests.get(balance_url, headers=headers, timeout=10)
            if balance_response.status_code == 200:
                balances_data = balance_response.json()
        except Exception as e:
            print(f"Balance error: {e}")
    
    # Get prices from CoinGecko
    prices = {}
    try:
        COINS = ['bitcoin', 'ethereum', 'solana', 'ripple', 'cardano', 'dogecoin',
                 'litecoin', 'matic', 'chainlink', 'uniswap', 'polkadot', 'avalanche-2',
                 'cosmos', 'stellar', 'vechain', 'sui', 'terra-luna', 'ethena',
                 'usd-coin', 'nexo', 'tether-gold']
        ids = ','.join(COINS)
        price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=aud&include_24hr_change=true"
        price_response = requests.get(price_url, timeout=10)
        if price_response.status_code == 200:
            prices = price_response.json()
    except Exception as e:
        print(f"Price error: {e}")
    
    # Build message
    message = f"📊 Daily Crypto Update\n"
    message += f"⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    # Swyftx Portfolio
    if balances_data:
        message += "💰 Swyftx Portfolio\n\n"
        
        total_aud = 0
        holdings = []
        
        # CoinGecko ID mapping
        cg_map = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'XRP': 'ripple', 
            'LTC': 'litecoin', 'ADA': 'cardano', 'SOL': 'solana',
            'DOGE': 'dogecoin', 'SHIB': 'shiba-inu', 'VET': 'vechain',
            'XLM': 'stellar', 'DOT': 'polkadot', 'LINK': 'chainlink',
            'UNI': 'uniswap', 'MATIC': 'matic', 'AVAX': 'avalanche-2',
            'ATOM': 'cosmos', 'ALGO': 'algorand', 'ETC': 'ethereum-classic',
            'FIL': 'filecoin', 'TRX': 'tron', 'EOS': 'eos',
            'AAVE': 'aave', 'XTZ': 'tezos', 'NEO': 'neo',
            'SUI': 'sui', 'LUNA': 'terra-luna', 'ENA': 'ethena',
            'USDC': 'usd-coin', 'NEXO': 'nexo', 'POL': 'polygon-ecosystem-token',
            'XAUT': 'tether-gold'
        }
        
        for item in balances_data:
            asset_id = item.get('assetId')
            balance = float(item.get('availableBalance', 0))
            
            if balance > 0:
                asset_name = ASSET_MAP.get(asset_id, f"ID_{asset_id}")
                
                # Get AUD value
                aud_value = 0
                change = 0
                cg_id = cg_map.get(asset_name)
                
                if cg_id and cg_id in prices:
                    price_aud = prices[cg_id].get('aud', 0)
                    change = prices[cg_id].get('aud_24h_change', 0)
                    aud_value = balance * price_aud
                
                total_aud += aud_value
                holdings.append((asset_name, balance, aud_value, change))
        
        # Sort by value and display
        holdings.sort(key=lambda x: x[2], reverse=True)
        for name, qty, value, change in holdings:
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
            
            emoji = "🟢" if change >= 0 else "🔴"
            message += f"{emoji} {name}: {qty_str} ({value_str})\n"
        
        message += f"\n💵 Total: ${total_aud:,.2f} AUD\n\n"
    else:
        message += "💰 Portfolio: Not available\n\n"
    
    # Market Prices
    if prices:
        message += "📈 Market Prices:\n"
        display_coins = {
            'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL',
            'ripple': 'XRP', 'cardano': 'ADA', 'dogecoin': 'DOGE',
            'litecoin': 'LTC', 'matic': 'MATIC', 'chainlink': 'LINK',
            'uniswap': 'UNI', 'polkadot': 'DOT', 'avalanche-2': 'AVAX',
            'cosmos': 'ATOM', 'stellar': 'XLM', 'vechain': 'VET',
            'sui': 'SUI', 'terra-luna': 'LUNA', 'ethena': 'ENA'
        }
        
        for coin_id, symbol in display_coins.items():
            if coin_id in prices:
                p = prices[coin_id]
                price = float(p['aud'])
                change = float(p.get('aud_24h_change', 0))
                price_str = f"${price:,.2f}" if price > 1000 else f"${price:.4f}"
                emoji = "🟢" if change >= 0 else "🔴"
                message += f"{emoji} {symbol}: {price_str} ({change:+.2f}%)\n"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(send_daily_update())
