import gspread
import pandas as pd
import yfinance as yf
import datetime

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

# === Function to Get YTD Performance (Fixed) ===
import time

# === Function to Get YTD Performance (Fixed) ===
def get_ytd_performance(ticker):
    try:
        time.sleep(2)  # Add delay to prevent rate limiting
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")  # Use "1y" to get data for the last year

        if hist.empty:
            print(f"Error fetching data for {ticker}: No data available")
            return None

        # Filter data to only include this year
        this_year = datetime.datetime.now().year
        hist = hist[hist.index.year == this_year]

        if hist.empty:
            print(f"Error: No data available for {ticker} in {this_year}")
            return None

        first_price = hist["Close"].iloc[0]  # First closing price of this year
        current_price = hist["Close"].iloc[-1]  # Latest closing price

        ytd_return = ((current_price - first_price) / first_price) * 100
        return round(ytd_return, 2)
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

# === Function to Get Stock Sector (With Delay) ===
def get_stock_sector(ticker):
    try:
        time.sleep(2)  # Add delay to prevent rate limiting
        stock = yf.Ticker(ticker)
        return stock.info.get("sector", "Unknown")
    except Exception as e:
        print(f"Error fetching sector for {ticker}: {e}")
        return "Unknown"

# === Function to Get Stock Sector ===
def get_stock_sector(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.info.get("sector", "Unknown")
    except Exception as e:
        print(f"Error fetching sector for {ticker}: {e}")
        return "Unknown"

# === Function to Get Asset Class Benchmark ===
def get_asset_class(ticker, sector):
    """Determine the best benchmark ETF based on sector or asset class."""
    if sector in asset_class_benchmark:
        return sector, asset_class_benchmark[sector]  # Use sector ETF if available

    # Manual classification for missing sectors
    crypto_tickers = ["BTC", "ETH", "IBIT"]
    bond_tickers = ["BND", "AGG", "LQD"]
    gold_tickers = ["GLD", "IAU"]
    reit_tickers = ["VNQ", "IYR"]
    small_cap_tickers = ["IWM", "IJR"]
    international_tickers = ["ACWI", "VEU"]

    if ticker in crypto_tickers:
        return "Crypto", "BITO"
    elif ticker in bond_tickers:
        return "Bonds", "BND"
    elif ticker in gold_tickers:
        return "Gold", "GLD"
    elif ticker in reit_tickers:
        return "Real Estate", "VNQ"
    elif ticker in small_cap_tickers:
        return "Small Cap Stocks", "IWM"
    elif ticker in international_tickers:
        return "International Stocks", "ACWI"
    else:
        return "US Stocks", "SPY"  # Default to S&P 500

# === Step 5: Analyze Portfolio & Save Data ===
data = [["Ticker", "Sector/Asset Class", "YTD Performance (%)", "Benchmark ETF", "Benchmark YTD Performance (%)", "Outperformance vs. Benchmark (%)"]]

for ticker in tickers:
    ytd_return = get_ytd_performance(ticker)
    sector = get_stock_sector(ticker)

    # Get the best available benchmark (sector ETF or asset class benchmark)
    sector, benchmark_etf = get_asset_class(ticker, sector)
    benchmark_ytd_return = get_ytd_performance(benchmark_etf)

    outperformance = None
    if ytd_return is not None and benchmark_ytd_return is not None:
        outperformance = round(ytd_return - benchmark_ytd_return, 2)

    data.append([ticker, sector, ytd_return, benchmark_etf, benchmark_ytd_return, outperformance])

import gspread # Keep only one import at the top



# === Step 6: Upload Data to Google Sheets (No Authentication Required) ===
import gspread

gc = gspread.Client(None)  # No API authentication needed
spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1wxzhusybeXYntIjb0fyREViSu1-GcnOpUOG2yxkp7kQ")
worksheet = spreadsheet.sheet1  # Get the first sheet

# Convert DataFrame to a list of lists and upload
worksheet.update("A1", [df_results.columns.tolist()] + df_results.values.tolist())

print("✅ Google Sheet updated successfully!")




