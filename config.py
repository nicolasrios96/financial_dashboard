"""
Configuration — Stock Universe, Names, Indices, Sectors, Commodities, Portfolios.
All data constants used across the financial dashboard.
"""

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
    # ===== Additional S&P 500 stocks =====
    "ABBV": "AbbVie Inc.", "WFC": "Wells Fargo", "PM": "Philip Morris Intl.",
    "CMCSA": "Comcast Corp.", "NEE": "NextEra Energy", "IBM": "IBM Corp.",
    "INTU": "Intuit Inc.", "SPGI": "S&P Global",
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
    "HEI": "HEICO Corp.", "ENTG": "Entegris Inc.",

    # ===== EU Stocks (80+) =====
    "ASML.AS": "ASML Holding", "INGA.AS": "ING Group", "PHIA.AS": "Philips NV",
    "AD.AS": "Ahold Delhaize", "WKL.AS": "Wolters Kluwer", "HEIA.AS": "Heineken NV",
    "MC.PA": "LVMH", "OR.PA": "L'Oréal", "AIR.PA": "Airbus SE",
    "BNP.PA": "BNP Paribas", "DG.PA": "Vinci SA", "RMS.PA": "Hermès",
    "TTE.PA": "TotalEnergies", "AI.PA": "Air Liquide", "SU.PA": "Schneider Electric",
    "EL.PA": "EssilorLuxottica", "CS.PA": "AXA SA", "BN.PA": "Danone SA",
    "KER.PA": "Kering SA", "SAF.PA": "Safran SA", "SAN.PA": "Sanofi SA",
    "STMPA.PA": "STMicroelectronics",
    "CAP.PA": "Capgemini SE", "RI.PA": "Pernod Ricard", "SGO.PA": "Saint-Gobain",
    "PUB.PA": "Publicis Groupe", "VIV.PA": "Vivendi SE",
    "SAP.DE": "SAP SE", "SIE.DE": "Siemens AG", "DTE.DE": "Deutsche Telekom",
    "ALV.DE": "Allianz SE", "BAS.DE": "BASF SE", "BAYN.DE": "Bayer AG",
    "ADS.DE": "Adidas AG", "MBG.DE": "Mercedes-Benz Group", "BMW.DE": "BMW AG",
    "VOW3.DE": "Volkswagen AG", "MUV2.DE": "Munich Re", "DBK.DE": "Deutsche Bank",
    "FRE.DE": "Fresenius SE",
    "IFX.DE": "Infineon Technologies", "HEN3.DE": "Henkel AG", "RHM.DE": "Rheinmetall AG",
    "MTX.DE": "MTU Aero Engines", "SHL.DE": "Siemens Healthineers", "PUM.DE": "Puma SE",
    "SAN.MC": "Banco Santander", "IBE.MC": "Iberdrola", "FER.MC": "Ferrovial SE",
    "ITX.MC": "Inditex SA", "TEF.MC": "Telefónica SA",
    "BBVA.MC": "BBVA", "AMS.MC": "Amadeus IT", "CABK.MC": "CaixaBank",
    "ENEL.MI": "Enel SpA", "ISP.MI": "Intesa Sanpaolo", "STLAM.MI": "Stellantis NV",
    "ENI.MI": "Eni SpA", "UCG.MI": "UniCredit SpA",
    "RACE.MI": "Ferrari NV", "G.MI": "Assicurazioni Generali",
    "ABI.BR": "AB InBev",
    "SHEL.L": "Shell plc", "AZN.L": "AstraZeneca", "HSBA.L": "HSBC Holdings",
    "BP.L": "BP plc", "GSK.L": "GSK plc", "RIO.L": "Rio Tinto",
    "ULVR.L": "Unilever plc", "LSEG.L": "London Stock Exchange",
    "DGE.L": "Diageo plc", "BATS.L": "British American Tobacco",
    "REL.L": "RELX plc", "AAL.L": "Anglo American",
    "NOVO-B.CO": "Novo Nordisk", "ERIC-B.ST": "Ericsson",
    "VOLV-B.ST": "Volvo Group",
    "NIBE-B.ST": "NIBE Industrier", "SAND.ST": "Sandvik AB",
    "MAERSK-B.CO": "A.P. Moller-Maersk",
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
    # EU-Domiciled ETFs
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
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL", "NFLX",
    "ADBE", "CRM", "INTC", "AMD", "CSCO", "PEP", "KO", "MRK", "ABT",
    "PFE", "TMO", "AVGO", "COST", "WMT", "XOM", "CVX", "LLY", "ORCL",
    "ACN", "MCD", "NKE", "TXN", "QCOM", "LOW", "UPS", "CAT", "BA",
    "GS", "MS", "BLK", "SCHW", "AXP",
    "UBER", "ABNB", "SQ", "SHOP", "PLTR", "NET", "CRWD", "SNOW",
    "DDOG", "MDB", "ZS", "PANW", "FTNT", "TEAM", "NOW", "WDAY",
    "VEEV", "TTD", "PINS", "SNAP", "ROKU", "ZM", "DASH", "RBLX", "U",
    "RIVN", "LCID", "ENPH", "FSLR", "PLUG",
    "COIN", "HOOD", "SOFI", "AFRM",
    "MRNA", "BIIB", "REGN", "VRTX", "GILD", "AMGN", "BMY", "ZTS",
    "ISRG", "DXCM", "IDXX",
    "TGT", "SBUX", "CMG", "LULU", "BKNG", "MAR",
    "RTX", "LMT", "GE", "HON", "DE", "MMM",
    "MRVL", "KLAC", "LRCX", "AMAT", "ON", "MU",
    "SPOT", "TTWO", "EA",
    "AMT", "PLD", "CCI", "O", "SPG",
    "ABBV", "WFC", "PM", "CMCSA", "NEE", "IBM", "INTU", "SPGI",
    "DHR", "SYK", "MDT", "CI", "ELV", "CB", "SO", "DUK", "ICE",
    "CL", "MCO", "CME", "PNC", "USB", "TFC", "AON", "ITW", "EMR",
    "NSC", "FDX", "GM", "F", "PSA", "WELL", "HCA", "MCK", "ADP",
    "FISV", "MSCI", "APD", "SHW", "ECL", "ROP", "CARR", "CTAS",
    "PAYX", "FAST", "ODFL", "CPRT", "VRSK", "MNST", "KDP",
    "DLTR", "DG", "ROST", "TJX", "ORLY", "AZO",
    "KMB", "GIS", "K", "HSY", "SJM", "HRL", "CLX", "CHD",
    "SMCI", "ARM", "PATH", "DUOL", "CFLT", "ESTC", "GTLB", "S",
    "IOT", "BILL",
    "AXON", "HWM", "TDG", "HEI",
]

