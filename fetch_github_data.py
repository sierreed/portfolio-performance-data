

import os
import openai
import requests
import pandas as pd
import subprocess

# === Step 1: Load OpenAI API Key ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("⚠️ OpenAI API Key not found! Set it using 'setx OPENAI_API_KEY your_key' in CMD.")
    exit(1)

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# === Step 2: Fetch Latest Stock Data from Yahoo Finance or Your Source ===
print("✅ Fetching latest stock data from Yahoo Finance...")

YAHOO_CSV_URL = "https://raw.githubusercontent.com/sierreed/portfolio-performance-data/main/expanded_portfolio_analysis_results.csv"

try:
    response = requests.get(YAHOO_CSV_URL)
    response.raise_for_status()
    
    with open("expanded_portfolio_analysis_results.csv", "wb") as file:
        file.write(response.content)

    print("✅ Successfully downloaded the latest stock data from Yahoo Finance!")
except Exception as e:
    print(f"❌ Error fetching stock data: {e}")
    exit(1)

# === Step 3: Push Updated Data to GitHub ===
print("🚀 Pushing latest stock data to GitHub...")

try:
    # Add only the CSV file
    subprocess.run(["git", "add", "expanded_portfolio_analysis_results.csv"], check=True)
    
    # Commit only if there are actual changes
    commit_status = subprocess.run(["git", "commit", "-m", "Auto-update portfolio data"], capture_output=True, text=True)
    if "nothing to commit" in commit_status.stdout.lower():
        print("✅ No changes in stock data. Skipping GitHub push.")
    else:
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Successfully pushed latest stock data to GitHub!")

except subprocess.CalledProcessError as e:
    print(f"❌ Error pushing to GitHub: {e}")
    exit(1)

# === Step 4: Read CSV and Prepare GPT Input ===
df = pd.read_csv("expanded_portfolio_analysis_results.csv")

# Convert dataset to a string (limited for safety)
full_data_string = df.to_string(index=False)

# Prepare prompt for GPT
prompt = f"""
You are a financial assistant. The user will ask questions about their stock portfolio.

### Here is the full stock dataset (Updated Daily): ###
{full_data_string}

### Analyze this dataset and provide key insights: ###
- Identify trends in stock performance.
- Highlight potential risks and concerns.
- Identify opportunities for growth.

Provide a structured, easy-to-read summary.
"""

# === Step 5: Send Data to GPT for Analysis ===
print("🚀 Sending latest dataset & analysis request to GPT...")

try:
    chat_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    
    analysis = chat_response.choices[0].message.content
    print("\n🔍 GPT Analysis:\n", analysis)

    # Save analysis to file
    with open("gpt_stock_analysis.txt", "w") as file:
        file.write(analysis)

    # Push GPT analysis to GitHub
    subprocess.run(["git", "add", "gpt_stock_analysis.txt"], check=True)
    
    # Commit only if there are actual changes
    commit_status = subprocess.run(["git", "commit", "-m", "Auto-update GPT stock analysis"], capture_output=True, text=True)
    if "nothing to commit" in commit_status.stdout.lower():
        print("✅ No changes in GPT analysis. Skipping GitHub push.")
    else:
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Analysis saved to 'gpt_stock_analysis.txt' and pushed to GitHub.")

except Exception as e:
    print(f"❌ Error communicating with GPT: {e}")
