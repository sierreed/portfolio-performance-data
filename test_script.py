import gspread
import pandas as pd
import yfinance as yf
import datetime
import time

# === Step 1: Connect to Public Google Sheets ===
google_sheet_url = "https://docs.google.com/spreadsheets/d/1wxzhusybeXYntIjb0fyREViSu1-GcnOpUOG2yxkp7kQ/export?format=csv"
df = pd.read_csv(google_sheet_url)  # Read Google Sheet as CSV
tickers = df.iloc[:, 0].dropna().tolist()  # Get tickers from first column

# === Function to Fetch Stock Data ===
def get_stock_data(ticker):
    try:
        time.sleep(2)  # Add delay to prevent rate limiting
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")  # 1-year historical data

        if hist.empty:
            return [ticker, None, None, None, None, None, None, None, None, None, "N/A", "N/A", "N/A"]

        # Year-to-Date (YTD) Performance
        this_year = datetime.datetime.now().year
        hist = hist[hist.index.year == this_year]
        first_price = hist["Close"].iloc[0] if not hist.empty else None
        current_price = hist["Close"].iloc[-1] if not hist.empty else None
        ytd_return = ((current_price - first_price) / first_price) * 100 if first_price else None
        
        # Other Data Points
        info = stock.info
        current_price = info.get("previousClose", None)
        pe_ratio = info.get("trailingPE", None)
        market_cap = info.get("marketCap", None)
        div_yield = info.get("dividendYield", None)  # Multiply by 100 for percentage
        beta = info.get("beta", None)
        high_52w = info.get("fiftyTwoWeekHigh", None)
        low_52w = info.get("fiftyTwoWeekLow", None)
        sector = info.get("sector", "Unknown")

        # Get News Headlines
        news = stock.news[:3] if "news" in stock.__dict__ else []
        news_headlines = [news[i]["title"] if i < len(news) else "N/A" for i in range(3)]

        return [ticker, sector, current_price, high_52w, low_52w, pe_ratio, market_cap, div_yield, beta, ytd_return] + news_headlines
    
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return [ticker, None, None, None, None, None, None, None, None, None, "N/A", "N/A", "N/A"]

# === Step 8: Fetch Data for All Tickers ===
data = [["Ticker", "Sector", "Current Price", "52W High", "52W Low", "P/E Ratio", "Market Cap", "Dividend Yield (%)", "Beta", "YTD Performance (%)", "News 1", "News 2", "News 3"]]

for ticker in tickers:
    data.append(get_stock_data(ticker))

# === Step 9: Upload Data to Google Sheets ===
gc = gspread.Client(None)  # No API authentication needed
spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1wxzhusybeXYntIjb0fyREViSu1-GcnOpUOG2yxkp7kQ")
worksheet = spreadsheet.sheet1  # Get the first sheet

# Upload data
worksheet.update("A1", data)

print("✅ Google Sheet updated successfully!")

