

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
    
    with open("expanded_portfolio_analysis_results.csv", "wb") as file:
        file.write(response.content)

    print("✅ Successfully downloaded the latest stock data!")
except Exception as e:
    print(f"❌ Error fetching stock data: {e}")
    exit(1)

# === Step 3: Read CSV and Prepare GPT Input ===
df = pd.read_csv("expanded_portfolio_analysis_results.csv")

# Convert full dataset to a string (limited to first 1000 rows for safety)
full_data_string = df.head(1000).to_string()

# Prepare prompt for GPT
prompt = f"""
You are a financial assistant. The user will ask questions about their stock portfolio. 

### Here is the full stock dataset: ###
{full_data_string}

### Additionally, analyze this dataset and provide key insights: ###
- Identify trends in stock performance.
- Highlight potential risks and concerns.
- Identify opportunities for growth.

Provide a structured, easy-to-read summary.
"""

# === Step 4: Send Full Data & Summary to GPT ===
print("🚀 Sending full dataset & analysis request to GPT...")

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
    print("✅ Full dataset has been sent to GPT for future queries.")

except Exception as e:
    print(f"❌ Error communicating with GPT: {e}")

# === Step 5: Commit & Push Data to GitHub ===
print("📤 Pushing updated data to GitHub...")

try:
    repo_path = r"C:\Users\14016\Documents"  # Ensure this is your correct repo location
    os.chdir(repo_path)  # Move to repo directory

    os.system("git add .")  # Add all changes
    os.system('git commit -m "Auto-update portfolio data and GPT analysis"')
    os.system("git push origin main")

    print("✅ Data successfully pushed to GitHub!")
except Exception as e:
    print(f"❌ Error pushing to GitHub: {e}")

