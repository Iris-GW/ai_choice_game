import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Set your OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_gpt35_response(prompt, model="gpt-3.5-turbo"):
    """
    Sends a prompt to OpenAI's GPT-3.5-turbo model and returns the response.
    
    Args:
        prompt (str): The text prompt to send to GPT-3.5-turbo.
        model (str): The model to use (default is 'gpt-3.5-turbo').

    Returns:
        str: The response text from the model.
    """
    try:
        print(f"Sending request to OpenAI with prompt: {prompt}")
        
        # Create a completion request with the OpenAI GPT-3.5 Turbo model
        response = openai.ChatCompletion.create(
            model=model,  # Model to be used (default: gpt-3.5-turbo)
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,  # Max token count for the response
            temperature=0.7  # Adjust to control creativity level
        )
        
        # Extract the generated text
        return response['choices'][0]['message']['content'].strip()

    except openai.error.InvalidRequestError as e:
        print(f"InvalidRequestError: {e}")
        return "An error occurred while processing your request."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "An unexpected error occurred."


if __name__ == "__main__":
    # Integration test: Sample prompt to ensure the API is working
    test_prompt = "Describe a mysterious forest with two paths."
    
    # Get response from the model
    response = get_gpt35_response(test_prompt)
    
    if response:
        print(f"Response: {response}")
    else:
        print("Failed to get a response from the model.")