EU_STOCKS = [
    "ASML.AS", "INGA.AS", "PHIA.AS", "AD.AS", "WKL.AS", "HEIA.AS",
    "MC.PA", "OR.PA", "AIR.PA", "BNP.PA", "DG.PA", "RMS.PA",
    "TTE.PA", "AI.PA", "SU.PA", "EL.PA", "CS.PA", "BN.PA",
    "KER.PA", "SAF.PA", "SAN.PA", "STMPA.PA",
    "CAP.PA", "RI.PA", "SGO.PA", "PUB.PA", "VIV.PA",
    "SAP.DE", "SIE.DE", "DTE.DE", "ALV.DE", "BAS.DE", "BAYN.DE",
    "ADS.DE", "MBG.DE", "BMW.DE", "VOW3.DE", "MUV2.DE", "DBK.DE", "FRE.DE",
    "IFX.DE", "HEN3.DE", "RHM.DE", "MTX.DE", "SHL.DE",
    "SAN.MC", "IBE.MC", "FER.MC", "ITX.MC", "TEF.MC",
    "BBVA.MC", "AMS.MC", "CABK.MC",
    "ENEL.MI", "ISP.MI", "STLAM.MI", "ENI.MI", "UCG.MI",
    "RACE.MI", "G.MI",
    "ABI.BR",
    "SHEL.L", "AZN.L", "HSBA.L", "BP.L", "GSK.L", "RIO.L", "ULVR.L", "LSEG.L",
    "DGE.L", "BATS.L", "REL.L", "AAL.L",
    "NOVO-B.CO", "ERIC-B.ST", "VOLV-B.ST",
    "NIBE-B.ST", "SAND.ST", "MAERSK-B.CO",
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
    "^GSPC": "S&P 500", "^IXIC": "NASDAQ", "^DJI": "Dow Jones", "^RUT": "Russell 2000",
}

EU_INDICES = {
    "^STOXX50E": "EURO STOXX 50", "^FTSE": "FTSE 100", "^GDAXI": "DAX 40",
    "^IBEX": "IBEX 35", "^FCHI": "CAC 40",
}

SECTOR_ETFS = {
    "XLK": "Technology", "XLF": "Financials", "XLV": "Healthcare",
    "XLE": "Energy", "XLY": "Consumer Discretionary", "XLP": "Consumer Staples",
    "XLI": "Industrials", "XLB": "Materials", "XLRE": "Real Estate",
    "XLU": "Utilities", "XLC": "Communication Services",
}

COMMODITY_FUTURES = {
    "GC=F": "Gold", "SI=F": "Silver", "CL=F": "Crude Oil (WTI)",
    "BZ=F": "Brent Crude", "NG=F": "Natural Gas", "HG=F": "Copper",
    "PL=F": "Platinum", "PA=F": "Palladium", "ZC=F": "Corn", "ZW=F": "Wheat",
}

COMMODITY_ETFS = ["GLD", "SLV", "USO", "PPLT", "DBA", "DBC", "PDBC", "COPX", "UNG"]

# Ticker aliases for common names
TICKER_ALIASES = {
    "XAU": "GC=F", "XAG": "SI=F", "XPT": "PL=F", "XPD": "PA=F",
    "GOLD": "GC=F", "SILVER": "SI=F",
    "XAUUSD=X": "GC=F", "XAGUSD=X": "SI=F", "XPTUSD=X": "PL=F", "XPDUSD=X": "PA=F",
}

# ---------------------------------------------------------------------------
# Portfolio definitions for each risk profile
# ---------------------------------------------------------------------------

PORTFOLIOS = {
    "conservative": {
        "name": "🟢 Conservative Portfolio",
        "description": "Low risk, steady income. Focus on bonds, dividends, and blue-chip stability.",
        "risk_level": "Low", "target_return": "5-7% annually", "rebalance": "Every 6 months",
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
        "risk_level": "Medium", "target_return": "8-11% annually", "rebalance": "Every 3 months",
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
        "risk_level": "High", "target_return": "12-18% annually", "rebalance": "Monthly review",
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
