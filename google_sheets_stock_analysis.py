import pandas as pd
import yfinance as yf
import datetime
import time

# === Step 1: Connect to Public Google Sheets ===
google_sheet_url = "https://docs.google.com/spreadsheets/d/1wxzhusybeXYntIjb0fyREViSu1-GcnOpUOG2yxkp7kQ/export?format=csv"
df = pd.read_csv(google_sheet_url)

tickers = df.iloc[:, 0].dropna().tolist()

# === Function to Fetch Stock Data ===
def get_stock_data(ticker):
    try:
        time.sleep(2)  # Prevent rate limiting
        stock = yf.Ticker(ticker)
        stock_info = stock.info

        # Extract company details
        company_name = stock_info.get("shortName", "N/A")
        sector = stock_info.get("sector", "N/A")
        industry = stock_info.get("industry", "Unknown")
        market_cap = stock_info.get("marketCap", "N/A")
        pe_ratio = stock_info.get("trailingPE", "N/A")
        eps = stock_info.get("trailingEps", "N/A")
        dividend_yield = stock_info.get("dividendYield", "N/A")
        fifty_two_week_high = stock_info.get("fiftyTwoWeekHigh", "N/A")
        fifty_two_week_low = stock_info.get("fiftyTwoWeekLow", "N/A")
        beta = stock_info.get("beta", "N/A")
        volume = stock_info.get("volume", "N/A")
        revenue_ttm = stock_info.get("totalRevenue", "N/A")
        net_income_ttm = stock_info.get("netIncomeToCommon", "N/A")
        debt_to_equity = stock_info.get("debtToEquity", "N/A")
        roa = stock_info.get("returnOnAssets", "N/A")
        roe = stock_info.get("returnOnEquity", "N/A")

        # Get historical performance
        hist = stock.history(period="5y")
        
        if hist.empty:
            ytd_return = one_year_return = five_year_return = "N/A"
        else:
            this_year = datetime.datetime.now().year
            hist["Year"] = hist.index.year
            
            hist_ytd = hist[hist["Year"] == this_year]
            first_price = hist_ytd["Close"].iloc[0] if not hist_ytd.empty else None
            current_price = hist["Close"].iloc[-1]
            
            ytd_return = ((current_price - first_price) / first_price) * 100 if first_price else "N/A"
            one_year_return = ((current_price - hist["Close"].iloc[-252]) / hist["Close"].iloc[-252]) * 100 if len(hist) > 252 else "N/A"
            five_year_return = ((current_price - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100 if len(hist) > 1250 else "N/A"

        # Get recent news
        news = stock.news if hasattr(stock, "news") else []
        latest_news = []
        if news:
            for n in news[:5]:
                title = n.get("title", "No Title Available")  # Handle missing title
                link = n.get("link", "No Link Available")    # Handle missing link
                latest_news.append((title, link))
        latest_news = latest_news if latest_news else "No Recent News"

        return {
            "Ticker": ticker,
            "Company Name": company_name,
            "Sector": sector,
            "Industry": industry,
            "Market Cap": market_cap,
            "PE Ratio": pe_ratio,
            "EPS": eps,
            "Dividend Yield": dividend_yield,
            "52W High": fifty_two_week_high,
            "52W Low": fifty_two_week_low,
            "Beta": beta,
            "YTD Performance (%)": round(ytd_return, 2) if isinstance(ytd_return, float) else ytd_return,
            "1Y Performance (%)": round(one_year_return, 2) if isinstance(one_year_return, float) else one_year_return,
            "5Y Performance (%)": round(five_year_return, 2) if isinstance(five_year_return, float) else five_year_return,
            "Volume": volume,
            "Revenue (TTM)": revenue_ttm,
            "Net Income (TTM)": net_income_ttm,
            "Debt-to-Equity Ratio": debt_to_equity,
            "ROA": roa,
            "ROE": roe,
            "Latest News": latest_news
        }

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return {
            "Ticker": ticker,
            "Company Name": "Error",
            "Sector": "Error",
            "Industry": "Error",
            "Market Cap": "Error",
            "PE Ratio": "Error",
            "EPS": "Error",
            "Dividend Yield": "Error",
            "52W High": "Error",
            "52W Low": "Error",
            "Beta": "Error",
            "YTD Performance (%)": "Error",
            "1Y Performance (%)": "Error",
            "5Y Performance (%)": "Error",
            "Volume": "Error",
            "Revenue (TTM)": "Error",
            "Net Income (TTM)": "Error",
            "Debt-to-Equity Ratio": "Error",
            "ROA": "Error",
            "ROE": "Error",
            "Latest News": "Error"
        }

# === Step 2: Fetch Data for All Tickers ===
data = []
for ticker in tickers:
    stock_data = get_stock_data(ticker)
    data.append(stock_data)

import os

# === Step 3: Save Data to CSV ===
df_results = pd.DataFrame(data)
csv_filename = "expanded_portfolio_analysis_results.csv"
df_results.to_csv(csv_filename, index=False)

print(f"✅ Data saved as {csv_filename}. Now pushing to GitHub...")

# Automate Git Commit & Push
os.system('git add expanded_portfolio_analysis_results.csv')
os.system('git commit -m "Auto-update portfolio analysis results"')
os.system('git push origin main')

print("🚀 Data successfully pushed to GitHub!")

