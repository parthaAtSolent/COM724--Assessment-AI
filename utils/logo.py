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
                        <img src="data:image/png;base64,{encoded_logo}" alt="Logo">
                    </div>
                </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning(f"⚠️ Logo not found at: {logo_path}")


def get_crypto_logo_url(selected_name):
    """Get cryptocurrency logo URL based on the selected name."""
    logo_url_mapping = {
        'Bitcoin': 'https://cryptologos.cc/logos/bitcoin-btc-logo.png',
        'Ethereum': 'https://cryptologos.cc/logos/ethereum-eth-logo.png',
        'Binance Coin': 'https://cryptologos.cc/logos/binance-coin-bnb-logo.png',
        'Ripple': 'https://cryptologos.cc/logos/xrp-xrp-logo.png',
        'Solana': 'https://cryptologos.cc/logos/solana-sol-logo.png',
        'Cardano': 'https://cryptologos.cc/logos/cardano-ada-logo.png',
        'Dogecoin': 'https://cryptologos.cc/logos/dogecoin-doge-logo.png',
        'Polkadot': 'https://cryptologos.cc/logos/polkadot-new-dot-logo.png',
        'Avalanche': 'https://cryptologos.cc/logos/avalanche-avax-logo.png',
        'Polygon': 'https://cryptologos.cc/logos/polygon-matic-logo.png',
        'Shiba Inu': 'https://cryptologos.cc/logos/shiba-inu-shib-logo.png',
        'Litecoin': 'https://cryptologos.cc/logos/litecoin-ltc-logo.png',
        'TRON': 'https://cryptologos.cc/logos/tron-trx-logo.png',
        'Bitcoin Cash': 'https://cryptologos.cc/logos/bitcoin-cash-bch-logo.png',
        'Cosmos': 'https://cryptologos.cc/logos/cosmos-atom-logo.png',
        'Chainlink': 'https://cryptologos.cc/logos/chainlink-link-logo.png',
        'Stellar': 'https://cryptologos.cc/logos/stellar-xlm-logo.png',
        'Uniswap': 'https://cryptologos.cc/logos/uniswap-uni-logo.png',
        'Monero': 'https://cryptologos.cc/logos/monero-xmr-logo.png',
        'Ethereum Classic': 'https://cryptologos.cc/logos/ethereum-classic-etc-logo.png',
        'NEAR Protocol': 'https://cryptologos.cc/logos/near-protocol-near-logo.png',
        'VeChain': 'https://cryptologos.cc/logos/vechain-vet-logo.png',
        'Internet Computer': 'https://cryptologos.cc/logos/internet-computer-icp-logo.png',
        'Filecoin': 'https://cryptologos.cc/logos/filecoin-fil-logo.png',
        'EOS': 'https://cryptologos.cc/logos/eos-eos-logo.png',
        'Aptos': 'https://cryptologos.cc/logos/aptos-apt-logo.png',
        'The Sandbox': 'https://cryptologos.cc/logos/the-sandbox-sand-logo.png',
        'Aave': 'https://cryptologos.cc/logos/aave-aave-logo.png',
        'Decentraland': 'https://cryptologos.cc/logos/decentraland-mana-logo.png',
        'Theta Network': 'https://cryptologos.cc/logos/theta-network-theta-logo.png',
        'MultiversX (Elrond)': 'https://cryptologos.cc/logos/multiversx-egld-logo.png'
    }

    return logo_url_mapping.get(selected_name)
