import os
import openai
import requests
import pandas as pd

# === Step 1: Load OpenAI API Key ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("⚠️ OpenAI API Key not found! Set it using 'setx OPENAI_API_KEY your_key' in CMD.")
    exit(1)

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# === Step 2: Fetch Stock Data from GitHub ===
print("✅ Fetching latest stock data from GitHub...")

GITHUB_CSV_URL = "https://raw.githubusercontent.com/sierreed/portfolio-performance-data/main/expanded_portfolio_analysis_results.csv"

try:
    response = requests.get(GITHUB_CSV_URL)
    response.raise_for_status()
    
    with open("latest_stock_data.csv", "wb") as file:
        file.write(response.content)

    print("✅ Successfully downloaded the latest stock data!")
except Exception as e:
    print(f"❌ Error fetching stock data: {e}")
    exit(1)

# === Step 3: Read CSV and Prepare GPT Input ===
df = pd.read_csv("latest_stock_data.csv")

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

# === Step 4: Send Data to GPT for Analysis ===
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

    print("✅ Analysis saved to 'gpt_stock_analysis.txt'.")
    print("✅ GPT now has the latest portfolio dataset.")

except Exception as e:
    print(f"❌ Error communicating with GPT: {e}")
