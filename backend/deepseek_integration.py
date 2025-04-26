import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

def get_deepseek_response(prompt):
    try:
        if not deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
            
        print(f"Sending request to DeepSeek API with prompt: {prompt}")
        
        headers = {
            "Authorization": f"Bearer {deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        # Using the correct model name for DeepSeek
        data = {
            "model": "deepseek-chat",  # Use the appropriate model name
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 250  # Increased token limit to accommodate 4 choices
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        print(f"DeepSeek API status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"Received response from DeepSeek: {content}")
            return content
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        print(f"Unexpected error with DeepSeek API: {e}")
        return f"An unexpected error occurred: {str(e)}"