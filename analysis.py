"""
Financial Analysis Engine
Provides market data, technical analysis, AI-enhanced stock recommendations,
and actionable portfolio strategies with simulations.
Uses yfinance data + Groq AI for intelligent analysis.

Stock Universe: 500+ tickers across US, EU, Crypto, and Commodities.
AI Integration: Groq (Llama 3.3 70B) for sentiment analysis and reasoning.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import traceback
import time
import ssl
import os
import certifi

# ---------------------------------------------------------------------------
# SSL / macOS fix — ensure Python uses proper certificates
# ---------------------------------------------------------------------------
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# ---------------------------------------------------------------------------
# Retry configuration
# ---------------------------------------------------------------------------
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds, doubles each retry


# ---------------------------------------------------------------------------
# Stock name lookup (avoids yf.Ticker.info auth issues)
# ---------------------------------------------------------------------------

STOCK_NAMES = {
    # ===== US Stocks (200+) =====
    "AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.", "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com Inc.", "NVDA": "NVIDIA Corp.", "META": "Meta Platforms",
    "TSLA": "Tesla Inc.", "BRK-B": "Berkshire Hathaway B", "JPM": "JPMorgan Chase",
    "JNJ": "Johnson & Johnson", "V": "Visa Inc.", "PG": "Procter & Gamble",
    "UNH": "UnitedHealth Group", "HD": "Home Depot", "MA": "Mastercard",
    "DIS": "Walt Disney Co.", "PYPL": "PayPal Holdings", "NFLX": "Netflix Inc.",
    "ADBE": "Adobe Inc.", "CRM": "Salesforce Inc.", "INTC": "Intel Corp.",
    "AMD": "Advanced Micro Devices", "CSCO": "Cisco Systems", "PEP": "PepsiCo Inc.",
    "KO": "Coca-Cola Co.", "MRK": "Merck & Co.", "ABT": "Abbott Laboratories",
    "PFE": "Pfizer Inc.", "TMO": "Thermo Fisher Scientific", "AVGO": "Broadcom Inc.",
    "COST": "Costco Wholesale", "WMT": "Walmart Inc.", "XOM": "Exxon Mobil",
    "CVX": "Chevron Corp.", "LLY": "Eli Lilly & Co.", "ORCL": "Oracle Corp.",
    "ACN": "Accenture plc", "MCD": "McDonald's Corp.", "NKE": "Nike Inc.",
    "TXN": "Texas Instruments", "QCOM": "Qualcomm Inc.", "LOW": "Lowe's Companies",
    "UPS": "United Parcel Service", "CAT": "Caterpillar Inc.", "BA": "Boeing Co.",
    "GS": "Goldman Sachs", "MS": "Morgan Stanley", "BLK": "BlackRock Inc.",
    "SCHW": "Charles Schwab", "AXP": "American Express",
    # Growth / Tech
    "UBER": "Uber Technologies", "ABNB": "Airbnb Inc.", "SQ": "Block Inc.",
    "SHOP": "Shopify Inc.", "PLTR": "Palantir Technologies", "NET": "Cloudflare Inc.",
    "CRWD": "CrowdStrike Holdings", "SNOW": "Snowflake Inc.", "DDOG": "Datadog Inc.",
    "MDB": "MongoDB Inc.", "ZS": "Zscaler Inc.", "PANW": "Palo Alto Networks",
    "FTNT": "Fortinet Inc.", "TEAM": "Atlassian Corp.", "NOW": "ServiceNow Inc.",
    "WDAY": "Workday Inc.", "VEEV": "Veeva Systems", "TTD": "The Trade Desk",
    "PINS": "Pinterest Inc.", "SNAP": "Snap Inc.", "ROKU": "Roku Inc.",
    "ZM": "Zoom Video", "DASH": "DoorDash Inc.", "RBLX": "Roblox Corp.",
    "U": "Unity Software",
    # EV / Clean Energy
    "RIVN": "Rivian Automotive", "LCID": "Lucid Group", "ENPH": "Enphase Energy",
    "FSLR": "First Solar Inc.", "PLUG": "Plug Power Inc.",
    # Fintech
    "COIN": "Coinbase Global", "HOOD": "Robinhood Markets", "SOFI": "SoFi Technologies",
    "AFRM": "Affirm Holdings",
    # Biotech / Pharma
    "MRNA": "Moderna Inc.", "BIIB": "Biogen Inc.", "REGN": "Regeneron Pharma",
    "VRTX": "Vertex Pharmaceuticals", "GILD": "Gilead Sciences", "AMGN": "Amgen Inc.",
    "BMY": "Bristol-Myers Squibb", "ZTS": "Zoetis Inc.", "ISRG": "Intuitive Surgical",
    "DXCM": "DexCom Inc.", "IDXX": "IDEXX Laboratories",
    # Consumer / Retail
    "TGT": "Target Corp.", "SBUX": "Starbucks Corp.", "CMG": "Chipotle Mexican Grill",
    "LULU": "Lululemon Athletica", "BKNG": "Booking Holdings", "MAR": "Marriott Intl.",
    # Industrial / Defense
    "RTX": "RTX Corp.", "LMT": "Lockheed Martin", "GE": "GE Aerospace",
    "HON": "Honeywell Intl.", "DE": "Deere & Company", "MMM": "3M Company",
    # Semiconductors
    "MRVL": "Marvell Technology", "KLAC": "KLA Corp.", "LRCX": "Lam Research",
    "AMAT": "Applied Materials", "ON": "ON Semiconductor", "MU": "Micron Technology",
    # Media / Entertainment
    "SPOT": "Spotify Technology", "TTWO": "Take-Two Interactive", "EA": "Electronic Arts",
    # REITs
    "AMT": "American Tower", "PLD": "Prologis Inc.", "CCI": "Crown Castle",
    "O": "Realty Income", "SPG": "Simon Property Group",
    # ===== NEW: Additional S&P 500 stocks =====
    "ABBV": "AbbVie Inc.", "WFC": "Wells Fargo", "PM": "Philip Morris Intl.",
    "CMCSA": "Comcast Corp.", "NEE": "NextEra Energy", "IBM": "IBM Corp.",
    "GE": "GE Aerospace", "INTU": "Intuit Inc.", "SPGI": "S&P Global",
    "DHR": "Danaher Corp.", "SYK": "Stryker Corp.", "MDT": "Medtronic plc",
    "CI": "Cigna Group", "ELV": "Elevance Health", "CB": "Chubb Ltd.",
    "SO": "Southern Company", "DUK": "Duke Energy", "ICE": "Intercontinental Exchange",
    "CL": "Colgate-Palmolive", "MCO": "Moody's Corp.", "CME": "CME Group",
    "PNC": "PNC Financial", "USB": "U.S. Bancorp", "TFC": "Truist Financial",
    "AON": "Aon plc", "ITW": "Illinois Tool Works", "EMR": "Emerson Electric",
    "NSC": "Norfolk Southern", "FDX": "FedEx Corp.", "GM": "General Motors",
    "F": "Ford Motor Co.", "PSA": "Public Storage", "WELL": "Welltower Inc.",
    "HCA": "HCA Healthcare", "MCK": "McKesson Corp.", "ADP": "Automatic Data Processing",
    "FISV": "Fiserv Inc.", "MSCI": "MSCI Inc.", "APD": "Air Products",
    "SHW": "Sherwin-Williams", "ECL": "Ecolab Inc.", "ROP": "Roper Technologies",
    "CARR": "Carrier Global", "CTAS": "Cintas Corp.", "PAYX": "Paychex Inc.",
    "FAST": "Fastenal Co.", "ODFL": "Old Dominion Freight", "CPRT": "Copart Inc.",
    "VRSK": "Verisk Analytics", "MNST": "Monster Beverage", "KDP": "Keurig Dr Pepper",
    "DLTR": "Dollar Tree", "DG": "Dollar General", "ROST": "Ross Stores",
    "TJX": "TJX Companies", "ORLY": "O'Reilly Automotive", "AZO": "AutoZone Inc.",
    "KMB": "Kimberly-Clark", "GIS": "General Mills", "K": "Kellanova",
    "HSY": "Hershey Co.", "SJM": "J.M. Smucker", "HRL": "Hormel Foods",
    "CLX": "Clorox Co.", "CHD": "Church & Dwight",
    # AI / Data / Cloud
    "SMCI": "Super Micro Computer", "ARM": "Arm Holdings", "AI": "C3.ai Inc.",
    "PATH": "UiPath Inc.", "DUOL": "Duolingo Inc.", "CFLT": "Confluent Inc.",
    "ESTC": "Elastic NV", "GTLB": "GitLab Inc.", "S": "SentinelOne Inc.",
    "IOT": "Samsara Inc.", "BILL": "BILL Holdings",
    # Aerospace / Space
    "AXON": "Axon Enterprise", "HWM": "Howmet Aerospace", "TDG": "TransDigm Group",
    "HEI": "HEICO Corp.",

    # ===== EU Stocks (80+) =====
    # Netherlands
    "ASML.AS": "ASML Holding", "INGA.AS": "ING Group", "PHIA.AS": "Philips NV",
    "AD.AS": "Ahold Delhaize", "WKL.AS": "Wolters Kluwer", "HEIA.AS": "Heineken NV",
    # France
    "MC.PA": "LVMH", "OR.PA": "L'Oréal", "AIR.PA": "Airbus SE",
    "BNP.PA": "BNP Paribas", "DG.PA": "Vinci SA", "RMS.PA": "Hermès",
    "TTE.PA": "TotalEnergies", "AI.PA": "Air Liquide", "SU.PA": "Schneider Electric",
    "EL.PA": "EssilorLuxottica", "CS.PA": "AXA SA", "BN.PA": "Danone SA",
    "KER.PA": "Kering SA", "SAF.PA": "Safran SA", "SAN.PA": "Sanofi SA",
    "STMPA.PA": "STMicroelectronics",
    "CAP.PA": "Capgemini SE", "RI.PA": "Pernod Ricard", "SGO.PA": "Saint-Gobain",
    "PUB.PA": "Publicis Groupe", "VIV.PA": "Vivendi SE",
    # Germany
    "SAP.DE": "SAP SE", "SIE.DE": "Siemens AG", "DTE.DE": "Deutsche Telekom",
    "ALV.DE": "Allianz SE", "BAS.DE": "BASF SE", "BAYN.DE": "Bayer AG",
    "ADS.DE": "Adidas AG", "MBG.DE": "Mercedes-Benz Group", "BMW.DE": "BMW AG",
    "VOW3.DE": "Volkswagen AG", "MUV2.DE": "Munich Re", "DBK.DE": "Deutsche Bank",
    "FRE.DE": "Fresenius SE",
    "IFX.DE": "Infineon Technologies", "HEN3.DE": "Henkel AG", "RHM.DE": "Rheinmetall AG",
    "MTX.DE": "MTU Aero Engines", "SHL.DE": "Siemens Healthineers", "PUM.DE": "Puma SE",
    # Spain
    "SAN.MC": "Banco Santander", "IBE.MC": "Iberdrola", "FER.MC": "Ferrovial SE",
    "ITX.MC": "Inditex SA", "TEF.MC": "Telefónica SA",
    "BBVA.MC": "BBVA", "AMS.MC": "Amadeus IT", "CABK.MC": "CaixaBank",
    # Italy
    "ENEL.MI": "Enel SpA", "ISP.MI": "Intesa Sanpaolo", "STLAM.MI": "Stellantis NV",
    "ENI.MI": "Eni SpA", "UCG.MI": "UniCredit SpA",
    "RACE.MI": "Ferrari NV", "G.MI": "Assicurazioni Generali",
    # Belgium
    "ABI.BR": "AB InBev",
    # UK
    "SHEL.L": "Shell plc", "AZN.L": "AstraZeneca", "HSBA.L": "HSBC Holdings",
    "BP.L": "BP plc", "GSK.L": "GSK plc", "RIO.L": "Rio Tinto",
    "ULVR.L": "Unilever plc", "LSEG.L": "London Stock Exchange",
    "DGE.L": "Diageo plc", "BATS.L": "British American Tobacco",
    "REL.L": "RELX plc", "AAL.L": "Anglo American",
    # Nordic
    "NOVO-B.CO": "Novo Nordisk", "ERIC-B.ST": "Ericsson",
    "VOLV-B.ST": "Volvo Group",
    "NIBE-B.ST": "NIBE Industrier", "SAND.ST": "Sandvik AB",
    "MAERSK-B.CO": "A.P. Moller-Maersk",
    # Swiss
    "NESN.SW": "Nestlé SA", "ROG.SW": "Roche Holding", "NOVN.SW": "Novartis AG",
    "ABBN.SW": "ABB Ltd.", "SREN.SW": "Swiss Re",

    # ===== Crypto (Top 25) =====
    "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "BNB-USD": "Binance Coin",
    "SOL-USD": "Solana", "XRP-USD": "Ripple", "ADA-USD": "Cardano",
    "DOGE-USD": "Dogecoin", "DOT-USD": "Polkadot", "AVAX-USD": "Avalanche",
    "MATIC-USD": "Polygon", "LINK-USD": "Chainlink", "UNI-USD": "Uniswap",
    "ATOM-USD": "Cosmos", "LTC-USD": "Litecoin", "FIL-USD": "Filecoin",
    "NEAR-USD": "NEAR Protocol", "APT-USD": "Aptos", "ARB-USD": "Arbitrum",
    "OP-USD": "Optimism", "SUI-USD": "Sui", "AAVE-USD": "Aave",
    "MKR-USD": "Maker", "RENDER-USD": "Render Token", "INJ-USD": "Injective",
    "FET-USD": "Fetch.ai",

    # ===== Commodity ETFs =====
    "GLD": "SPDR Gold Trust", "SLV": "iShares Silver Trust",
    "USO": "United States Oil Fund", "PPLT": "Aberdeen Platinum ETF",
    "DBA": "Invesco DB Agriculture", "DBC": "Invesco DB Commodity Index",
    "PDBC": "Invesco Optimum Yield Diversified Commodity",
    "COPX": "Global X Copper Miners", "UNG": "United States Natural Gas Fund",
    "WEAT": "Teucrium Wheat Fund", "CORN": "Teucrium Corn Fund",
    "CPER": "United States Copper Index", "JO": "iPath Bloomberg Coffee",

    # ===== ETFs =====
    "SPY": "S&P 500 ETF", "VOO": "Vanguard S&P 500", "QQQ": "NASDAQ 100 ETF",
    "VGK": "Vanguard FTSE Europe", "VXUS": "Vanguard Intl Stock",
    "BND": "Vanguard Total Bond", "AGG": "iShares Core Bond",
    "VYM": "Vanguard High Dividend", "SCHD": "Schwab US Dividend",
    "VNQ": "Vanguard Real Estate", "IWM": "iShares Russell 2000",
    "VWO": "Vanguard Emerging Markets", "VUG": "Vanguard Growth",
    "XLK": "Technology Select", "XLF": "Financial Select",
    "XLV": "Health Care Select", "XLE": "Energy Select",
    "XLY": "Consumer Discretionary", "XLP": "Consumer Staples",
    "XLI": "Industrial Select", "XLB": "Materials Select",
    "XLRE": "Real Estate Select", "XLU": "Utilities Select",
    "XLC": "Communication Services", "EFA": "iShares MSCI EAFE",
    "TLT": "iShares 20+ Year Treasury",
    "IEFA": "iShares Core MSCI EAFE", "VIG": "Vanguard Dividend Appreciation",
    "ARKK": "ARK Innovation ETF", "ARKG": "ARK Genomic Revolution",
    "SOXX": "iShares Semiconductor", "HACK": "ETFMG Prime Cyber Security",
    "BOTZ": "Global X Robotics & AI", "LIT": "Global X Lithium & Battery",
    "TAN": "Invesco Solar ETF", "ICLN": "iShares Global Clean Energy",
    # ===== EU-Domiciled ETFs (popular on Revolut/IBKR in Europe) =====
    "VUAA.L": "Vanguard S&P 500 UCITS ETF", "VWCE.DE": "Vanguard FTSE All-World UCITS ETF",
    "CSPX.L": "iShares Core S&P 500 UCITS ETF", "IUSA.L": "iShares S&P 500 UCITS ETF",
    "EUNL.DE": "iShares Core MSCI World UCITS ETF", "IWDA.L": "iShares Core MSCI World UCITS ETF",
    "VUSA.L": "Vanguard S&P 500 UCITS ETF (Dist)", "VWRL.L": "Vanguard FTSE All-World UCITS ETF (Dist)",
    "SWDA.L": "iShares Core MSCI World UCITS ETF", "EMIM.L": "iShares Core MSCI EM UCITS ETF",
    "VUAG.L": "Vanguard S&P 500 UCITS ETF (GBP)", "VHYL.L": "Vanguard FTSE All-World High Div UCITS ETF",
    "ISAC.L": "iShares MSCI ACWI UCITS ETF", "AGGH.L": "iShares Core Global Aggregate Bond UCITS ETF",
    "SXR8.DE": "iShares Core S&P 500 UCITS ETF (EUR)", "EQQQ.L": "Invesco NASDAQ-100 UCITS ETF",
}

# ---------------------------------------------------------------------------
# Universe of stocks to scan
# ---------------------------------------------------------------------------

US_STOCKS = [
    # Original 50 blue chips
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL", "NFLX",
    "ADBE", "CRM", "INTC", "AMD", "CSCO", "PEP", "KO", "MRK", "ABT",
    "PFE", "TMO", "AVGO", "COST", "WMT", "XOM", "CVX", "LLY", "ORCL",
    "ACN", "MCD", "NKE", "TXN", "QCOM", "LOW", "UPS", "CAT", "BA",
    "GS", "MS", "BLK", "SCHW", "AXP",
    # Growth / Tech
    "UBER", "ABNB", "SQ", "SHOP", "PLTR", "NET", "CRWD", "SNOW",
    "DDOG", "MDB", "ZS", "PANW", "FTNT", "TEAM", "NOW", "WDAY",
    "VEEV", "TTD", "PINS", "SNAP", "ROKU", "ZM", "DASH", "RBLX", "U",
    # EV / Clean Energy
    "RIVN", "LCID", "ENPH", "FSLR", "PLUG",
    # Fintech
    "COIN", "HOOD", "SOFI", "AFRM",
    # Biotech / Pharma
    "MRNA", "BIIB", "REGN", "VRTX", "GILD", "AMGN", "BMY", "ZTS",
    "ISRG", "DXCM", "IDXX",
    # Consumer / Retail
    "TGT", "SBUX", "CMG", "LULU", "BKNG", "MAR",
    # Industrial / Defense
    "RTX", "LMT", "GE", "HON", "DE", "MMM",
    # Semiconductors
    "MRVL", "KLAC", "LRCX", "AMAT", "ON", "MU",
    # Media / Entertainment
    "SPOT", "TTWO", "EA",
    # REITs
    "AMT", "PLD", "CCI", "O", "SPG",
    # ===== NEW: Additional S&P 500 stocks =====
    "ABBV", "WFC", "PM", "CMCSA", "NEE", "IBM", "INTU", "SPGI",
    "DHR", "SYK", "MDT", "CI", "ELV", "CB", "SO", "DUK", "ICE",
    "CL", "MCO", "CME", "PNC", "USB", "TFC", "AON", "ITW", "EMR",
    "NSC", "FDX", "GM", "F", "PSA", "WELL", "HCA", "MCK", "ADP",
    "FISV", "MSCI", "APD", "SHW", "ECL", "ROP", "CARR", "CTAS",
    "PAYX", "FAST", "ODFL", "CPRT", "VRSK", "MNST", "KDP",
    "DLTR", "DG", "ROST", "TJX", "ORLY", "AZO",
    "KMB", "GIS", "K", "HSY", "SJM", "HRL", "CLX", "CHD",
    # AI / Data / Cloud
    "SMCI", "ARM", "PATH", "DUOL", "CFLT", "ESTC", "GTLB", "S",
    "IOT", "BILL",
    # Aerospace / Space
    "AXON", "HWM", "TDG", "HEI",
]

EU_STOCKS = [
    # Netherlands
    "ASML.AS", "INGA.AS", "PHIA.AS", "AD.AS", "WKL.AS", "HEIA.AS",
    # France
    "MC.PA", "OR.PA", "AIR.PA", "BNP.PA", "DG.PA", "RMS.PA",
    "TTE.PA", "AI.PA", "SU.PA", "EL.PA", "CS.PA", "BN.PA",
    "KER.PA", "SAF.PA", "SAN.PA", "STMPA.PA",
    "CAP.PA", "RI.PA", "SGO.PA", "PUB.PA", "VIV.PA",
    # Germany
    "SAP.DE", "SIE.DE", "DTE.DE", "ALV.DE", "BAS.DE", "BAYN.DE",
    "ADS.DE", "MBG.DE", "BMW.DE", "VOW3.DE", "MUV2.DE", "DBK.DE", "FRE.DE",
    "IFX.DE", "HEN3.DE", "RHM.DE", "MTX.DE", "SHL.DE",
    # Spain
    "SAN.MC", "IBE.MC", "FER.MC", "ITX.MC", "TEF.MC",
    "BBVA.MC", "AMS.MC", "CABK.MC",
    # Italy
    "ENEL.MI", "ISP.MI", "STLAM.MI", "ENI.MI", "UCG.MI",
    "RACE.MI", "G.MI",
    # Belgium
    "ABI.BR",
    # UK
    "SHEL.L", "AZN.L", "HSBA.L", "BP.L", "GSK.L", "RIO.L", "ULVR.L", "LSEG.L",
    "DGE.L", "BATS.L", "REL.L", "AAL.L",
    # Nordic
    "NOVO-B.CO", "ERIC-B.ST", "VOLV-B.ST",
    "NIBE-B.ST", "SAND.ST", "MAERSK-B.CO",
    # Swiss
    "NESN.SW", "ROG.SW", "NOVN.SW", "ABBN.SW", "SREN.SW",
]

CRYPTO_STOCKS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD",
    "DOGE-USD", "DOT-USD", "AVAX-USD", "MATIC-USD", "LINK-USD", "UNI-USD",
    "ATOM-USD", "LTC-USD", "FIL-USD", "NEAR-USD", "APT-USD", "ARB-USD",
    "OP-USD", "SUI-USD", "AAVE-USD", "MKR-USD", "RENDER-USD", "INJ-USD",
    "FET-USD",
]

US_INDICES = {
    "^GSPC": "S&P 500",
    "^IXIC": "NASDAQ",
    "^DJI": "Dow Jones",
    "^RUT": "Russell 2000",
}

EU_INDICES = {
    "^STOXX50E": "EURO STOXX 50",
    "^FTSE": "FTSE 100",
    "^GDAXI": "DAX 40",
    "^IBEX": "IBEX 35",
    "^FCHI": "CAC 40",
}

SECTOR_ETFS = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLV": "Healthcare",
    "XLE": "Energy",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLI": "Industrials",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLU": "Utilities",
    "XLC": "Communication Services",
}

# ---------------------------------------------------------------------------
# Commodities — Futures tickers + ETFs
# ---------------------------------------------------------------------------

COMMODITY_FUTURES = {
    "GC=F": "Gold",
    "SI=F": "Silver",
    "CL=F": "Crude Oil (WTI)",
    "BZ=F": "Brent Crude",
    "NG=F": "Natural Gas",
    "HG=F": "Copper",
    "PL=F": "Platinum",
    "PA=F": "Palladium",
    "ZC=F": "Corn",
    "ZW=F": "Wheat",
}

COMMODITY_ETFS = ["GLD", "SLV", "USO", "PPLT", "DBA", "DBC", "PDBC", "COPX", "UNG"]

# ---------------------------------------------------------------------------
# Portfolio definitions for each risk profile
# ---------------------------------------------------------------------------

PORTFOLIOS = {
    "conservative": {
        "name": "🟢 Conservative Portfolio",
        "description": "Low risk, steady income. Focus on bonds, dividends, and blue-chip stability.",
        "risk_level": "Low",
        "target_return": "5-7% annually",
        "rebalance": "Every 6 months",
        "holdings": [
            {"ticker": "BND",  "name": "Vanguard Total Bond ETF",     "pct": 30, "why": "Core bond holding for stability and income"},
            {"ticker": "VOO",  "name": "Vanguard S&P 500 ETF",        "pct": 20, "why": "Broad US market exposure at low cost"},
            {"ticker": "SCHD", "name": "Schwab US Dividend ETF",       "pct": 15, "why": "High-quality dividend stocks for income"},
            {"ticker": "VGK",  "name": "Vanguard FTSE Europe ETF",     "pct": 10, "why": "European diversification, value-oriented"},
            {"ticker": "VIG",  "name": "Vanguard Dividend Appreciation","pct": 10, "why": "Companies with growing dividends"},
            {"ticker": "GLD",  "name": "SPDR Gold Trust",              "pct": 5,  "why": "Inflation hedge and safe haven"},
            {"ticker": "TLT",  "name": "iShares 20+ Year Treasury",    "pct": 10, "why": "Long-term government bonds for safety"},
        ],
    },
    "moderate": {
        "name": "🟡 Moderate Portfolio",
        "description": "Balanced growth and stability. Mix of stocks and bonds with global diversification.",
        "risk_level": "Medium",
        "target_return": "8-11% annually",
        "rebalance": "Every 3 months",
        "holdings": [
            {"ticker": "VOO",  "name": "Vanguard S&P 500 ETF",        "pct": 30, "why": "Core US equity holding"},
            {"ticker": "QQQ",  "name": "Invesco NASDAQ 100 ETF",       "pct": 15, "why": "Tech-heavy growth exposure"},
            {"ticker": "VGK",  "name": "Vanguard FTSE Europe ETF",     "pct": 12, "why": "European market exposure"},
            {"ticker": "BND",  "name": "Vanguard Total Bond ETF",      "pct": 15, "why": "Bond ballast for stability"},
            {"ticker": "SCHD", "name": "Schwab US Dividend ETF",       "pct": 10, "why": "Dividend income stream"},
            {"ticker": "VNQ",  "name": "Vanguard Real Estate ETF",     "pct": 8,  "why": "Real estate diversification"},
            {"ticker": "VWO",  "name": "Vanguard Emerging Markets ETF", "pct": 5, "why": "Emerging market growth potential"},
            {"ticker": "GLD",  "name": "SPDR Gold Trust",              "pct": 5,  "why": "Portfolio insurance"},
        ],
    },
    "aggressive": {
        "name": "🔴 Aggressive Portfolio",
        "description": "Maximum growth. Heavy on tech, growth stocks, and individual picks. Higher volatility.",
        "risk_level": "High",
        "target_return": "12-18% annually",
        "rebalance": "Monthly review",
        "holdings": [
            {"ticker": "QQQ",  "name": "Invesco NASDAQ 100 ETF",       "pct": 25, "why": "Core tech/growth exposure"},
            {"ticker": "VOO",  "name": "Vanguard S&P 500 ETF",         "pct": 15, "why": "Broad market foundation"},
            {"ticker": "NVDA", "name": "NVIDIA Corp.",                  "pct": 8,  "why": "AI/GPU leader, massive growth"},
            {"ticker": "MSFT", "name": "Microsoft Corp.",               "pct": 7,  "why": "Cloud + AI dominance"},
            {"ticker": "AMZN", "name": "Amazon.com Inc.",               "pct": 6,  "why": "E-commerce + AWS cloud leader"},
            {"ticker": "ASML.AS","name": "ASML Holding",                "pct": 5,  "why": "Monopoly in chip lithography (EU)"},
            {"ticker": "IWM",  "name": "iShares Russell 2000 ETF",     "pct": 8,  "why": "Small-cap growth potential"},
            {"ticker": "VGK",  "name": "Vanguard FTSE Europe ETF",     "pct": 8,  "why": "European value opportunity"},
            {"ticker": "META", "name": "Meta Platforms",                "pct": 5,  "why": "Social media + AI + metaverse"},
            {"ticker": "AMD",  "name": "Advanced Micro Devices",        "pct": 5,  "why": "CPU/GPU competitor, AI beneficiary"},
            {"ticker": "VWO",  "name": "Vanguard Emerging Markets ETF", "pct": 5,  "why": "High-growth emerging economies"},
            {"ticker": "LLY",  "name": "Eli Lilly & Co.",               "pct": 3,  "why": "Pharma leader, weight-loss drugs boom"},
        ],
    },
}


# ---------------------------------------------------------------------------
# Helper: fetch a single ticker's data safely (with retries)
# ---------------------------------------------------------------------------

def _safe_download(ticker, period="3mo", interval="1d"):
    """Download data for a single ticker with retry logic and SSL handling."""
    for attempt in range(MAX_RETRIES):
        try:
            df = yf.download(
                ticker,
                period=period,
                interval=interval,
                progress=False,
                threads=False,
                timeout=15,
            )
            if df is not None and not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                return df
            # Empty result — might be a transient issue, retry
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
        except Exception as e:
            error_msg = str(e).lower()
            # Retry on network / SSL / rate-limit errors
            if any(kw in error_msg for kw in ["ssl", "timeout", "connection", "rate", "429", "503"]):
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    print(f"  ⚠️  Retry {attempt+1}/{MAX_RETRIES} for {ticker} (waiting {delay}s): {e}")
                    time.sleep(delay)
                    continue
            # Non-retryable error
            print(f"  ❌ Failed to download {ticker}: {e}")
            break
    return None


def _safe_download_daterange(ticker, start, end, interval="1d"):
    """Download data for a single ticker using date range, with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            df = yf.download(
                ticker,
                start=start,
                end=end,
                interval=interval,
                progress=False,
                threads=False,
                timeout=15,
            )
            if df is not None and not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                return df
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
        except Exception as e:
            error_msg = str(e).lower()
            if any(kw in error_msg for kw in ["ssl", "timeout", "connection", "rate", "429", "503"]):
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    print(f"  ⚠️  Retry {attempt+1}/{MAX_RETRIES} for {ticker} (waiting {delay}s): {e}")
                    time.sleep(delay)
                    continue
            print(f"  ❌ Failed to download {ticker}: {e}")
            break
    return None


