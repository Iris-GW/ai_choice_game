from flask import Flask, jsonify, request
import json
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the appropriate AI module based on configuration
use_deepseek = os.getenv("USE_DEEPSEEK", "false").lower() == "true"

print("Using DeepSeek API")
from deepseek_integration import get_deepseek_response as get_ai_response

app = Flask(__name__)

# Global variable to store story context for simplicity (you may want to improve this with session management)
story_context = ""

# Function to extract valid JSON from the response
def extract_json_from_response(response):
    try:
        # Match the JSON structure inside the response
        json_match = re.search(r"\{.*?\}", response, re.DOTALL)
        if json_match:
            json_content = json_match.group(0)
            return json.loads(json_content)  # Convert the string to JSON
        else:
            return None  # Return None if no JSON structure is found
    except json.JSONDecodeError:
        return None  # Handle JSON decode errors gracefully

# Route to start the game (resets story context)
@app.route('/start', methods=['GET'])
def start_game():
    global story_context
    story_context = ""  # Reset the story context when starting a new game

    prompt = """
    You are telling a short, interactive story. The player is standing at a crossroads. 
    Continue the story in **plain language only**, without any code, instructions, or examples. 
    Write exactly 3 sentences that describe what happens next. 
    After the story, provide exactly 4 choices for the player, labeled '1', '2', '3', and '4'. 
    Format the response in this exact JSON structure:
    {
      'story': 'story text here',
      'choices': ['choice 1', 'choice 2', 'choice 3', 'choice 4']
    }
    Do not include any programming code, technical instructions, or comments. Only return the plain JSON.
    """
    response = get_ai_response(prompt)
    story_data = extract_json_from_response(response)

    if story_data and "story" in story_data and "choices" in story_data:
        story_context = story_data['story']  # Initialize the story context
        return jsonify(story_data)
    else:
        return jsonify({
            "story": "There was an issue generating the initial story. Please try again.",
            "choices": ["1. Retry", "2. Exit", "3. Start a new story", "4. Try a different theme"]
        })

# Route to handle player choice
@app.route('/choice', methods=['POST'])
def player_choice():
    global story_context
    data = request.get_json()
    choice = data.get('choice')

    if choice not in [1, 2, 3, 4]:  # Updated to accept 4 choices
        return jsonify({"error": "Invalid choice"}), 400

    # Add the player's choice to the existing story context
    choice_text = f"The player chose option {choice}."

    # Build the prompt to continue the story
    prompt = f"""
    The story so far: "{story_context}"
    Based on the player's decision (option {choice}), continue the story in **plain language only**, 
    without any code, instructions, or examples.

    Write exactly 3 sentences that describe what happens next in the story. 
    After the story, provide exactly 4 new choices for the player in this JSON structure:
    {{
    "story": "story text here",
    "choices": ["choice 1", "choice 2", "choice 3", "choice 4"]
    }}

    Do not include any code, comments, or the phrase 'the player chose option X'. Only return the JSON.
    """

    # Get response from AI
    response = get_ai_response(prompt)
    story_data = extract_json_from_response(response)

    if story_data and "story" in story_data and "choices" in story_data:
        # Append the new part of the story to the existing context
        story_context += " " + story_data['story']
        return jsonify(story_data)
    else:
        return jsonify({
            "story": "There was an issue generating the next part of the story. Please try again.",
            "choices": ["1. Retry", "2. Go back", "3. Try a different path", "4. Exit game"]
        })

if __name__ == '__main__':
    app.run(debug=True)
