import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
SWYFTX_API_KEY = "VFYGZCDPG-f4ZXWzr6g0fKE9x2Z6nNPbbDSu_Ub7cjI1x"

# Coin mapping: Swyftx ID -> CoinGecko ID
COIN_MAP = {
    1: ('AUD', 'aud', 1.0),  # AUD is always 1.0
    3: ('BTC', 'bitcoin', None),
    5: ('ETH', 'ethereum', None),
    6: ('XRP', 'ripple', None),
    12: ('ADA', 'cardano', None),
    36: ('USD', 'usd', 1.0),  # USD approx
    53: ('USDC', 'usd-coin', None),
    73: ('DOGE', 'dogecoin', None),
    130: ('SOL', 'solana', None),
    405: ('LUNA', 'terra-luna', None),
    407: ('NEXO', 'nexo', None),
    438: ('SUI', 'sui', None),
    496: ('ENA', 'ethena', None),
    569: ('POL', 'polygon-ecosystem-token', None),
    635: ('XAUT', 'tether-gold', None),
}

async def send_daily_update():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Authenticate with Swyftx
    auth = requests.post(
        "https://api.swyftx.com.au/auth/refresh/",
        json={"apiKey": SWYFTX_API_KEY},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    token = auth.json().get("accessToken")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get balances from Swyftx
    balances_resp = requests.get(
        "https://api.swyftx.com.au/user/balance/",
        headers=headers,
        timeout=10
    )
    balances = {b['assetId']: float(b['availableBalance']) for b in balances_resp.json() if float(b['availableBalance']) > 0}
    
    # Get prices from CoinGecko
    cg_ids = [COIN_MAP[k][1] for k in balances.keys() if k in COIN_MAP and COIN_MAP[k][2] is None]
    prices = {}
    
    if cg_ids:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(cg_ids)}&vs_currencies=aud&include_24hr_change=true"
        cg_data = requests.get(url, timeout=10).json()
        
        for asset_id, (code, cg_id, fixed_price) in COIN_MAP.items():
            if fixed_price:
                prices[asset_id] = {'price': fixed_price, 'change': 0}
            elif cg_id in cg_data:
                prices[asset_id] = {
                    'price': cg_data[cg_id]['aud'],
                    'change': cg_data[cg_id].get('aud_24h_change', 0)
                }
    
    # Calculate portfolio
    total_aud = 0
    holdings = []
    
    for asset_id, balance in balances.items():
        if asset_id in COIN_MAP and asset_id in prices:
            code, _, _ = COIN_MAP[asset_id]
            value = balance * prices[asset_id]['price']
            change = prices[asset_id]['change']
            total_aud += value
            holdings.append((code, balance, value, change))
    
    # Sort by value
    holdings.sort(key=lambda x: x[2], reverse=True)
    
    # Build message
    message = f"📊 Swyftx Portfolio\n"
    message += f"⏰ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    
    for code, qty, value, change in holdings:
        emoji = "🟢" if change >= 0 else "🔴"
        
        # Format quantity
        if qty < 0.01:
            qty_str = f"{qty:.8f}"
        elif qty < 1:
            qty_str = f"{qty:.6f}"
        elif qty < 1000:
            qty_str = f"{qty:.2f}"
        else:
            qty_str = f"{qty:.0f}"
        
        # Format value
        if value > 1000:
            value_str = f"${value:,.0f}"
        elif value > 1:
            value_str = f"${value:.2f}"
        else:
            value_str = f"${value:.4f}"
        
        message += f"{emoji} {code}: {qty_str} ({value_str}) {change:+.2f}%\n"
    
    # Portfolio summary
    total_change = sum(h[2] * h[3] / 100 for h in holdings)
    portfolio_change_pct = (total_change / total_aud * 100) if total_aud > 0 else 0
    portfolio_emoji = "🟢" if portfolio_change_pct >= 0 else "🔴"
    
    message += f"\n💵 Total: ${total_aud:,.2f} AUD"
    message += f"\n📈 24h: {portfolio_emoji} {portfolio_change_pct:+.2f}%"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(send_daily_update())
