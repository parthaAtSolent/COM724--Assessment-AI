from datetime import date, timedelta


TODAY = date.today().strftime("%Y-%m-%d")
START_DATE = "2020-01-01"

# print(f"Data will be fetched from {START_DATE} to {TODAY}")

CRYPTOS = {
    'BTC-USD': 'Bitcoin',
    'ETH-USD': 'Ethereum',
    'BNB-USD': 'Binance Coin',
    'XRP-USD': 'Ripple',
    'SOL-USD': 'Solana',
    'ADA-USD': 'Cardano',
    'DOGE-USD': 'Dogecoin',
    'DOT-USD': 'Polkadot',
    'AVAX-USD': 'Avalanche',
    'MATIC-USD': 'Polygon',
    'SHIB-USD': 'Shiba Inu',
    'LTC-USD': 'Litecoin',
    'TRX-USD': 'TRON',
    'BCH-USD': 'Bitcoin Cash',
    'ATOM-USD': 'Cosmos',
    'LINK-USD': 'Chainlink',
    'XLM-USD': 'Stellar',
    'UNI-USD': 'Uniswap',
    'XMR-USD': 'Monero',
    'ETC-USD': 'Ethereum Classic',
    'NEAR-USD': 'NEAR Protocol',
    'VET-USD': 'VeChain',
    'ICP-USD': 'Internet Computer',
    'FIL-USD': 'Filecoin',
    'EOS-USD': 'EOS',
    'APT-USD': 'Aptos',
    'SAND-USD': 'The Sandbox',
    'AAVE-USD': 'Aave',
    'MANA-USD': 'Decentraland',
    'THETA-USD': 'Theta Network',
    'EGLD-USD': 'MultiversX (Elrond)'
}
