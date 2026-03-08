import streamlit as st
import base64
import os


def load_custom_css(css_path: str):
    """Load external CSS file for custom Streamlit styling."""
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ CSS file not found at: {css_path}")


def display_logo(logo_path: str):
    """Display app logo with blur and rounded background."""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            encoded_logo = base64.b64encode(f.read()).decode()

        st.markdown(
            f"""
                <div style="display: flex; justify-content: flex-start;">
                    <div style="height: 120px; width: 120px; 
                                border-radius: 20px;">
                        <img src="data:image/png;base64,{encoded_logo}" alt="Logo" style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning(f"⚠️ Logo not found at: {logo_path}")


def get_crypto_logo_url(selected_name):
    """Get cryptocurrency logo URL based on the selected name."""

    # Mapping of cryptocurrency names to their CoinGecko image IDs
    logo_url_mapping = {
        'Bitcoin': 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png',
        'Ethereum': 'https://assets.coingecko.com/coins/images/279/large/ethereum.png',
        'Binance Coin': 'https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png',
        'Ripple': 'https://assets.coingecko.com/coins/images/44/large/xrp-symbol-white-128.png',
        'Solana': 'https://assets.coingecko.com/coins/images/4128/large/solana.png',
        'Cardano': 'https://assets.coingecko.com/coins/images/975/large/cardano.png',
        'Dogecoin': 'https://assets.coingecko.com/coins/images/5/large/dogecoin.png',
        'Polkadot': 'https://assets.coingecko.com/coins/images/12171/large/polkadot.png',
        'Avalanche': 'https://assets.coingecko.com/coins/images/12559/large/Avalanche_Circle_RedWhite.png',
        'Polygon': 'https://assets.coingecko.com/coins/images/4713/large/matic-token-icon.png',
        'Shiba Inu': 'https://assets.coingecko.com/coins/images/11939/large/shiba.png',
        'Litecoin': 'https://assets.coingecko.com/coins/images/2/large/litecoin.png',
        'TRON': 'https://assets.coingecko.com/coins/images/1094/large/tron-logo.png',
        'Bitcoin Cash': 'https://assets.coingecko.com/coins/images/780/large/bitcoin-cash-circle.png',
        'Cosmos': 'https://assets.coingecko.com/coins/images/1481/large/cosmos_hub.png',
        'Chainlink': 'https://assets.coingecko.com/coins/images/877/large/chainlink-new-logo.png',
        'Stellar': 'https://assets.coingecko.com/coins/images/100/large/Stellar_symbol_black_RGB.png',
        'Uniswap': 'https://assets.coingecko.com/coins/images/12504/large/uniswap-uni.png',
        'Monero': 'https://assets.coingecko.com/coins/images/69/large/monero_logo.png',
        'Ethereum Classic': 'https://assets.coingecko.com/coins/images/453/large/ethereum-classic-logo.png',
        'NEAR Protocol': 'https://assets.coingecko.com/coins/images/10365/large/near_icon.png',
        'VeChain': 'https://assets.coingecko.com/coins/images/1167/large/VET_Token_Icon.png',
        'Internet Computer': 'https://assets.coingecko.com/coins/images/14495/large/Internet_Computer_logo.png',
        'Filecoin': 'https://assets.coingecko.com/coins/images/12817/large/filecoin.png',
        'EOS': 'https://assets.coingecko.com/coins/images/738/large/eos-eos-logo.png',
        'Aptos': 'https://assets.coingecko.com/coins/images/26455/large/aptos_round.png',
        'The Sandbox': 'https://assets.coingecko.com/coins/images/12129/large/sandbox_logo.jpg',
        'Aave': 'https://assets.coingecko.com/coins/images/12645/large/AAVE.png',
        'Decentraland': 'https://assets.coingecko.com/coins/images/878/large/decentraland-mana.png',
        'Theta Network': 'https://assets.coingecko.com/coins/images/2538/large/theta-token-logo.png',
        'MultiversX (Elrond)': 'https://assets.coingecko.com/coins/images/12335/large/elrond_egld_logo.png'
    }

    # Return the URL or a default placeholder if not found
    return logo_url_mapping.get(selected_name, 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png')
