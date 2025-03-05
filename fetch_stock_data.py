
import os
import openai
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime
import subprocess

# === Step 1: Load OpenAI API Key ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("⚠️ OpenAI API Key not found! Set it using 'setx OPENAI_API_KEY your_key' in CMD.")
    exit(1)

# === Step 2: Load Tickers from Excel (Only Used for Initial List) ===
print("✅ Fetching stock tickers from Excel...")

excel_path = os.path.expanduser("~/Documents/stock_data.xlsx")
csv_path = os.path.expanduser("~/Documents/stock_data.csv")  # CSV Path

try:
    df_tickers = pd.read_excel(excel_path, sheet_name=0)
    tickers = df_tickers.iloc[:, 0].dropna().tolist()

    if not tickers:
        print("⚠️ No tickers found in Excel file!")
        exit(1)

    print(f"✅ Successfully loaded {len(tickers)} tickers from Excel!")

except Exception as e:
    print(f"❌ Error reading Excel file: {e}")
    exit(1)

# === Step 3: Fetch Stock Data from Yahoo Finance ===
print("✅ Fetching latest stock data from Yahoo Finance...")

try:
    stock_data = yf.Tickers(tickers)

    stock_list = []
    for ticker in tickers:
        stock = stock_data.tickers[ticker]
        info = stock.info

        # Attempt to fetch news headlines (alternative API needed)
        news = info.get("news", [])
        if news and isinstance(news, list):
            latest_news = news[0].get("title", "No Recent News")
            latest_news_link = news[0].get("link", "No Link Available")
        else:
            latest_news = "No Recent News"
            latest_news_link = "No Link Available"

        stock_list.append({
            "Ticker": ticker,
            "Company Name": info.get("shortName", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "Market Cap": info.get("marketCap", "N/A"),
            "PE Ratio": info.get("trailingPE", "N/A"),
            "EPS": info.get("trailingEps", "N/A"),
            "Dividend Yield": info.get("dividendYield", "N/A"),
            "52W High": info.get("fiftyTwoWeekHigh", "N/A"),
            "52W Low": info.get("fiftyTwoWeekLow", "N/A"),
            "Beta": info.get("beta", "N/A"),
            "YTD Performance (%)": info.get("52WeekChange", "N/A"),
            "1Y Performance (%)": info.get("52WeekChange", "N/A"),
            "5Y Performance (%)": info.get("fiveYearAverageReturn", "N/A"),
            "Volume": info.get("volume", "N/A"),
            "Revenue (TTM)": info.get("totalRevenue", "N/A"),
            "Net Income (TTM)": info.get("netIncomeToCommon", "N/A"),
            "Debt-to-Equity Ratio": info.get("debtToEquity", "N/A"),
            "ROA": info.get("returnOnAssets", "N/A"),
            "ROE": info.get("returnOnEquity", "N/A"),
            "Latest News": latest_news,
            "News Link": latest_news_link
        })

    df_stock_data = pd.DataFrame(stock_list)

    # **FORCE SAVE AS CSV (ONLY)**
    df_stock_data.to_csv(csv_path, index=False)
    
    # **OPTIONAL: Delete the old Excel file to avoid confusion**
    if os.path.exists(excel_path):
        os.remove(excel_path)  # Deletes the old Excel file so only CSV remains

    print(f"✅ Successfully updated stock data for {len(tickers)} stocks and saved as CSV: {csv_path}")

except Exception as e:
    print(f"❌ Error fetching stock data: {e}")
    exit(1)

# === Step 4: Push Updated CSV Data to GitHub (Ensuring Only CSV is Tracked) ===
print("🚀 Pushing latest stock data to GitHub...")

try:
    subprocess.run(["git", "add", csv_path], check=True)
    subprocess.run(["git", "commit", "-m", "Auto-update stock data (CSV format)"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ Successfully pushed latest stock data (CSV) to GitHub!")
except subprocess.CalledProcessError as e:
    print(f"❌ Error pushing to GitHub: {e}")
    exit(1)
