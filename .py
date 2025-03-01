import openai

# Confirm API key is accessible
print("API Key Loaded:", openai.api_key is not None)

# Test OpenAI API
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello, GPT!"}]
)

print(response)
