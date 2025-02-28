
import pandas as pd
import yfinance as yf
import datetime
import time

# === Step 1: Connect to Public Google Sheets (No Authentication) ===
google_sheet_url = "https://docs.google.com/spreadsheets/d/1wxzhusybeXYntIjb0fyREViSu1-GcnOpUOG2yxkp7kQ/export?format=csv"
df = pd.read_csv(google_sheet_url)  # Read Google Sheet as CSV
tickers = df.iloc[:, 0].dropna().tolist()  # Get tickers from first column

# === Mapping Asset Classes to Benchmark ETFs ===
asset_class_benchmark = {
    "Technology": "XLK",
    "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP",
    "Healthcare": "XLV",
    "Financials": "XLF",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Utilities": "XLU",
    "Energy": "XLE",
    "Communication Services": "XLC",
    "US Stocks": "SPY",
    "Small Cap Stocks": "IWM",
    "Crypto": "BITO",
    "Bonds": "BND",
    "Gold": "GLD",
    "Real Estate": "VNQ",
    "International Stocks": "ACWI"
}

# === Function to Get YTD Performance ===
def get_ytd_performance(ticker):
    try:
        time.sleep(2)  # Prevent rate limiting
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")

        if hist.empty:
            print(f"⚠️ No data for {ticker}")
            return None

        # Filter to only include this year's data
        this_year = datetime.datetime.now().year
        hist = hist[hist.index.year == this_year]

        if hist.empty:
            print(f"⚠️ No data available for {ticker} in {this_year}")
            return None

        first_price = hist["Close"].iloc[0]
        current_price = hist["Close"].iloc[-1]

        return round(((current_price - first_price) / first_price) * 100, 2)
    except Exception as e:
        print(f"⚠️ Error fetching data for {ticker}: {e}")
        return None

# === Function to Get Stock Sector ===
def get_stock_sector(ticker):
    try:
        time.sleep(2)  # Prevent rate limiting
        stock = yf.Ticker(ticker)
        return stock.info.get("sector", "Unknown")
    except Exception as e:
        print(f"⚠️ Error fetching sector for {ticker}: {e}")
        return "Unknown"

# === Function to Get Asset Class Benchmark ===
def get_asset_class(ticker, sector):
    if sector in asset_class_benchmark:
        return sector, asset_class_benchmark[sector]

    # Manual classification for missing sectors
    if ticker in ["BTC", "ETH", "IBIT"]:
        return "Crypto", "BITO"
    elif ticker in ["BND", "AGG", "LQD"]:
        return "Bonds", "BND"
    elif ticker in ["GLD", "IAU"]:
        return "Gold", "GLD"
    elif ticker in ["VNQ", "IYR"]:
        return "Real Estate", "VNQ"
    elif ticker in ["IWM", "IJR"]:
        return "Small Cap Stocks", "IWM"
    elif ticker in ["ACWI", "VEU"]:
        return "International Stocks", "ACWI"
    else:
        return "US Stocks", "SPY"  # Default to S&P 500

# === Step 5: Analyze Portfolio & Save Data ===
data = [["Ticker", "Sector/Asset Class", "YTD Performance (%)", "Benchmark ETF", "Benchmark YTD Performance (%)", "Outperformance vs. Benchmark (%)"]]

for ticker in tickers:
    ytd_return = get_ytd_performance(ticker)
    sector = get_stock_sector(ticker)
    
    sector, benchmark_etf = get_asset_class(ticker, sector)
    benchmark_ytd_return = get_ytd_performance(benchmark_etf)

    outperformance = None
    if ytd_return is not None and benchmark_ytd_return is not None:
        outperformance = round(ytd_return - benchmark_ytd_return, 2)

    data.append([ticker, sector, ytd_return, benchmark_etf, benchmark_ytd_return, outperformance])

# === Step 6: Save Data as CSV for GitHub Upload ===
df_results = pd.DataFrame(data[1:], columns=data[0])  # Convert list to DataFrame
csv_filename = "portfolio_analysis_results.csv"
df_results.to_csv(csv_filename, index=False)

print(f"✅ Data saved as {csv_filename}. Now push it to GitHub!")