def _batch_download(tickers, period="3mo", interval="1d"):
    """Download data for multiple tickers using threading with retries.
    Uses 20 workers for faster fetching of 500+ tickers."""
    results = {}
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(_safe_download, t, period, interval): t
            for t in tickers
        }
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                data = future.result()
                if data is not None:
                    results[ticker] = data
            except Exception:
                pass
    return results


# ---------------------------------------------------------------------------
# AI Analysis Engine — Groq Integration (70% AI / 30% Technical)
# ---------------------------------------------------------------------------

_groq_client = None
_ai_cache = {}
_ai_cache_ttl = 1800  # 30 minutes


def _get_groq_client():
    """Lazy-initialize the Groq client using OpenAI-compatible SDK."""
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        _groq_client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        return _groq_client
    except Exception as e:
        print(f"  ⚠️ Could not initialize Groq client: {e}")
        return None


def ai_is_available():
    """Check if AI analysis is available (Groq API key configured)."""
    return bool(os.environ.get("GROQ_API_KEY", ""))


def ai_analyze_stocks(stocks_data, market_regime=None):
    """
    Use Groq AI to analyze a batch of stocks.
    Takes pre-computed technical data and returns AI sentiment + reasoning.
    
    stocks_data: list of dicts with ticker, name, price, score, rsi, trend, pct_1w, pct_1m, etc.
    market_regime: dict with regime info (bull/bear/sideways)
    
    Returns: dict mapping ticker -> {ai_score, ai_reasoning, ai_risk, ai_confidence}
    """
    client = _get_groq_client()
    if not client or not stocks_data:
        return {}

    # Check cache
    cache_key = "ai_batch_" + "_".join(sorted(s["ticker"] for s in stocks_data[:8]))
    now = datetime.now().timestamp()
    if cache_key in _ai_cache:
        cached, ts = _ai_cache[cache_key]
        if now - ts < _ai_cache_ttl:
            return cached

    # Build the prompt
    regime_text = ""
    if market_regime and market_regime.get("regime") != "unknown":
        regime_text = f"Market regime: {market_regime['regime'].upper()} — {market_regime.get('description', '')}\n"

    stocks_text = ""
    for s in stocks_data[:8]:  # Limit to 8 stocks per batch
        news_text = ""
        if s.get("news"):
            news_text = " | News: " + "; ".join(n.get("title", "")[:60] for n in s["news"][:3])
        stocks_text += (
            f"- {s['ticker']} ({s['name']}): ${s['price']}, "
            f"Tech Score: {s.get('score', 0)}, RSI: {s.get('rsi', 50)}, "
            f"Trend: {s.get('trend', 'neutral')}, "
            f"Week: {s.get('pct_1w', 0):+.1f}%, Month: {s.get('pct_1m', 0):+.1f}%"
            f"{', 3M: ' + str(round(s['pct_3m'], 1)) + '%' if s.get('pct_3m') is not None else ''}"
            f"{news_text}\n"
        )

    prompt = f"""You are a senior financial analyst. Analyze these stocks and provide your assessment.

{regime_text}
STOCKS TO ANALYZE:
{stocks_text}

For EACH stock, respond in this EXACT JSON format (no markdown, no extra text):
{{
  "TICKER": {{
    "score": <number from -50 to 50, your sentiment score>,
    "reasoning": "<1-2 sentence analysis including fundamentals, sector outlook, catalysts, risks>",
    "risk": "<main risk factor in 5-10 words>",
    "confidence": "<high/medium/low>"
  }}
}}

Rules:
- Positive score = bullish, negative = bearish, 0 = neutral
- Consider news sentiment, sector trends, competitive position, macro factors
- Be honest about risks — don't just agree with technical signals
- If a stock has bad fundamentals but good technicals, flag it
- If a stock is in a declining sector, penalize it regardless of short-term bounce
- Consider the current market regime in your analysis"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a senior financial analyst. Respond ONLY with valid JSON. No markdown, no code blocks, no extra text."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.3,
        )

        raw = response.choices[0].message.content.strip()
        # Clean up potential markdown wrapping
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            if raw.endswith("```"):
                raw = raw[:-3]
        raw = raw.strip()

        result = json.loads(raw)

        # Validate and normalize
        ai_results = {}
        for ticker, data in result.items():
            ticker = ticker.upper().strip()
            ai_score = max(-50, min(50, int(data.get("score", 0))))
            ai_results[ticker] = {
                "ai_score": ai_score,
                "ai_reasoning": str(data.get("reasoning", ""))[:200],
                "ai_risk": str(data.get("risk", ""))[:100],
                "ai_confidence": str(data.get("confidence", "medium")).lower(),
            }

        # Cache results
        _ai_cache[cache_key] = (ai_results, now)
        return ai_results

    except json.JSONDecodeError as e:
        print(f"  ⚠️ AI response was not valid JSON: {e}")
        return {}
    except Exception as e:
        print(f"  ⚠️ AI analysis failed: {e}")
        return {}


def ai_analyze_single(ticker, stock_data, news=None, market_regime=None):
    """
    AI analysis for a single stock (used in search and portfolio analysis).
    Returns: {ai_score, ai_reasoning, ai_risk, ai_confidence} or empty dict.
    """
    enriched = dict(stock_data)
    if news:
        enriched["news"] = news
    results = ai_analyze_stocks([enriched], market_regime=market_regime)
    return results.get(ticker.upper(), {})


def combine_scores(technical_score, ai_score):
    """
    Combine technical and AI scores with 70/30 AI/Technical weighting.
    Returns combined score clamped to -100..100.
    """
    # AI score is -50 to 50, scale to -100 to 100
    ai_scaled = ai_score * 2
    combined = (0.30 * technical_score) + (0.70 * ai_scaled)
    return max(-100, min(100, round(combined)))


def get_crypto_data():
    """Get current crypto prices and daily changes."""
    data = _batch_download(CRYPTO_STOCKS, period="5d", interval="1d")

    cryptos = []
    for ticker in CRYPTO_STOCKS:
        df = data.get(ticker)
        if df is not None and len(df) >= 2:
            close = df["Close"].squeeze()
            current = float(close.iloc[-1])
            prev = float(close.iloc[-2])
            change = ((current - prev) / prev) * 100
            pct_1w = float((close.iloc[-1] / close.iloc[-5] - 1) * 100) if len(close) >= 5 else None
            name = STOCK_NAMES.get(ticker, ticker.replace("-USD", ""))

            cryptos.append({
                "name": name,
                "ticker": ticker,
                "price": round(current, 2),
                "change": round(change, 2),
                "pct_1w": round(pct_1w, 2) if pct_1w is not None else None,
            })

    return cryptos


# ---------------------------------------------------------------------------
# Technical indicators
# ---------------------------------------------------------------------------

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def analyze_stock(ticker, df):
    """Run technical analysis on a stock. Returns score + recommendation.
    Enhanced with 200-day SMA, trend detection, and long-term context."""
    if df is None or len(df) < 30:
        return None

    close = df["Close"].squeeze().dropna()
    volume = df["Volume"].squeeze().dropna()

    if len(close) < 10:
        return None

    current_price = float(close.iloc[-1])
    prev_price = float(close.iloc[-2]) if len(close) > 1 else current_price

    sma_20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else None
    sma_50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None
    sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None

    rsi = compute_rsi(close)
    current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50

    macd_line, signal_line, histogram = compute_macd(close)
    current_macd = float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else 0

    avg_volume = float(volume.rolling(20).mean().iloc[-1]) if len(volume) >= 20 else float(volume.mean())
    current_volume = float(volume.iloc[-1])
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

    pct_1w = float((close.iloc[-1] / close.iloc[-5] - 1) * 100) if len(close) >= 5 else 0
    pct_1m = float((close.iloc[-1] / close.iloc[-21] - 1) * 100) if len(close) >= 21 else 0
    pct_3m = float((close.iloc[-1] / close.iloc[-63] - 1) * 100) if len(close) >= 63 else None
    pct_6m = float((close.iloc[-1] / close.iloc[-126] - 1) * 100) if len(close) >= 126 else None

    # 52-week high/low
    high_52w = float(close.max()) if len(close) >= 200 else float(close.max())
    low_52w = float(close.min()) if len(close) >= 200 else float(close.min())
    pct_from_high = ((current_price - high_52w) / high_52w) * 100 if high_52w > 0 else 0

    # Trend detection: higher highs / lower lows
    trend = "neutral"
    if len(close) >= 63:
        recent_high = float(close.iloc[-21:].max())
        prev_high = float(close.iloc[-63:-21].max())
        recent_low = float(close.iloc[-21:].min())
        prev_low = float(close.iloc[-63:-21].min())
        if recent_high > prev_high and recent_low > prev_low:
            trend = "uptrend"
        elif recent_high < prev_high and recent_low < prev_low:
            trend = "downtrend"

    # --- IMPROVED SCORING ---
    score = 0

    # RSI scoring
    if current_rsi < 30: score += 25
    elif current_rsi < 40: score += 10
    elif current_rsi > 70: score -= 25
    elif current_rsi > 60: score -= 10

    # MACD scoring
    if current_macd > 0: score += 15
    else: score -= 10

    # SMA 20 scoring
    if sma_20 is not None:
        if current_price > sma_20: score += 8
        else: score -= 8

    # SMA 50 scoring
    if sma_50 is not None:
        if current_price > sma_50: score += 8
        else: score -= 10
        if sma_20 is not None and sma_20 > sma_50: score += 8
        elif sma_20 is not None: score -= 8

    # *** NEW: SMA 200 scoring (major trend indicator) ***
    if sma_200 is not None:
        if current_price > sma_200:
            score += 15  # Above 200-day = bullish
        else:
            score -= 20  # Below 200-day = bearish (heavy penalty)

    # Short-term momentum
    if pct_1w > 2: score += 5
    elif pct_1w < -2: score -= 5

    # 1-month momentum
    if pct_1m > 5: score += 8
    elif pct_1m < -5: score -= 8
    elif pct_1m < -10: score -= 15

    # *** NEW: 3-month trend (catches sustained declines) ***
    if pct_3m is not None:
        if pct_3m > 10: score += 10
        elif pct_3m < -15: score -= 20
        elif pct_3m < -30: score -= 35

    # *** NEW: 6-month trend ***
    if pct_6m is not None:
        if pct_6m < -30: score -= 25  # Severe long-term decline
        elif pct_6m < -15: score -= 10

    # *** NEW: Trend structure scoring ***
    if trend == "uptrend": score += 10
    elif trend == "downtrend": score -= 15

    # *** NEW: Distance from 52-week high ***
    if pct_from_high < -40: score -= 20  # More than 40% below high
    elif pct_from_high < -25: score -= 10

    # *** NEW: Dead cat bounce detection ***
    # If stock is in severe decline but had a short-term bounce, penalize
    if pct_3m is not None and pct_3m < -20 and pct_1w > 5:
        score -= 15  # Bounce in a downtrend = suspicious

    # Volume confirmation
    if volume_ratio > 1.5 and score > 0: score += 8

    score = max(-100, min(100, score))

    if score >= 50:
        hold = "Short-term (1-2 weeks)"
        action = "Strong Buy"
    elif score >= 25:
        hold = "Medium-term (1-3 months)"
        action = "Buy"
    elif score >= 0:
        hold = "Long-term (6-12 months)"
        action = "Hold / Accumulate"
    elif score >= -25:
        hold = "—"
        action = "Hold"
    else:
        hold = "—"
        action = "Avoid / Sell"

    name = STOCK_NAMES.get(ticker, ticker)
    daily_change = ((current_price - prev_price) / prev_price) * 100 if prev_price else 0

    # Dynamic stop-loss and target price based on volatility
    # Calculate annualized volatility from daily returns
    daily_returns = close.pct_change().dropna()
    ann_vol = float(daily_returns.std() * (252 ** 0.5)) if len(daily_returns) > 10 else 0.20

    # Quick Flip targets (tighter) vs Long Hold targets (wider)
    # These will be overridden in get_todays_actions based on strategy_type
    # Default: use moderate targets scaled by volatility
    target_pct = max(0.05, min(0.25, ann_vol * 1.0))   # 5% to 25% based on volatility
    stop_pct = max(0.03, min(0.10, ann_vol * 0.5))      # 3% to 10% based on volatility

    stop_loss = round(current_price * (1 - stop_pct), 2)
    target_price = round(current_price * (1 + target_pct), 2)

    return {
        "ticker": ticker,
        "name": name,
        "price": round(current_price, 2),
        "daily_change": round(daily_change, 2),
        "rsi": round(current_rsi, 1),
        "macd_histogram": round(current_macd, 4),
        "sma_20": round(sma_20, 2) if sma_20 else None,
        "sma_50": round(sma_50, 2) if sma_50 else None,
        "sma_200": round(sma_200, 2) if sma_200 else None,
        "pct_1w": round(pct_1w, 2),
        "pct_1m": round(pct_1m, 2),
        "pct_3m": round(pct_3m, 2) if pct_3m is not None else None,
        "pct_6m": round(pct_6m, 2) if pct_6m is not None else None,
        "pct_from_high": round(pct_from_high, 2),
        "trend": trend,
        "volume_ratio": round(volume_ratio, 2),
        "score": score,
        "action": action,
        "hold_duration": hold,
        "stop_loss": stop_loss,
        "target_price": target_price,
    }


# ---------------------------------------------------------------------------
# Public API functions
# ---------------------------------------------------------------------------

def get_market_overview():
    """Get current performance of major US and EU indices."""
    all_indices = {**US_INDICES, **EU_INDICES}
    results = {"us": [], "eu": []}

    data = _batch_download(list(all_indices.keys()), period="5d", interval="1d")

    if not data:
        raise RuntimeError(
            "Could not fetch market data from Yahoo Finance. "
            "This may be due to network issues, rate limiting, or SSL certificate problems. "
            "Try again in a few seconds."
        )

    for ticker, name in US_INDICES.items():
        df = data.get(ticker)
        if df is not None and len(df) >= 2:
            close = df["Close"].squeeze().dropna()
            if len(close) < 2:
                continue
            current = float(close.iloc[-1])
            prev = float(close.iloc[-2])
            change = ((current - prev) / prev) * 100 if prev else 0
            results["us"].append({
                "name": name, "ticker": ticker,
                "price": round(current, 2), "change": round(change, 2),
            })

    for ticker, name in EU_INDICES.items():
        df = data.get(ticker)
        if df is not None and len(df) >= 2:
            close = df["Close"].squeeze().dropna()
            if len(close) < 2:
                continue
            current = float(close.iloc[-1])
            prev = float(close.iloc[-2])
            change = ((current - prev) / prev) * 100 if prev else 0
            results["eu"].append({
                "name": name, "ticker": ticker,
                "price": round(current, 2), "change": round(change, 2),
            })

    return results


def get_commodities():
    """Get current commodity prices and daily changes."""
    tickers = list(COMMODITY_FUTURES.keys())
    data = _batch_download(tickers, period="5d", interval="1d")

    commodities = []
    for ticker, name in COMMODITY_FUTURES.items():
        df = data.get(ticker)
        if df is not None and len(df) >= 2:
            close = df["Close"].squeeze()
            current = float(close.iloc[-1])
            prev = float(close.iloc[-2])
            change = ((current - prev) / prev) * 100

            # Also get 1-week and 1-month change if available
            pct_1w = float((close.iloc[-1] / close.iloc[-5] - 1) * 100) if len(close) >= 5 else None

            commodities.append({
                "name": name,
                "ticker": ticker,
                "price": round(current, 2),
                "change": round(change, 2),
                "pct_1w": round(pct_1w, 2) if pct_1w is not None else None,
            })

    return commodities


def get_recommendations(market="all", top_n=10):
    """Scan stocks and return top recommendations sorted by score."""
    if market == "us":
        tickers = US_STOCKS
    elif market == "eu":
        tickers = EU_STOCKS
    else:
        tickers = US_STOCKS + EU_STOCKS

    data = _batch_download(tickers, period="3mo", interval="1d")

    if not data:
        raise RuntimeError(
            "Could not fetch stock data. Yahoo Finance may be rate-limiting requests. "
            "Try again in a minute."
        )

    recommendations = []
    for ticker in tickers:
        df = data.get(ticker)
        if df is not None:
            result = analyze_stock(ticker, df)
            if result and result["score"] > 0:
                result["market"] = "US" if ticker in US_STOCKS else "EU"
                recommendations.append(result)

    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations[:top_n]


def get_top_movers(market="all", n=10):
    """Get biggest gainers and losers for the day."""
    if market == "us":
        tickers = US_STOCKS
    elif market == "eu":
        tickers = EU_STOCKS
    else:
        tickers = US_STOCKS + EU_STOCKS

    data = _batch_download(tickers, period="5d", interval="1d")

    movers = []
    for ticker in tickers:
        df = data.get(ticker)
        if df is not None and len(df) >= 2:
            close = df["Close"].squeeze()
            current = float(close.iloc[-1])
            prev = float(close.iloc[-2])
            change = ((current - prev) / prev) * 100
            name = STOCK_NAMES.get(ticker, ticker)

            movers.append({
                "ticker": ticker, "name": name,
                "price": round(current, 2), "change": round(change, 2),
                "market": "US" if ticker in US_STOCKS else "EU",
            })

    gainers = sorted(movers, key=lambda x: x["change"], reverse=True)[:n]
    losers = sorted(movers, key=lambda x: x["change"])[:n]
    return {"gainers": gainers, "losers": losers}


def get_sector_performance():
    """Get performance of major sectors via ETFs."""
    data = _batch_download(list(SECTOR_ETFS.keys()), period="1mo", interval="1d")

    sectors = []
    for ticker, name in SECTOR_ETFS.items():
        df = data.get(ticker)
        if df is not None and len(df) >= 2:
            close = df["Close"].squeeze()
            current = float(close.iloc[-1])
            prev_day = float(close.iloc[-2])
            first = float(close.iloc[0])

            daily_change = ((current - prev_day) / prev_day) * 100
            monthly_change = ((current - first) / first) * 100

            sectors.append({
                "sector": name, "ticker": ticker,
                "price": round(current, 2),
                "daily_change": round(daily_change, 2),
                "monthly_change": round(monthly_change, 2),
            })

    sectors.sort(key=lambda x: x["monthly_change"], reverse=True)
    return sectors


def get_portfolio_simulation(profile="moderate", investment=10000, timeframe_months=12, max_tickers=0):
    """
    Build an actionable portfolio with specific ETFs/stocks,
    current prices, exact fractional shares to buy, and historical simulation.
    Supports fractional shares (Revolut, etc.).
    timeframe_months: number of months for simulation (1-60)
    max_tickers: 0 = use all holdings, otherwise limit to top N holdings
    """
    portfolio = PORTFOLIOS.get(profile, PORTFOLIOS["moderate"])
    all_holdings = portfolio["holdings"]

    # If max_tickers is set, take only the top N holdings and redistribute %
    if max_tickers > 0 and max_tickers < len(all_holdings):
        selected = all_holdings[:max_tickers]
        total_pct = sum(h["pct"] for h in selected)
        # Redistribute to sum to 100%
        holdings = []
        for h in selected:
            new_h = dict(h)
            new_h["pct"] = round(h["pct"] / total_pct * 100, 1)
            holdings.append(new_h)
    else:
        holdings = all_holdings
        max_tickers = len(all_holdings)

    tickers = [h["ticker"] for h in holdings]

    # Convert months to a start date for precise period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=timeframe_months * 30)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    # Get current prices (5d) and historical data using exact dates
    current_data = _batch_download(tickers, period="5d", interval="1d")

    # Download historical data with exact date range (with retries)
    historical_data = {}
    for ticker in tickers:
        df = _safe_download_daterange(ticker, start_str, end_str, interval="1d")
        if df is not None:
            historical_data[ticker] = df

    # Build actionable buy list with fractional shares
    buy_list = []
    total_allocated = 0

    for h in holdings:
        ticker = h["ticker"]
        df = current_data.get(ticker)
        if df is not None and len(df) >= 1:
            close = df["Close"].squeeze()
            current_price = float(close.iloc[-1])
            allocation_amount = round(investment * (h["pct"] / 100), 2)
            shares = round(allocation_amount / current_price, 4)  # Fractional shares
            total_allocated += allocation_amount

            buy_list.append({
                "ticker": ticker,
                "name": h["name"],
                "target_pct": h["pct"],
                "price": round(current_price, 2),
                "shares_to_buy": shares,
                "cost": allocation_amount,
                "why": h["why"],
            })
        else:
            buy_list.append({
                "ticker": ticker,
                "name": h["name"],
                "target_pct": h["pct"],
                "price": None,
                "shares_to_buy": 0,
                "cost": 0,
                "why": h["why"],
            })

    # Forward projection based on historical performance
    simulation = _project_portfolio(historical_data, holdings, investment, timeframe_months)

    # Concentration risk assessment
    if max_tickers <= 2:
        concentration = "Very High"
        concentration_color = "red"
    elif max_tickers <= 4:
        concentration = "High"
        concentration_color = "red"
    elif max_tickers <= 6:
        concentration = "Medium"
        concentration_color = "yellow"
    else:
        concentration = "Low"
        concentration_color = "green"

    # Format timeframe label
    if timeframe_months < 12:
        tf_label = f"{timeframe_months}mo"
    else:
        years = timeframe_months / 12
        tf_label = f"{years:.0f}y" if years == int(years) else f"{years:.1f}y"

    return {
        "profile": profile,
        "name": portfolio["name"],
        "description": portfolio["description"],
        "risk_level": portfolio["risk_level"],
        "target_return": portfolio["target_return"],
        "rebalance": portfolio["rebalance"],
        "investment": investment,
        "timeframe_months": timeframe_months,
        "timeframe_label": tf_label,
        "num_tickers": max_tickers,
        "total_tickers_available": len(all_holdings),
        "concentration_risk": concentration,
        "concentration_color": concentration_color,
        "total_allocated": round(total_allocated, 2),
        "cash_remaining": round(investment - total_allocated, 2),
        "buy_list": buy_list,
        "simulation": simulation,
    }


def _project_portfolio(historical_data, holdings, investment, projection_months):
    """
    Project portfolio performance into the future.
    Uses historical data to calculate annualized return and volatility per ticker,
    then projects forward with 3 scenarios: optimistic, expected, pessimistic.
    """
    ticker_stats = {}

    for h in holdings:
        ticker = h["ticker"]
        df = historical_data.get(ticker)
        if df is not None and len(df) > 20:
            close = df["Close"].squeeze()
            # Calculate daily returns
            daily_returns = close.pct_change().dropna()
            if len(daily_returns) < 10:
                continue

            # Annualized metrics
            mean_daily = float(daily_returns.mean())
            std_daily = float(daily_returns.std())
            trading_days = 252

            annualized_return = mean_daily * trading_days
            annualized_vol = std_daily * (trading_days ** 0.5)

            ticker_stats[ticker] = {
                "annual_return": annualized_return,
                "annual_vol": annualized_vol,
                "pct": h["pct"],
            }

    if not ticker_stats:
        return None

    # Calculate weighted portfolio return and volatility
    portfolio_annual_return = 0
    portfolio_annual_vol = 0
    total_weight = 0

    for ticker, stats in ticker_stats.items():
        w = stats["pct"] / 100
        portfolio_annual_return += w * stats["annual_return"]
        portfolio_annual_vol += w * stats["annual_vol"]  # Simplified (ignores correlation)
        total_weight += w

    if total_weight > 0:
        portfolio_annual_return /= total_weight
        portfolio_annual_vol /= total_weight

    # Monthly return and vol
    monthly_return = portfolio_annual_return / 12
    monthly_vol = portfolio_annual_vol / (12 ** 0.5)

    # Generate 3 scenarios: expected, optimistic (+1 std), pessimistic (-1 std)
    today = datetime.now()

    for scenario_name, multiplier in [("expected", 0), ("optimistic", 1), ("pessimistic", -1)]:
        value = investment
        points = [{"date": today.strftime("%Y-%m-%d"), "value": round(value, 2)}]

        for m in range(1, projection_months + 1):
            month_return = monthly_return + (multiplier * monthly_vol)
            value = value * (1 + month_return)
            future_date = today + timedelta(days=m * 30)
            points.append({
                "date": future_date.strftime("%Y-%m-%d"),
                "value": round(value, 2),
            })

        if scenario_name == "expected":
            expected_points = points
        elif scenario_name == "optimistic":
            optimistic_points = points
        else:
            pessimistic_points = points

    # Use expected scenario for main stats
    expected_end = expected_points[-1]["value"]
    optimistic_end = optimistic_points[-1]["value"]
    pessimistic_end = pessimistic_points[-1]["value"]

    expected_return = ((expected_end - investment) / investment) * 100
    optimistic_return = ((optimistic_end - investment) / investment) * 100
    pessimistic_return = ((pessimistic_end - investment) / investment) * 100

    expected_profit = expected_end - investment
    optimistic_profit = optimistic_end - investment
    pessimistic_profit = pessimistic_end - investment

    return {
        "start_date": today.strftime("%Y-%m-%d"),
        "end_date": (today + timedelta(days=projection_months * 30)).strftime("%Y-%m-%d"),
        "start_value": investment,
        "end_value": round(expected_end, 2),
        "total_return_pct": round(expected_return, 2),
        "profit": round(expected_profit, 2),
        "optimistic_value": round(optimistic_end, 2),
        "optimistic_return_pct": round(optimistic_return, 2),
        "optimistic_profit": round(optimistic_profit, 2),
        "pessimistic_value": round(pessimistic_end, 2),
        "pessimistic_return_pct": round(pessimistic_return, 2),
        "pessimistic_profit": round(pessimistic_profit, 2),
        "annual_return_pct": round(portfolio_annual_return * 100, 2),
        "annual_volatility_pct": round(portfolio_annual_vol * 100, 2),
        "monthly_data": expected_points,
        "optimistic_data": optimistic_points,
        "pessimistic_data": pessimistic_points,
    }


def get_strategies():
    """Return actionable investment strategies with specific tickers."""
    return {
        "action_plans": [
            {
                "name": "🎯 Quick Start: Just Tell Me What to Buy",
                "description": "Pick your risk level below and follow the exact buy list. Each portfolio tells you exactly which ETFs/stocks to buy, how many shares, and when to rebalance.",
                "steps": [
                    "1. Choose your risk profile: Conservative, Moderate, or Aggressive",
                    "2. Look at the 'Exact Buy List' — it shows ticker, shares, and cost",
                    "3. Open your broker (Fidelity, Schwab, Interactive Brokers, etc.)",
                    "4. Buy the exact shares listed for each ticker",
                    "5. Set a calendar reminder to rebalance (frequency shown per portfolio)",
                    "6. Check the 'Weekly Picks' tab for any tactical trades to add",
                ],
            },
            {
                "name": "📅 Weekly Routine (5 minutes)",
                "description": "What to do each week to stay on top of your investments.",
                "steps": [
                    "1. Monday: Check the 'Market Overview' tab — are markets up or down?",
                    "2. Check the 'Weekly Picks' tab — any Strong Buy signals?",
                    "3. If a pick has score > 50: Consider buying with 2-5% of your portfolio",
                    "4. Set stop-loss at the price shown in the recommendations",
                    "5. If a stock you own hits the target price: Sell half, trail-stop the rest",
                    "6. Friday: Check 'Top Movers' — any of your holdings in the losers list?",
                ],
            },
            {
                "name": "🔄 When to Sell Rules",
                "description": "Clear rules so you never have to guess when to sell.",
                "steps": [
                    "SELL if: Stock drops 5% below your buy price (stop-loss hit)",
                    "SELL HALF if: Stock gains 10%+ (lock in profits)",
                    "SELL if: Stock appears in Weekly Picks with 'Avoid/Sell' action",
                    "SELL if: You need the money within 6 months",
                    "DON'T SELL if: Market drops but your stock's fundamentals haven't changed",
                    "REBALANCE: If any position grows to 2x its target %, trim it back",
                ],
            },
        ],
        "portfolios": list(PORTFOLIOS.keys()),
    }


def get_todays_actions(investment=1000, strategy="best"):
    """
    Generate personalized "Today's Actions" — exact buy/sell recommendations.
    
    strategy:
        "quick"  — Short-term trades (1-2 weeks), momentum-based
        "long"   — Long-term holds (3-12 months), value/growth-based
        "best"   — Auto-mix of both (default)
    
    Returns a list of action cards with exact shares, costs, targets.
    """
    investment = max(1, float(investment))
    strategy = strategy if strategy in ("quick", "long", "best") else "best"

    tickers = US_STOCKS + EU_STOCKS
    data = _batch_download(tickers, period="3mo", interval="1d")

    if not data:
        raise RuntimeError(
            "Could not fetch stock data. Yahoo Finance may be rate-limiting. "
            "Try again in a minute."
        )

    quick_buys = []  # High momentum, short-term
    long_buys = []   # Undervalued, long-term
    sells = []       # Stocks to avoid/sell

    for ticker in tickers:
        df = data.get(ticker)
        if df is None:
            continue
        result = analyze_stock(ticker, df)
        if result is None:
            continue

        result["market"] = "US" if ticker in US_STOCKS else "EU"

        # Classify into quick/long/sell
        score = result["score"]
        rsi = result["rsi"]
        macd = result["macd_histogram"]
        vol_ratio = result["volume_ratio"]
        pct_1w = result["pct_1w"]

        if score <= -25:
            # SELL signal
            reason = _build_reason(result, "sell")
            result["reason"] = reason
            result["urgency"] = "Act now" if score <= -50 else "This week"
            sells.append(result)

        elif score >= 25 and macd > 0 and pct_1w > 0:
            # QUICK BUY — short-term momentum (relaxed criteria for more results)
            reason = _build_reason(result, "quick")
            result["reason"] = reason
            result["strategy_type"] = "quick"
            result["hold_label"] = "Quick Flip · 1-2 weeks"
            result["urgency"] = "Act now" if score >= 50 else "This week"
            quick_buys.append(result)

        elif score >= 15 and rsi < 55:
            # LONG BUY — good value, room to grow
            reason = _build_reason(result, "long")
            result["reason"] = reason
            result["strategy_type"] = "long"
            result["hold_label"] = "Long Hold · 3-12 months"
            result["urgency"] = "This week" if score >= 30 else "When convenient"
            long_buys.append(result)

    # Sort by score descending
    quick_buys.sort(key=lambda x: x["score"], reverse=True)
    long_buys.sort(key=lambda x: x["score"], reverse=True)
    sells.sort(key=lambda x: x["score"])

    # Select picks based on strategy
    if strategy == "quick":
        selected = quick_buys[:5]
    elif strategy == "long":
        selected = long_buys[:5]
    else:  # "best" — mix
        # Take top quick + top long, balanced
        n_quick = min(2, len(quick_buys))
        n_long = min(3, len(long_buys))
        # If not enough of one type, fill with the other
        if n_quick < 2 and len(long_buys) > n_long:
            n_long = min(5 - n_quick, len(long_buys))
        if n_long < 3 and len(quick_buys) > n_quick:
            n_quick = min(5 - n_long, len(quick_buys))
        selected = quick_buys[:n_quick] + long_buys[:n_long]
        selected.sort(key=lambda x: x["score"], reverse=True)
        selected = selected[:5]

    # Track if we had to fallback
    fallback_note = ""
    if not selected:
        if strategy == "quick":
            fallback_note = "⚠️ No Quick Flip opportunities found in current market conditions. Showing best available Long Hold picks instead."
            selected = long_buys[:5]
        elif strategy == "long":
            fallback_note = "⚠️ No Long Hold opportunities found. Showing best available Quick Flip picks instead."
            selected = quick_buys[:5]
        else:
            selected = long_buys[:3] if long_buys else quick_buys[:3]
            if not selected:
                fallback_note = "⚠️ Very few opportunities in current market. Consider holding cash."

    # Allocate investment across selected picks
    actions = []
    if selected:
        # Weight by score (higher score = more allocation)
        total_score = sum(max(s["score"], 1) for s in selected)
        remaining = investment

        for i, pick in enumerate(selected):
            weight = max(pick["score"], 1) / total_score
            # Last pick gets remaining to avoid rounding issues
            if i == len(selected) - 1:
                alloc = round(remaining, 2)
            else:
                alloc = round(investment * weight, 2)
                remaining -= alloc

            shares = round(alloc / pick["price"], 4) if pick["price"] > 0 else 0

            actions.append({
                "action": "BUY",
                "ticker": pick["ticker"],
                "name": pick["name"],
                "market": pick["market"],
                "price": pick["price"],
                "invest_amount": alloc,
                "shares": shares,
                "stop_loss": pick["stop_loss"],
                "target_price": pick["target_price"],
                "potential_gain_pct": round((pick["target_price"] - pick["price"]) / pick["price"] * 100, 1),
                "potential_loss_pct": round((pick["stop_loss"] - pick["price"]) / pick["price"] * 100, 1),
                "strategy_type": pick.get("strategy_type", "long"),
                "hold_label": pick.get("hold_label", "Hold"),
                "urgency": pick.get("urgency", "This week"),
                "reason": pick.get("reason", ""),
                "score": pick["score"],
                "rsi": pick["rsi"],
                "pct_1w": pick["pct_1w"],
                "pct_1m": pick["pct_1m"],
            })

    # Build sell alerts (top 3)
    sell_alerts = []
    for s in sells[:3]:
        sell_alerts.append({
            "action": "SELL" if s["score"] <= -50 else "AVOID",
            "ticker": s["ticker"],
            "name": s["name"],
            "market": s["market"],
            "price": s["price"],
            "reason": s.get("reason", ""),
            "score": s["score"],
            "urgency": s.get("urgency", "This week"),
            "pct_1w": s["pct_1w"],
            "pct_1m": s["pct_1m"],
        })

    # Market sentiment summary
    all_scores = []
    for ticker in tickers:
        df = data.get(ticker)
        if df is not None:
            r = analyze_stock(ticker, df)
            if r:
                all_scores.append(r["score"])

    avg_score = np.mean(all_scores) if all_scores else 0
    if avg_score > 20:
        sentiment = {"label": "🟢 Bullish", "color": "green", "desc": "Markets look strong — good time to buy"}
    elif avg_score > 0:
        sentiment = {"label": "🟡 Neutral", "color": "yellow", "desc": "Mixed signals — be selective"}
    else:
        sentiment = {"label": "🔴 Bearish", "color": "red", "desc": "Markets are weak — be cautious, consider holding cash"}

    return {
        "investment": investment,
        "strategy": strategy,
        "strategy_label": {"quick": "🔄 Quick Flip", "long": "📈 Long Hold", "best": "⭐ Best Mix"}[strategy],
        "sentiment": sentiment,
        "actions": actions,
        "sell_alerts": sell_alerts,
        "total_picks": len(actions),
        "cash_remaining": round(investment - sum(a["invest_amount"] for a in actions), 2),
        "fallback_note": fallback_note,
    }


def _build_reason(result, action_type):
    """Build a human-readable one-line reason for a recommendation."""
    parts = []
    rsi = result["rsi"]
    macd = result["macd_histogram"]
    vol = result["volume_ratio"]
    pct_1w = result["pct_1w"]
    pct_1m = result["pct_1m"]
    price = result["price"]
    sma_20 = result["sma_20"]

    if action_type == "sell":
        if rsi > 70:
            parts.append("Overbought (RSI {:.0f})".format(rsi))
        if macd < 0:
            parts.append("Bearish momentum")
        if pct_1w < -3:
            parts.append("Down {:.1f}% this week".format(pct_1w))
        if pct_1m < -10:
            parts.append("Down {:.1f}% this month".format(pct_1m))
        if price < sma_20:
            parts.append("Below 20-day average")
    elif action_type == "quick":
        if macd > 0:
            parts.append("Bullish MACD crossover")
        if vol > 1.5:
            parts.append("Volume {:.1f}x above average".format(vol))
        if pct_1w > 2:
            parts.append("Up {:.1f}% this week".format(pct_1w))
        if rsi < 40:
            parts.append("Oversold bounce (RSI {:.0f})".format(rsi))
        elif 40 <= rsi <= 60:
            parts.append("Healthy momentum")
    else:  # long
        if rsi < 40:
            parts.append("Oversold (RSI {:.0f}) — good entry".format(rsi))
        elif rsi < 55:
            parts.append("Room to grow (RSI {:.0f})".format(rsi))
        if price > sma_20:
            parts.append("Above 20-day average")
        if pct_1m > 3:
            parts.append("Steady uptrend (+{:.1f}% month)".format(pct_1m))
        if macd > 0:
            parts.append("Positive momentum")

    return " · ".join(parts[:3]) if parts else "Technical signals favorable"


def check_holdings(tickers_str):
    """
    Check health of user's holdings. Takes comma-separated tickers.
    Returns status (green/yellow/red) and advice for each.
    """
    raw_tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]
    if not raw_tickers:
        return {"holdings": [], "summary": "No tickers provided"}

    # Limit to 20 tickers
    raw_tickers = raw_tickers[:20]

    data = _batch_download(raw_tickers, period="3mo", interval="1d")

    holdings = []
    for ticker in raw_tickers:
        df = data.get(ticker)
        if df is None:
            holdings.append({
                "ticker": ticker,
                "name": STOCK_NAMES.get(ticker, ticker),
                "status": "gray",
                "status_label": "⚪ No Data",
                "advice": "Could not fetch data for this ticker",
                "price": None,
                "pct_1w": None,
                "pct_1m": None,
            })
            continue

        result = analyze_stock(ticker, df)
        if result is None:
            holdings.append({
                "ticker": ticker,
                "name": STOCK_NAMES.get(ticker, ticker),
                "status": "gray",
                "status_label": "⚪ Insufficient Data",
                "advice": "Not enough historical data to analyze",
                "price": None,
                "pct_1w": None,
                "pct_1m": None,
            })
            continue

        score = result["score"]
        rsi = result["rsi"]
        pct_1w = result["pct_1w"]
        pct_1m = result["pct_1m"]

        # Determine status and advice
        if score >= 25:
            status = "green"
            status_label = "🟢 Looking Good"
            advice = "Hold — strong signals, no action needed"
        elif score >= 0:
            status = "yellow"
            status_label = "🟡 Watch"
            if rsi > 65:
                advice = "Consider taking partial profits — getting overbought"
            elif pct_1w < -2:
                advice = "Minor dip — hold if fundamentals unchanged"
            else:
                advice = "Neutral — hold and monitor weekly"
        elif score >= -25:
            status = "yellow"
            status_label = "🟡 Caution"
            advice = "Weakening signals — set a stop-loss if you haven't"
        else:
            status = "red"
            status_label = "🔴 Consider Selling"
            if pct_1m < -10:
                advice = f"Down {pct_1m:.1f}% this month — consider cutting losses"
            elif rsi > 70:
                advice = "Overbought and losing momentum — take profits"
            else:
                advice = "Multiple bearish signals — review your position"

        holdings.append({
            "ticker": ticker,
            "name": result["name"],
            "status": status,
            "status_label": status_label,
            "advice": advice,
            "price": result["price"],
            "pct_1w": result["pct_1w"],
            "pct_1m": result["pct_1m"],
            "score": score,
            "rsi": rsi,
            "stop_loss": result["stop_loss"],
            "target_price": result["target_price"],
        })

    # Summary
    greens = sum(1 for h in holdings if h["status"] == "green")
    yellows = sum(1 for h in holdings if h["status"] == "yellow")
    reds = sum(1 for h in holdings if h["status"] == "red")
    total = len(holdings)

    if reds > 0:
        summary = f"⚠️ {reds} holding(s) need attention!"
    elif yellows > total / 2:
        summary = "🟡 Portfolio is mixed — review yellow items"
    else:
        summary = "🟢 Portfolio looks healthy overall"

    return {
        "holdings": holdings,
        "summary": summary,
        "counts": {"green": greens, "yellow": yellows, "red": reds, "total": total},
    }


def analyze_portfolio_holdings(holdings, trade_history=None):
    """
    Analyze user's portfolio with purchase history.
    Each holding: {"ticker": "AMZN", "shares": 3, "buy_price": 185.50, "buy_date": "2026-04-04"}
    trade_history: list of closed trades for pattern analysis
    Returns analysis with P&L, advice (buy more / hold / sell), and current status.
    """
    # --- CONSOLIDATE same-ticker holdings into one entry ---
    consolidated = {}
    for h in holdings:
        ticker = h.get("ticker", "").upper().strip()
        shares = float(h.get("shares", 0))
        buy_price = float(h.get("buy_price", 0))
        buy_date = h.get("buy_date", "")
        if not ticker or shares <= 0 or buy_price <= 0:
            continue
        if ticker in consolidated:
            c = consolidated[ticker]
            # Weighted average buy price
            total_cost = c["shares"] * c["buy_price"] + shares * buy_price
            c["shares"] += shares
            c["buy_price"] = round(total_cost / c["shares"], 2)
            # Use earliest buy date
            if buy_date and (not c["buy_date"] or buy_date < c["buy_date"]):
                c["buy_date"] = buy_date
            c["num_lots"] = c.get("num_lots", 1) + 1
        else:
            consolidated[ticker] = {"ticker": ticker, "shares": shares, "buy_price": buy_price, "buy_date": buy_date, "num_lots": 1}

    merged_holdings = list(consolidated.values())

    tickers = list(set(h["ticker"] for h in merged_holdings))
    if not tickers:
        return {"holdings": [], "summary": "No valid tickers provided"}

    data = _batch_download(tickers, period="3mo", interval="1d")

    results = []
    total_invested = 0
    total_current_value = 0

    for h in merged_holdings:
        ticker = h["ticker"]
        shares = h["shares"]
        buy_price = h["buy_price"]
        buy_date = h.get("buy_date", "")
        num_lots = h.get("num_lots", 1)

        cost_basis = round(shares * buy_price, 2)
        total_invested += cost_basis

        df = data.get(ticker)
        if df is None:
            results.append({
                "ticker": ticker,
                "name": STOCK_NAMES.get(ticker, ticker),
                "shares": shares,
                "buy_price": buy_price,
                "buy_date": buy_date,
                "current_price": None,
                "cost_basis": cost_basis,
                "current_value": None,
                "pnl": None,
                "pnl_pct": None,
                "status": "gray",
                "status_label": "⚪ No Data",
                "advice": "Could not fetch data for this ticker",
                "days_held": None,
            })
            continue

        result = analyze_stock(ticker, df)
        if result is None:
            results.append({
                "ticker": ticker,
                "name": STOCK_NAMES.get(ticker, ticker),
                "shares": shares,
                "buy_price": buy_price,
                "buy_date": buy_date,
                "current_price": None,
                "cost_basis": cost_basis,
                "current_value": None,
                "pnl": None,
                "pnl_pct": None,
                "status": "gray",
                "status_label": "⚪ Insufficient Data",
                "advice": "Not enough data to analyze",
                "days_held": None,
            })
            continue

        current_price = result["price"]
        current_value = round(shares * current_price, 2)
        total_current_value += current_value
        pnl = round(current_value - cost_basis, 2)
        pnl_pct = round((pnl / cost_basis) * 100, 2) if cost_basis > 0 else 0

        # Calculate days held
        days_held = None
        if buy_date:
            try:
                bd = datetime.strptime(buy_date, "%Y-%m-%d")
                days_held = (datetime.now() - bd).days
            except (ValueError, TypeError):
                pass

        # Generate advice based on P&L + technical score + trend
        score = result["score"]
        rsi = result["rsi"]
        stock_trend = result.get("trend", "neutral")
        pct_from_high = result.get("pct_from_high", 0)

        # *** IMPROVED: Severe loss override ***
        if pnl_pct <= -30:
            # Down 30%+ = always flag as danger regardless of short-term signals
            status = "red"
            status_label = "🔴 Cut Losses"
            if stock_trend == "downtrend":
                advice = f"Down {pnl_pct:.1f}% in a downtrend — strongly consider selling to limit further losses"
            elif score > 0 and result.get("pct_1w", 0) > 3:
                advice = f"Down {pnl_pct:.1f}% with a short-term bounce — likely a dead cat bounce, consider selling"
            else:
                advice = f"Down {pnl_pct:.1f}% — severe loss, consider cutting and reallocating to stronger positions"
        elif pnl_pct <= -15:
            # Down 15-30%
            if score <= -10 or stock_trend == "downtrend":
                status = "red"
                status_label = "🔴 Sell"
                advice = f"Down {pnl_pct:.1f}% and in a downtrend — consider selling before further decline"
            elif score > 20:
                status = "yellow"
                status_label = "🟡 Recovering?"
                advice = f"Down {pnl_pct:.1f}% but showing recovery signals — hold with tight stop-loss at ${round(current_price * 0.93, 2)}"
            else:
                status = "red"
                status_label = "🔴 Consider Selling"
                advice = f"Down {pnl_pct:.1f}% — set stop-loss at ${round(current_price * 0.95, 2)} or sell"
        elif pnl_pct <= -5:
            # Losing position (5-15%)
            if score <= -25:
                status = "red"
                status_label = "🔴 Sell"
                advice = f"Down {pnl_pct:.1f}% and bearish signals — consider cutting losses"
            elif score <= 0:
                status = "red"
                status_label = "🔴 Consider Selling"
                advice = f"Down {pnl_pct:.1f}% — set stop-loss at ${round(current_price * 0.95, 2)} if you hold"
            else:
                status = "yellow"
                status_label = "🟡 Hold & Watch"
                advice = f"Down {pnl_pct:.1f}% but signals improving — hold, may recover"
        elif pnl_pct >= 10:
            # Winning position
            if score <= -10:
                status = "yellow"
                status_label = "🟡 Take Profits"
                advice = f"Up {pnl_pct:.1f}% but momentum fading — sell half, trail-stop the rest"
            elif rsi > 70:
                status = "yellow"
                status_label = "🟡 Overbought"
                advice = f"Up {pnl_pct:.1f}% and overbought — consider taking partial profits"
            else:
                status = "green"
                status_label = "🟢 Winner"
                advice = f"Up {pnl_pct:.1f}% with strong signals — hold and ride the trend"
        elif pnl_pct >= 0:
            # Small gain
            if score >= 25:
                status = "green"
                status_label = "🟢 Buy More"
                advice = f"Up {pnl_pct:.1f}% with bullish signals — consider adding to position"
            else:
                status = "green"
                status_label = "🟢 Hold"
                advice = f"Up {pnl_pct:.1f}% — hold, no action needed"
        else:
            # Small loss (0 to -5%)
            if score >= 25:
                status = "yellow"
                status_label = "🟡 Buy the Dip"
                advice = f"Down {pnl_pct:.1f}% but bullish signals — good opportunity to average down"
            else:
                status = "yellow"
                status_label = "🟡 Watch"
                advice = f"Down {pnl_pct:.1f}% — hold but set stop-loss at ${round(buy_price * 0.90, 2)}"

        days_label = f"{days_held}d" if days_held is not None else "?"

        results.append({
            "ticker": ticker,
            "name": result["name"],
            "shares": shares,
            "buy_price": buy_price,
            "buy_date": buy_date,
            "days_held": days_held,
            "days_label": days_label,
            "current_price": current_price,
            "cost_basis": cost_basis,
            "current_value": current_value,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "status": status,
            "status_label": status_label,
            "advice": advice,
            "score": score,
            "rsi": rsi,
            "stop_loss": result["stop_loss"],
            "target_price": result["target_price"],
        })

    # Portfolio summary
    total_pnl = round(total_current_value - total_invested, 2)
    total_pnl_pct = round((total_pnl / total_invested) * 100, 2) if total_invested > 0 else 0

    greens = sum(1 for r in results if r["status"] == "green")
    yellows = sum(1 for r in results if r["status"] == "yellow")
    reds = sum(1 for r in results if r["status"] == "red")

    if total_pnl >= 0:
        summary = f"🟢 Portfolio is up ${total_pnl:,.2f} ({total_pnl_pct:+.1f}%)"
    else:
        summary = f"🔴 Portfolio is down ${total_pnl:,.2f} ({total_pnl_pct:+.1f}%)"

    # Analyze trade history if provided
    trade_stats = _analyze_trade_history(trade_history) if trade_history else None

    return {
        "holdings": results,
        "summary": summary,
        "total_invested": total_invested,
        "total_current_value": round(total_current_value, 2),
        "total_pnl": total_pnl,
        "total_pnl_pct": total_pnl_pct,
        "counts": {"green": greens, "yellow": yellows, "red": reds, "total": len(results)},
        "trade_stats": trade_stats,
    }


def _analyze_trade_history(trade_history):
    """
    Analyze closed trades to find patterns and generate insights.
    Each trade: {ticker, shares, buy_price, buy_date, sell_price, sell_date}
    """
    if not trade_history:
        return None

    wins = []
    losses = []
    all_returns = []
    all_days = []

    for t in trade_history:
        try:
            buy_price = float(t.get("buy_price", 0))
            sell_price = float(t.get("sell_price", 0))
            shares = float(t.get("shares", 0))
            if buy_price <= 0 or sell_price <= 0 or shares <= 0:
                continue

            pnl = (sell_price - buy_price) * shares
            pnl_pct = ((sell_price - buy_price) / buy_price) * 100

            days_held = None
            buy_date = t.get("buy_date", "")
            sell_date = t.get("sell_date", "")
            if buy_date and sell_date:
                try:
                    bd = datetime.strptime(buy_date, "%Y-%m-%d")
                    sd = datetime.strptime(sell_date, "%Y-%m-%d")
                    days_held = (sd - bd).days
                    all_days.append(days_held)
                except (ValueError, TypeError):
                    pass

            trade_data = {
                "ticker": t.get("ticker", "?"),
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl_pct, 2),
                "days_held": days_held,
            }

            all_returns.append(pnl_pct)

            if pnl >= 0:
                wins.append(trade_data)
            else:
                losses.append(trade_data)

        except (ValueError, TypeError):
            continue

    total_trades = len(wins) + len(losses)
    if total_trades == 0:
        return None

    win_rate = round((len(wins) / total_trades) * 100, 1)
    avg_return = round(np.mean(all_returns), 2) if all_returns else 0
    avg_win = round(np.mean([w["pnl_pct"] for w in wins]), 2) if wins else 0
    avg_loss = round(np.mean([l["pnl_pct"] for l in losses]), 2) if losses else 0
    avg_days = round(np.mean(all_days), 1) if all_days else None

    total_profit = round(sum(w["pnl"] for w in wins), 2)
    total_loss = round(sum(l["pnl"] for l in losses), 2)
    net_pnl = round(total_profit + total_loss, 2)

    best_trade = max(wins + losses, key=lambda x: x["pnl_pct"]) if (wins or losses) else None
    worst_trade = min(wins + losses, key=lambda x: x["pnl_pct"]) if (wins or losses) else None

    # Generate insights
    insights = []
    if win_rate >= 60:
        insights.append("🟢 Strong win rate! Your stock picking is above average.")
    elif win_rate >= 40:
        insights.append("🟡 Average win rate. Focus on cutting losers faster.")
    else:
        insights.append("🔴 Low win rate. Consider using stop-losses more aggressively.")

    if avg_win > 0 and avg_loss < 0:
        risk_reward = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        if risk_reward >= 2:
            insights.append(f"🟢 Great risk/reward ratio ({risk_reward:.1f}:1). Your winners outpace losers.")
        elif risk_reward >= 1:
            insights.append(f"🟡 Decent risk/reward ({risk_reward:.1f}:1). Try to let winners run longer.")
        else:
            insights.append(f"🔴 Poor risk/reward ({risk_reward:.1f}:1). Your losses are bigger than wins — tighten stop-losses.")

    if avg_days is not None:
        if avg_days < 7:
            insights.append("⚡ You trade very frequently. Consider holding longer for bigger gains.")
        elif avg_days > 90:
            insights.append("🐢 You hold for a long time. Make sure to take profits when targets are hit.")

    return {
        "total_trades": total_trades,
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": win_rate,
        "avg_return_pct": avg_return,
        "avg_win_pct": avg_win,
        "avg_loss_pct": avg_loss,
        "avg_days_held": avg_days,
        "total_profit": total_profit,
        "total_loss": total_loss,
        "net_pnl": net_pnl,
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "insights": insights,
    }


def calculate_goal(target_profit, months):
    """
    Goal calculator: determine what to invest and where to generate target profit.
    Returns a list of stock/ETF picks sorted by least capital needed.
    """
    # Validate inputs
    target_profit = max(1, float(target_profit))
    months = max(1, min(60, int(months)))

    # Get historical data for all stocks to calculate expected returns
    all_tickers = US_STOCKS + EU_STOCKS
    etf_tickers = ["VOO", "QQQ", "VGK", "SCHD", "BND", "IWM", "VWO", "GLD"]
    all_tickers = etf_tickers + all_tickers

    data = _batch_download(all_tickers, period="1y", interval="1d")

    if not data:
        raise RuntimeError(
            "Could not fetch stock data. Yahoo Finance may be rate-limiting requests. "
            "Try again in a minute."
        )

    picks = []
    for ticker in all_tickers:
        df = data.get(ticker)
        if df is None or len(df) < 60:
            continue
        close = df["Close"].squeeze()
        daily_returns = close.pct_change().dropna()
        if len(daily_returns) < 30:
            continue

        mean_daily = float(daily_returns.mean())
        std_daily = float(daily_returns.std())
        current_price = float(close.iloc[-1])

        # Monthly projections
        monthly_return = mean_daily * 21  # ~21 trading days/month
        monthly_vol = std_daily * (21 ** 0.5)

        # Expected return over the timeframe
        expected_return = monthly_return * months
        optimistic_return = (monthly_return + monthly_vol) * months
        pessimistic_return = (monthly_return - monthly_vol) * months

        if expected_return <= 0:
            continue  # Skip stocks with negative expected returns

        # How much to invest to generate target_profit (expected case)
        investment_needed = target_profit / expected_return if expected_return > 0 else 999999
        optimistic_profit = investment_needed * optimistic_return
        pessimistic_profit = investment_needed * pessimistic_return

        # RSI for recommendation color
        rsi_series = compute_rsi(close)
        current_rsi = float(rsi_series.iloc[-1]) if not np.isnan(rsi_series.iloc[-1]) else 50

        # Feasibility score
        if expected_return > 0.15:
            feasibility = "🟢 Very Feasible"
            feas_color = "green"
        elif expected_return > 0.05:
            feasibility = "🟡 Feasible"
            feas_color = "yellow"
        elif expected_return > 0:
            feasibility = "🟠 Possible"
            feas_color = "yellow"
        else:
            feasibility = "🔴 Unlikely"
            feas_color = "red"

        name = STOCK_NAMES.get(ticker, ticker)
        is_etf = ticker in etf_tickers

        picks.append({
            "ticker": ticker,
            "name": name,
            "is_etf": is_etf,
            "price": round(current_price, 2),
            "investment_needed": round(investment_needed, 2),
            "expected_return_pct": round(expected_return * 100, 2),
            "expected_profit": round(target_profit, 2),
            "optimistic_profit": round(optimistic_profit, 2),
            "pessimistic_profit": round(pessimistic_profit, 2),
            "optimistic_return_pct": round(optimistic_return * 100, 2),
            "pessimistic_return_pct": round(pessimistic_return * 100, 2),
            "rsi": round(current_rsi, 1),
            "volatility_pct": round(std_daily * (252**0.5) * 100, 1),
            "feasibility": feasibility,
            "feasibility_color": feas_color,
        })

    # Sort by investment needed (ascending = cheapest way to reach goal)
    picks.sort(key=lambda x: x["investment_needed"])

    return {
        "target_profit": target_profit,
        "months": months,
        "picks": picks[:20],  # Top 20
    }


# ---------------------------------------------------------------------------
# Stock Search — analyze any ticker on the fly
# ---------------------------------------------------------------------------

def search_ticker(ticker_str):
    """
    Search and analyze any Yahoo Finance ticker (not limited to the 200 list).
    Downloads 1 year of data for full analysis including 200-day SMA.
    """
    ticker = ticker_str.strip().upper()
    if not ticker:
        return {"error": "No ticker provided"}

    # Download 1 year of data for comprehensive analysis
    df = _safe_download(ticker, period="1y", interval="1d")
    if df is None or len(df) < 5:
        return {"error": f"Could not find data for '{ticker}'. Check the ticker symbol."}

    result = analyze_stock(ticker, df)
    if result is None:
        return {"error": f"Not enough data to analyze '{ticker}'."}

    # Add market classification
    if ticker in US_STOCKS:
        result["market"] = "US"
    elif ticker in EU_STOCKS:
        result["market"] = "EU"
    elif "=" in ticker:
        result["market"] = "Commodity"
    else:
        result["market"] = "Other"

    result["in_universe"] = ticker in US_STOCKS or ticker in EU_STOCKS

    return result


# ---------------------------------------------------------------------------
# Chat Context — build context for AI chatbot
# ---------------------------------------------------------------------------

def get_market_regime():
    """
    Detect current market regime: bull, bear, or sideways.
    Uses S&P 500 as the primary indicator.
    Returns regime info for adjusting recommendations.
    """
    df = _safe_download("^GSPC", period="6mo", interval="1d")
    if df is None or len(df) < 50:
        return {"regime": "unknown", "description": "Could not determine market regime"}

    close = df["Close"].squeeze()
    current = float(close.iloc[-1])

    sma_50 = float(close.rolling(50).mean().iloc[-1])
    sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None

    pct_1m = float((close.iloc[-1] / close.iloc[-21] - 1) * 100) if len(close) >= 21 else 0
    pct_3m = float((close.iloc[-1] / close.iloc[-63] - 1) * 100) if len(close) >= 63 else 0

    # Determine regime
    if sma_200 and current > sma_200 and current > sma_50 and pct_3m > 5:
        regime = "bull"
        desc = "Strong bull market — stocks trending up, good time for growth picks"
        strategy_hint = "Favor growth stocks, tech, and aggressive positions. Reduce bonds."
    elif sma_200 and current < sma_200 and pct_3m < -5:
        regime = "bear"
        desc = "Bear market — stocks trending down, be defensive"
        strategy_hint = "Favor bonds (BND), gold (GLD), dividends (SCHD). Avoid speculative stocks."
    elif pct_1m < -3 and pct_3m < 0:
        regime = "correction"
        desc = "Market correction — pullback in progress"
        strategy_hint = "Hold cash, look for oversold quality stocks to buy the dip."
    else:
        regime = "sideways"
        desc = "Sideways/mixed market — no clear direction"
        strategy_hint = "Be selective. Mix of value and growth. Keep some cash ready."

    return {
        "regime": regime,
        "description": desc,
        "strategy_hint": strategy_hint,
        "sp500_price": round(current, 2),
        "sp500_vs_sma50": round(((current - sma_50) / sma_50) * 100, 2),
        "sp500_vs_sma200": round(((current - sma_200) / sma_200) * 100, 2) if sma_200 else None,
        "sp500_1m": round(pct_1m, 2),
        "sp500_3m": round(pct_3m, 2),
    }


def get_ai_analysis_context(holdings=None, trade_history=None):
    """
    Build enhanced context for AI analysis including market regime,
    portfolio details, trade patterns, and specific analysis requests.
    Used for AI-enhanced stock analysis and smarter recommendations.
    """
    context_parts = []

    # Market regime
    try:
        regime = get_market_regime()
        context_parts.append(f"=== CURRENT MARKET REGIME ===")
        context_parts.append(f"Regime: {regime['regime'].upper()}")
        context_parts.append(f"S&P 500: ${regime['sp500_price']} ({regime['sp500_1m']:+.1f}% 1M, {regime['sp500_3m']:+.1f}% 3M)")
        context_parts.append(f"Assessment: {regime['description']}")
        context_parts.append(f"Strategy: {regime['strategy_hint']}")
    except Exception:
        context_parts.append("=== MARKET REGIME: Unknown (data unavailable) ===")

    # Portfolio details with P&L
    if holdings and len(holdings) > 0:
        context_parts.append(f"\n=== USER'S ACTIVE PORTFOLIO ===")
        for h in holdings[:20]:
            ticker = h.get("ticker", "?")
            shares = h.get("shares", 0)
            buy_price = h.get("buy_price", 0)
            buy_date = h.get("buy_date", "?")
            context_parts.append(f"- {ticker}: {shares} shares @ ${buy_price} (bought {buy_date})")

    # Trade history patterns
    if trade_history and len(trade_history) > 0:
        wins = sum(1 for t in trade_history if float(t.get("sell_price", 0)) > float(t.get("buy_price", 0)))
        total = len(trade_history)
        win_rate = round((wins / total) * 100, 1) if total > 0 else 0

        avg_hold_days = []
        avg_win_pct = []
        avg_loss_pct = []
        for t in trade_history:
            bp = float(t.get("buy_price", 0))
            sp = float(t.get("sell_price", 0))
            if bp > 0:
                pct = ((sp - bp) / bp) * 100
                if pct >= 0:
                    avg_win_pct.append(pct)
                else:
                    avg_loss_pct.append(pct)
            if t.get("buy_date") and t.get("sell_date"):
                try:
                    days = (datetime.strptime(t["sell_date"], "%Y-%m-%d") - datetime.strptime(t["buy_date"], "%Y-%m-%d")).days
                    avg_hold_days.append(days)
                except (ValueError, TypeError):
                    pass

        context_parts.append(f"\n=== TRADING PATTERNS ===")
        context_parts.append(f"Total trades: {total}, Win rate: {win_rate}%")
        if avg_win_pct:
            context_parts.append(f"Avg winning trade: +{np.mean(avg_win_pct):.1f}%")
        if avg_loss_pct:
            context_parts.append(f"Avg losing trade: {np.mean(avg_loss_pct):.1f}%")
        if avg_hold_days:
            context_parts.append(f"Avg holding period: {np.mean(avg_hold_days):.0f} days")

        # Pattern insights
        if avg_win_pct and avg_loss_pct:
            if np.mean(avg_win_pct) < abs(np.mean(avg_loss_pct)):
                context_parts.append("⚠️ PATTERN: User's losses are bigger than wins — needs tighter stop-losses")
            if avg_hold_days and np.mean(avg_hold_days) < 7:
                context_parts.append("⚠️ PATTERN: User trades very frequently — may benefit from longer holds")

        context_parts.append("Recent trades:")
        for t in trade_history[-5:]:
            bp = float(t.get("buy_price", 0))
            sp = float(t.get("sell_price", 0))
            pnl_pct = ((sp - bp) / bp * 100) if bp > 0 else 0
            context_parts.append(f"  {t.get('ticker','?')}: ${bp:.2f} → ${sp:.2f} ({pnl_pct:+.1f}%)")

    return "\n".join(context_parts)


def get_stock_news(ticker_str):
    """
    Get recent news headlines for a stock using yfinance.
    Returns headlines that the AI can analyze for sentiment.
    """
    ticker = ticker_str.strip().upper()
    try:
        t = yf.Ticker(ticker)
        news = t.news if hasattr(t, 'news') else []
        headlines = []
        for item in (news or [])[:8]:
            title = item.get("title", "")
            publisher = item.get("publisher", "")
            link = item.get("link", "")
            pub_date = ""
            if item.get("providerPublishTime"):
                pub_date = datetime.fromtimestamp(item["providerPublishTime"]).strftime("%Y-%m-%d")
            if title:
                headlines.append({
                    "title": title,
                    "publisher": publisher,
                    "date": pub_date,
                    "link": link,
                })
        return {"ticker": ticker, "headlines": headlines, "count": len(headlines)}
    except Exception as e:
        return {"ticker": ticker, "headlines": [], "count": 0, "error": str(e)}


def get_earnings_info(ticker_str):
    """
    Check if a stock has upcoming earnings.
    Returns earnings date if available.
    """
    ticker = ticker_str.strip().upper()
    try:
        t = yf.Ticker(ticker)
        cal = t.calendar if hasattr(t, 'calendar') else None
        if cal is not None and not (isinstance(cal, pd.DataFrame) and cal.empty):
            # Try to extract earnings date
            if isinstance(cal, dict):
                earnings_date = cal.get("Earnings Date", [])
                if earnings_date:
                    if isinstance(earnings_date, list) and len(earnings_date) > 0:
                        ed = earnings_date[0]
                        if hasattr(ed, 'strftime'):
                            return {"ticker": ticker, "earnings_date": ed.strftime("%Y-%m-%d"), "has_upcoming": True}
                        return {"ticker": ticker, "earnings_date": str(ed), "has_upcoming": True}
            elif isinstance(cal, pd.DataFrame):
                if "Earnings Date" in cal.columns:
                    dates = cal["Earnings Date"].tolist()
                    if dates:
                        return {"ticker": ticker, "earnings_date": str(dates[0]), "has_upcoming": True}
        return {"ticker": ticker, "earnings_date": None, "has_upcoming": False}
    except Exception:
        return {"ticker": ticker, "earnings_date": None, "has_upcoming": False}


def get_portfolio_intelligence(holdings, trade_history=None):
    """
    Get comprehensive intelligence for portfolio holdings:
    - News headlines for each stock
    - Earnings calendar warnings
    - Market regime context
    Returns enriched data for AI analysis.
    """
    intelligence = {
        "news": {},
        "earnings_warnings": [],
        "market_regime": None,
    }

    # Get market regime
    try:
        intelligence["market_regime"] = get_market_regime()
    except Exception:
        pass

    # Get news and earnings for each holding
    tickers = list(set(h.get("ticker", "").upper().strip() for h in holdings if h.get("ticker")))[:10]

    for ticker in tickers:
        # News
        try:
            news = get_stock_news(ticker)
            if news["count"] > 0:
                intelligence["news"][ticker] = news["headlines"][:3]  # Top 3 headlines
        except Exception:
            pass

        # Earnings
        try:
            earnings = get_earnings_info(ticker)
            if earnings.get("has_upcoming"):
                intelligence["earnings_warnings"].append({
                    "ticker": ticker,
                    "date": earnings["earnings_date"],
                    "warning": f"⚠️ {ticker} has earnings coming up on {earnings['earnings_date']} — expect high volatility"
                })
        except Exception:
            pass

    return intelligence


def get_chat_context(holdings=None, trade_history=None):
    """
    Build a context summary for the AI chatbot.
    Returns a text summary of portfolio, market conditions, and recommendations.
    """
    context_parts = []

    # Market sentiment (quick check using cached data if available)
    context_parts.append("=== MARKET CONDITIONS ===")
    context_parts.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    context_parts.append(f"Stock universe: {len(US_STOCKS)} US + {len(EU_STOCKS)} EU stocks tracked")

    # Portfolio summary
    if holdings and len(holdings) > 0:
        context_parts.append("\n=== USER'S PORTFOLIO (Active Holdings) ===")
        for h in holdings[:20]:
            ticker = h.get("ticker", "?")
            shares = h.get("shares", 0)
            buy_price = h.get("buy_price", 0)
            buy_date = h.get("buy_date", "?")
            context_parts.append(f"- {ticker}: {shares} shares, bought at ${buy_price} on {buy_date}")

    # Trade history summary
    if trade_history and len(trade_history) > 0:
        wins = sum(1 for t in trade_history if float(t.get("sell_price", 0)) > float(t.get("buy_price", 0)))
        losses = len(trade_history) - wins
        total = len(trade_history)
        win_rate = round((wins / total) * 100, 1) if total > 0 else 0

        context_parts.append(f"\n=== TRADE HISTORY ===")
        context_parts.append(f"Total closed trades: {total}")
        context_parts.append(f"Wins: {wins}, Losses: {losses}, Win rate: {win_rate}%")

        # Last 5 trades
        context_parts.append("Recent trades:")
        for t in trade_history[-5:]:
            ticker = t.get("ticker", "?")
            bp = float(t.get("buy_price", 0))
            sp = float(t.get("sell_price", 0))
            pnl_pct = ((sp - bp) / bp * 100) if bp > 0 else 0
            context_parts.append(f"  {ticker}: ${bp:.2f} → ${sp:.2f} ({pnl_pct:+.1f}%)")

    context_parts.append("\n=== YOUR IDENTITY ===")
    context_parts.append("You are Marcus, a Senior Portfolio Strategist at a top-tier investment firm. You manage $50M+ in client assets across US and EU equities, ETFs, commodities, and crypto. You have 20+ years of experience in technical analysis, risk management, and portfolio construction.")
    context_parts.append("")
    context_parts.append("=== YOUR PERSONALITY ===")
    context_parts.append("- Direct and confident, like a trusted advisor talking over coffee")
    context_parts.append("- You use NUMBERS, not vague language ('NVDA is 12% below its 200-day SMA at $198' NOT 'NVDA looks weak')")
    context_parts.append("- Slightly opinionated — you have views and defend them with data")
    context_parts.append("- You admit uncertainty honestly when data is missing")
    context_parts.append("- You explain complex concepts simply for beginners, but don't dumb things down for experienced users")
    context_parts.append("")
    context_parts.append("=== ANALYSIS FRAMEWORK (use for every stock question) ===")
    context_parts.append("1. PRICE ACTION: Current price vs key levels (SMA 50/200, 52-week high/low, support/resistance)")
    context_parts.append("2. MOMENTUM: RSI (overbought >70, oversold <30), MACD direction, trend (uptrend/downtrend/sideways)")
    context_parts.append("3. CONTEXT: Sector performance, market regime (bull/bear), catalysts, earnings, news")
    context_parts.append("4. VERDICT: Clear BUY / HOLD / SELL with conviction level (high/medium/low)")
    context_parts.append("5. ACTION: Entry price, stop-loss level, target price, suggested position size (% of portfolio)")
    context_parts.append("")
    context_parts.append("=== RESPONSE FORMAT ===")
    context_parts.append("- Lead with the answer FIRST, then explain why (don't bury the recommendation)")
    context_parts.append("- Use **bold** for key numbers, tickers, and verdicts")
    context_parts.append("- Use bullet points for multi-part analysis")
    context_parts.append("- Simple questions: 3-5 sentences. 'Analyze' requests: up to 10 sentences with the framework above")
    context_parts.append("- End with a one-line risk note: '⚠️ Do your own DD before trading.'")
    context_parts.append("")
    context_parts.append("=== PORTFOLIO ADVICE RULES ===")
    context_parts.append("- If a holding is down 20%+, be HONEST — suggest cutting losses unless there's a clear catalyst for recovery")
    context_parts.append("- If a holding is up 15%+, suggest taking partial profits (sell half, trail-stop the rest)")
    context_parts.append("- Never recommend more than 5% of portfolio in a single speculative stock")
    context_parts.append("- Always consider the user's EXISTING positions before recommending new ones (avoid over-concentration)")
    context_parts.append("- If the portfolio lacks diversification, flag it explicitly")
    context_parts.append("- Reference the user's win rate and trading patterns when giving advice")
    context_parts.append("")
    context_parts.append("=== WHAT NOT TO DO ===")
    context_parts.append("- NEVER say 'I don't have access to real-time data' — you DO, it's provided in the context above")
    context_parts.append("- NEVER give wishy-washy 'it depends' answers without following up with a specific recommendation")
    context_parts.append("- NEVER use the phrase 'not financial advice' or long disclaimers — just end with '⚠️ Do your own DD'")
    context_parts.append("- NEVER hallucinate prices — if a stock's data isn't in the context, say 'I don't have live data for that — search it using the search bar'")
    context_parts.append("- NEVER recommend buying a stock that's in a clear downtrend without flagging the risk")

    return "\n".join(context_parts)
